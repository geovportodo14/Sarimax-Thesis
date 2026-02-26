const EnergyBucket = require('../models/EnergyBucket');
const axios = require('axios');

exports.getHistoricalData = async (req, res) => {
    try {
        const { date } = req.query; // Expects YYYY-MM-DD
        let granularity = parseInt(req.query.granularity, 10);
        const validGranularities = [10, 30, 60];
        if (isNaN(granularity) || !validGranularities.includes(granularity)) granularity = 60;

        const targetAppliances = ['aircon', 'refrigerator', 'electricfan'];

        // 1. Calculate Daily Aggregate Total (Real kWh) - For Summary Cards
        const summaryDocs = await EnergyBucket.find(
            { date: date, appliance_type: { $in: targetAppliances } },
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

        // 2. Multi-Granularity Aggregation (kW Demand) - For Trendlines
        const groupInterval = granularity;

        const granularAggregation = await EnergyBucket.aggregate([
            { $match: { date: date, appliance_type: { $in: targetAppliances } } },
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
                $project: {
                    appliance_type: 1,
                    power_w: "$readings.processed_data.power_w",
                    bucketIndex: { $floor: { $divide: ["$timeInMinutes", groupInterval] } }
                }
            },
            {
                $group: {
                    _id: { bucket: "$bucketIndex", appliance: "$appliance_type" },
                    avg_w: { $avg: "$power_w" }
                }
            },
            {
                $project: {
                    _id: 0,
                    bucket: "$_id.bucket",
                    appliance: "$_id.appliance",
                    kw: { $divide: ["$avg_w", 1000.0] } // Convert to kW Demand
                }
            },
            { $sort: { bucket: 1 } }
        ]);

        // Pivot aggregation results
        const bucketMap = {};
        granularAggregation.forEach(d => {
            if (!bucketMap[d.bucket]) bucketMap[d.bucket] = { total: 0, aircon: 0, refrigerator: 0, electricfan: 0 };
            const kwVal = d.kw || 0;
            bucketMap[d.bucket][d.appliance] = Number(kwVal.toFixed(4));
            bucketMap[d.bucket].total += kwVal;
        });

        // 3. RETROACTIVE SARIMAX BACKTESTING (Hourly in kW)
        let predictedHourly = [];
        try {
            const hourlyAggregation = await EnergyBucket.aggregate([
                { $match: { date: date, appliance_type: { $in: targetAppliances } } },
                { $unwind: "$readings" },
                {
                    $group: {
                        _id: { $hour: { date: "$readings.timestamp", timezone: "Asia/Manila" } },
                        total_w: { $sum: "$readings.processed_data.power_w" }
                    }
                },
                { $sort: { _id: 1 } }
            ]);

            const baseActual = hourlyAggregation.length > 0 ? hourlyAggregation[0].total_w : 250.0;
            const pyRes = await axios.post('http://127.0.0.1:8000/predict', {
                history: [baseActual],
                horizon: 24
            });
            predictedHourly = pyRes.data.forecast.map(w => w / 1000.0); // Convert forecast to kW
        } catch (e) {
            predictedHourly = Array(24).fill(null);
        }

        // 4. Construct Final Time-Series (kW Trend)
        const totalBuckets = Math.floor(1440 / groupInterval);
        const time_series = Array.from({ length: totalBuckets }, (_, i) => {
            const hour = Math.floor((i * groupInterval) / 60);
            const min = (i * groupInterval) % 60;
            const timeLabel = `${hour.toString().padStart(2, '0')}:${min.toString().padStart(2, '0')}`;

            const data = bucketMap[i] || { total: 0, aircon: 0, refrigerator: 0, electricfan: 0 };
            const payload = {
                timestamp: timeLabel,
                actual_kwh: Number((data.total * (granularity / 60)).toFixed(4)),
                forecast_kwh: null,
                breakdown: {
                    aircon: Number((data.aircon * (granularity / 60)).toFixed(4)),
                    refrigerator: Number((data.refrigerator * (granularity / 60)).toFixed(4)),
                    electricfan: Number((data.electricfan * (granularity / 60)).toFixed(4))
                }
            };

            // Map hourly forecast into buckets
            const hourOffset = hour;
            if (hourOffset < predictedHourly.length) {
                const hourlyKw = predictedHourly[hourOffset];
                if (hourlyKw !== null) {
                    const bucketKwh = hourlyKw * (granularity / 60.0);
                    payload.forecast_kwh = Number(bucketKwh.toFixed(4));
                }
            }

            return payload;
        });

        res.status(200).json({
            date,
            granularity,
            unit_trend: "kWh",
            unit_summary: "kWh",
            aggregate_total_kwh: Number(aggregate_total_kwh.toFixed(2)),
            appliance_totals_kwh: applianceTotals,
            data: time_series
        });
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: "Internal Server Error" });
    }
};