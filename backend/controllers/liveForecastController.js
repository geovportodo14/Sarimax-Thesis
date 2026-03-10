const EnergyBucket = require('../models/EnergyBucket');
const axios = require('axios');

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

        // 2. Fetch History for Forecasting (from Yesterday)
        const yesterday = new Date(now);
        yesterday.setDate(yesterday.getDate() - 1);
        const yesterdayStr = new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Manila' }).format(yesterday);

        const hourlyHistory = await EnergyBucket.aggregate([
            { $match: { date: yesterdayStr, appliance_type: { $in: targetAppliances } } },
            { $unwind: "$readings" },
            {
                $group: {
                    _id: {
                        hour: { $hour: { date: "$readings.timestamp", timezone: "Asia/Manila" } },
                        appliance: "$appliance_type"
                    },
                    total_w: { $sum: "$readings.processed_data.power_w" },
                    avg_temp: { $avg: "$readings.weather.temp" },
                    avg_humidity: { $avg: "$readings.weather.humidity" },
                    count: { $sum: 1 }
                }
            },
            { $sort: { "_id.hour": 1 } }
        ]);

        // 3. Request Baseline Forecast (from start of today)
        const predictionPromises = targetAppliances.map(async (appliance) => {
            const h_kwh = Array.from({ length: 24 }, (_, i) => {
                const match = hourlyHistory.find(d => d._id.hour === i && d._id.appliance === appliance);
                return match ? Number(((match.total_w / 6.0) / 1000.0).toFixed(6)) : 0.25;
            });
            const h_watts = Array.from({ length: 24 }, (_, i) => {
                const match = hourlyHistory.find(d => d._id.hour === i && d._id.appliance === appliance);
                return match ? Number((match.total_w / match.count).toFixed(2)) : 250.0;
            });
            const h_temp = Array.from({ length: 24 }, (_, i) => {
                const match = hourlyHistory.find(d => d._id.hour === i && d._id.appliance === appliance);
                return match ? (match.avg_temp || 30.0) : 30.0;
            });
            const h_hum = Array.from({ length: 24 }, (_, i) => {
                const match = hourlyHistory.find(d => d._id.hour === i && d._id.appliance === appliance);
                return match ? (match.avg_humidity || 70.0) : 70.0;
            });

            try {
                const pyRes = await axios.post('http://127.0.0.1:8000/predict', {
                    appliance,
                    history: h_kwh,
                    watts: h_watts,
                    temps: h_temp,
                    hums: h_hum,
                    horizon: 24
                });
                return { appliance, forecast: pyRes.data.forecast };
            } catch (e) {
                return { appliance, forecast: Array(24).fill(null) };
            }
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

            // 2. Populate Forecasts (full-day baseline + dynamic updates)
            const hourlyKw = predictedHourly[hour];
            if (hourlyKw !== null) {
                payload.forecast_kwh = Number((hourlyKw * (granularity / 60.0)).toFixed(4));
                targetAppliances.forEach(app => {
                    const appHkw = appliancePredictedHourly[app][hour];
                    if (appHkw !== null) {
                        payload.breakdown[app].forecast = Number((appHkw * (granularity / 60.0)).toFixed(4));
                    }
                });
            }

            return payload;
        }).filter(p => p.actual_kwh !== null || p.forecast_kwh !== null);

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