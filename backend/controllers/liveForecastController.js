const EnergyBucket = require('../models/EnergyBucket');

function normalizeAppName(name) {
    if (name === 'electric_fan') return 'electricfan';
    return name;
}

function parseForecastHour(log) {
    // Preferred: "HH:00" stored for JS compatibility.
    if (typeof log.timestamp === 'string' && /^\d{2}:\d{2}$/.test(log.timestamp)) {
        return Number.parseInt(log.timestamp.slice(0, 2), 10);
    }

    // Fallback: datetime fields interpreted in Manila timezone.
    if (log.timestamp_dt) {
        const d = new Date(log.timestamp_dt);
        if (!Number.isNaN(d.getTime())) {
            const hh = new Intl.DateTimeFormat('en-US', {
                timeZone: 'Asia/Manila',
                hour: '2-digit',
                hour12: false
            }).format(d);
            return Number.parseInt(hh, 10);
        }
    }

    if (typeof log.timestamp === 'string') {
        const d = new Date(log.timestamp);
        if (!Number.isNaN(d.getTime())) {
            const hh = new Intl.DateTimeFormat('en-US', {
                timeZone: 'Asia/Manila',
                hour: '2-digit',
                hour12: false
            }).format(d);
            return Number.parseInt(hh, 10);
        }
    }

    return null;
}

function getGeneratedAtMs(log) {
    if (log && log.generated_at) {
        const t = new Date(log.generated_at).getTime();
        if (!Number.isNaN(t)) return t;
    }
    return 0;
}

