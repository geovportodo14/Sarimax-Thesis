const EnergyBucket = require('../models/EnergyBucket');
const Forecast = require('../models/Forecast');

exports.getHistoricalData = async (req, res) => {
    try {
        const { date } = req.query; // Expects YYYY-MM-DD
        let granularity = parseInt(req.query.granularity, 10);
        const validGranularities = [10, 30, 60];
        if (isNaN(granularity) || !validGranularities.includes(granularity)) granularity = 60;

        // Note: MongoDB enum in energybuckets uses 'electricfan', 
        // but frontend or pipeline might use 'electric_fan'.
        const targetAppliances = ['aircon', 'refrigerator', 'electricfan'];
        const groupInterval = granularity;

        // 1. Fetch Actuals from energybuckets
        const currentAggregation = await EnergyBucket.aggregate([
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
                $group: {
                    _id: {
                        bucket: { $floor: { $divide: ["$timeInMinutes", groupInterval] } },
                        appliance: "$appliance_type"
                    },
                    avg_w: { $avg: "$readings.processed_data.power_w" }
                }
            }
        ]);

        // 2. Fetch Forecasts from daily_forecasts
        let forecasts = [];
        if (granularity === 60) {
            forecasts = await Forecast.find({ forecast_date: date });
        }

        const bucketMap = {};
        let aggregate_total_kwh = 0;
        let applianceTotals = { aircon: 0, refrigerator: 0, electricfan: 0 };

        // Process Actuals
        currentAggregation.forEach(d => {
            if (!bucketMap[d._id.bucket]) bucketMap[d._id.bucket] = { total: 0, aircon: 0, refrigerator: 0, electricfan: 0, forecast_total: 0 };
            const kw = d.avg_w / 1000.0;
            const kwh = kw * (granularity / 60.0);

            bucketMap[d._id.bucket][d._id.appliance] = Number(kwh.toFixed(4));
            bucketMap[d._id.bucket].total += kwh;

            applianceTotals[d._id.appliance] += kwh;
            aggregate_total_kwh += kwh;
        });

        // Process Forecasts (merge into bucketMap)
        forecasts.forEach(f => {
            const hour = parseInt(f.timestamp.split(':')[0], 10);
            const bucket = Math.floor((hour * 60) / granularity);
            if (!bucketMap[bucket]) {
                bucketMap[bucket] = { total: 0, aircon: 0, refrigerator: 0, electricfan: 0, forecast_total: 0, forecasts: {} };
            }
            if (!bucketMap[bucket].forecasts) bucketMap[bucket].forecasts = {};

            // Map 'electric_fan' (forecast db) to 'electricfan' (response schema)
            const appKey = f.appliance === 'electric_fan' ? 'electricfan' : f.appliance;
            bucketMap[bucket].forecasts[appKey] = f.predicted_kwh;
            bucketMap[bucket].forecast_total += f.predicted_kwh;
        });

        // 3. Build Time-Series
        const totalBuckets = Math.floor(1440 / granularity);
        const time_series = Array.from({ length: totalBuckets }, (_, i) => {
            const hour = Math.floor((i * granularity) / 60);
            const min = (i * granularity) % 60;
            const timeLabel = `${hour.toString().padStart(2, '0')}:${min.toString().padStart(2, '0')}`;
            const data = bucketMap[i] || { total: 0, aircon: 0, refrigerator: 0, electricfan: 0, forecast_total: 0, forecasts: {} };

            const payload = {
                timestamp: timeLabel,
                actual_kwh: data.total > 0 ? Number(data.total.toFixed(4)) : null,
                forecast_kwh: data.forecast_total > 0 ? Number(data.forecast_total.toFixed(4)) : null,
                breakdown: {
                    aircon: { actual: null, forecast: null },
                    refrigerator: { actual: null, forecast: null },
                    electricfan: { actual: null, forecast: null }
                }
            };

            // Populate Actuals
            targetAppliances.forEach(app => {
                if (data[app] > 0) payload.breakdown[app].actual = Number(data[app].toFixed(4));
                if (data.forecasts && data.forecasts[app] > 0) payload.breakdown[app].forecast = Number(data.forecasts[app].toFixed(4));
            });

            return payload;
        });

        res.status(200).json({
            date,
            granularity,
            aggregate_total_kwh: Number(aggregate_total_kwh.toFixed(2)),
            appliance_totals_kwh: applianceTotals,
            data: time_series
        });
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: error.message });
    }
};