exports.getLiveForecast = async (req, res) => {
    try {
        let horizon = parseInt(req.query.horizon, 10);
        const validHorizons = [1, 4, 8, 24];
        if (isNaN(horizon) || !validHorizons.includes(horizon)) horizon = 4;

        let granularity = parseInt(req.query.granularity, 10);
        const validGranularities = [10, 30, 60];
        if (isNaN(granularity) || !validGranularities.includes(granularity)) granularity = 60;

        // --- MANILA TIMEZONE HELPERS ---
        const now = new Date();
        const todayStr = new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Manila' }).format(now);
        const currentHour = parseInt(new Intl.DateTimeFormat('en-US', {
            timeZone: 'Asia/Manila', hour: 'numeric', hour12: false
        }).format(now), 10);
        const currentMinute = parseInt(new Intl.DateTimeFormat('en-US', {
            timeZone: 'Asia/Manila', minute: 'numeric'
        }).format(now), 10);

        const targetAppliances = ['aircon', 'refrigerator', 'electricfan'];

        // 1. Fetch Today's Actuals & Summaries
        const summaryDocs = await EnergyBucket.find(
            { date: todayStr, appliance_type: { $in: targetAppliances } },
            { 'daily_summary.total_kwh': 1, 'readings.processed_data': 1, _id: 0, appliance_type: 1 }
        );

        let applianceTotals = { aircon: 0, refrigerator: 0, electricfan: 0 };
        let aggregate_total_kwh = 0;

        summaryDocs.forEach(doc => {
            let kwh = 0;
            if (doc.daily_summary && doc.daily_summary.total_kwh) {
                kwh = doc.daily_summary.total_kwh;
            } else if (doc.readings && doc.readings.length > 0) {
                doc.readings.forEach(r => {
                    if (r.processed_data && r.processed_data.power_w) {
                        kwh += (r.processed_data.power_w / 6.0) / 1000.0;
                    }
                });
            }
            applianceTotals[doc.appliance_type] = Number(kwh.toFixed(4));
            aggregate_total_kwh += kwh;
        });

        // 2. Fetch hourly ML forecasts for today from Mongo.
        const db = require('mongoose').connection.db;
        const forecastCollection = db.collection('daily_forecasts');
        const todayLogsAll = await forecastCollection.find({ forecast_date: todayStr }).toArray();
        const normalizedLogs = todayLogsAll.map(log => ({
            ...log,
            appliance: normalizeAppName(log.appliance)
        }));

        // 3. Build per-appliance 24-hour vectors in true hour order.
        const predictionPromises = targetAppliances.map(async (appliance) => {
            const appLogs = normalizedLogs.filter(log => log.appliance === appliance);
            const hourly = Array(24).fill(null);
            const latestByHour = new Map();

            appLogs.forEach(log => {
                const hour = parseForecastHour(log);
                if (hour === null || hour < 0 || hour > 23) return;

                const prev = latestByHour.get(hour);
                if (!prev || getGeneratedAtMs(log) >= getGeneratedAtMs(prev)) {
                    latestByHour.set(hour, log);
                }
            });

            latestByHour.forEach((log, hour) => {
                const value = log.predicted_energy ?? log.predicted_kwh ?? null;
                hourly[hour] = typeof value === 'number' ? value : null;
            });

            return { appliance, forecast: hourly };
        });

        const predictions = await Promise.all(predictionPromises);
        let predictedHourly = Array(24).fill(0);
        let appliancePredictedHourly = {};
        predictions.forEach(p => {
            appliancePredictedHourly[p.appliance] = p.forecast;
            p.forecast.forEach((v, i) => { if (v !== null) predictedHourly[i] += v; });
        });

        // 4. Aggregate Today's Actuals for Chart
        const granularAggregation = await EnergyBucket.aggregate([
            { $match: { date: todayStr, appliance_type: { $in: targetAppliances } } },
            { $unwind: "$readings" },
            {
                $addFields: {
                    timeInMinutes: {
                        $add: [
                            { $multiply: [{ $hour: { date: "$readings.timestamp", timezone: "Asia/Manila" } }, 60] },
                            { $minute: { date: "$readings.timestamp", timezone: "Asia/Manila" } }
                        ]
                    }
                }
            },
            {
                $group: {
                    _id: {
                        bucket: { $floor: { $divide: ["$timeInMinutes", granularity] } },
                        appliance: "$appliance_type"
                    },
                    avg_w: { $avg: "$readings.processed_data.power_w" }
                }
            }
        ]);

        const bucketMap = {};
        granularAggregation.forEach(d => {
            if (!bucketMap[d._id.bucket]) bucketMap[d._id.bucket] = { total: 0, aircon: 0, refrigerator: 0, electricfan: 0 };
            const kw = d.avg_w / 1000.0;
            bucketMap[d._id.bucket][d._id.appliance] = Number(kw.toFixed(4));
            bucketMap[d._id.bucket].total += kw;
        });

        // 5. Construct Final Time-Series
        const currentBucket = Math.floor((currentHour * 60 + currentMinute) / granularity);
        const totalBuckets = Math.floor(1440 / granularity);

        const time_series = Array.from({ length: totalBuckets }, (_, i) => {
            const hour = Math.floor((i * granularity) / 60);
            const min = (i * granularity) % 60;
            const timeLabel = `${hour.toString().padStart(2, '0')}:${min.toString().padStart(2, '0')}`;
            const data = bucketMap[i] || { total: 0, aircon: 0, refrigerator: 0, electricfan: 0 };

            const payload = {
                timestamp: timeLabel,
                actual_kwh: i <= currentBucket ? Number((data.total * (granularity / 60)).toFixed(4)) : null,
                forecast_kwh: null,
                breakdown: {
                    aircon: { actual: null, forecast: null },
                    refrigerator: { actual: null, forecast: null },
                    electricfan: { actual: null, forecast: null }
                }
            };

            // 1. Populate Actuals
            if (i <= currentBucket) {
                targetAppliances.forEach(app => {
                    payload.breakdown[app].actual = Number((data[app] * (granularity / 60)).toFixed(4));
                });
            }

            // 2. Populate Forecasts for the ENTIRE day (past + future)
            // This allows the chart to overlay the full prediction line alongside actuals,
            // so users can compare what the model predicted vs what actually happened all day.
            const hourlyKw = predictedHourly[hour];

            if (hourlyKw !== null && hourlyKw !== undefined) {
                if (i < currentBucket) {
                    // Past hours: show what the model predicted for comparison with actuals
                    payload.forecast_kwh = Number((hourlyKw * (granularity / 60.0)).toFixed(4));
                    targetAppliances.forEach(app => {
                        const appHkw = appliancePredictedHourly[app][hour];
                        if (appHkw !== null && appHkw !== undefined) {
                            payload.breakdown[app].forecast = Number((appHkw * (granularity / 60.0)).toFixed(4));
                        }
                    });
                } else if (i === currentBucket) {
                    // Current bucket: bridge actual and forecast lines
                    payload.forecast_kwh = payload.actual_kwh;
                    targetAppliances.forEach(app => {
                        payload.breakdown[app].forecast = payload.breakdown[app].actual;
                    });
                } else {
                    // Future predictions
                    payload.forecast_kwh = Number((hourlyKw * (granularity / 60.0)).toFixed(4));
                    targetAppliances.forEach(app => {
                        const appHkw = appliancePredictedHourly[app][hour];
                        if (appHkw !== null && appHkw !== undefined) {
                            payload.breakdown[app].forecast = Number((appHkw * (granularity / 60.0)).toFixed(4));
                        }
                    });
                }
            }

            return payload;
        });

        res.status(200).json({
            date: todayStr,
            granularity,
            unit_trend: "kWh",
            unit_summary: "kWh",
            current_bucket_index: currentBucket,
            aggregate_total_kwh: Number(aggregate_total_kwh.toFixed(2)),
            appliance_totals_kwh: applianceTotals,
            data: time_series
        });
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: "Internal Server Error" });
    }
};
