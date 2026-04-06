const EnergyBucket = require('../models/EnergyBucket');

exports.getMonthlySummary = async (req, res) => {
    try {
        const { date } = req.query; // Expects YYYY-MM

        // If no date provided in query, default to current month (Manila Time)
        let targetMonth = date;
        if (!targetMonth) {
            const now = new Date();
            const yearStr = now.toLocaleDateString('en-CA', { timeZone: 'Asia/Manila', year: 'numeric' });
            const monthStr = now.toLocaleDateString('en-CA', { timeZone: 'Asia/Manila', month: '2-digit' });
            targetMonth = `${yearStr}-${monthStr}`;
        }

        // Defensive validation to avoid malformed month filters.
        if (!/^\d{4}-(0[1-9]|1[0-2])$/.test(targetMonth)) {
            return res.status(400).json({ error: 'Invalid month format. Use YYYY-MM.' });
        }

        // Fast Regex Query to match 'YYYY-MM-DD' against 'YYYY-MM'
        // Example matches: ^2026-03
        const dateRegex = new RegExp(`^${targetMonth}`);

        // Aggregate from raw readings via:
        // reading -> hourly kWh -> daily kWh -> monthly kWh (per appliance).
        // reading_kwh assumes 10-minute sampling: power_w / 6000.
        const summaryByAppliance = await EnergyBucket.aggregate([
            { $match: { date: { $regex: dateRegex } } },
            { $unwind: "$readings" },
            {
                $project: {
                    normalized_appliance: {
                        $switch: {
                            branches: [
                                { case: { $eq: ["$appliance_type", "electric_fan"] }, then: "electricfan" },
                                { case: { $eq: ["$appliance_type", "electricfan"] }, then: "electricfan" },
                                { case: { $eq: ["$appliance_type", "air_conditioner"] }, then: "aircon" },
                                { case: { $eq: ["$appliance_type", "aircon"] }, then: "aircon" },
                                { case: { $eq: ["$appliance_type", "refrigerator"] }, then: "refrigerator" }
                            ],
                            default: "$appliance_type"
                        }
                    },
                    day_key: "$date",
                    hour_key: {
                        $dateToString: {
                            format: "%Y-%m-%d %H:00",
                            date: "$readings.timestamp",
                            timezone: "Asia/Manila"
                        }
                    },
                    reading_kwh: { $divide: [{ $ifNull: ["$readings.processed_data.power_w", 0] }, 6000] }
                }
            },
            {
                $group: {
                    _id: {
                        appliance: "$normalized_appliance",
                        day: "$day_key",
                        hour: "$hour_key"
                    },
                    hourly_kwh: { $sum: "$reading_kwh" }
                }
            },
            {
                $group: {
                    _id: {
                        appliance: "$_id.appliance",
                        day: "$_id.day"
                    },
                    daily_kwh: { $sum: "$hourly_kwh" }
                }
            },
            {
                $group: {
                    _id: "$_id.appliance",
                    total_kwh: { $sum: "$daily_kwh" }
                }
            }
        ], { allowDiskUse: true });

        // Fallback source for months/documents where readings are incomplete
        // but daily_summary.total_kwh already exists.
        const summaryByDaily = await EnergyBucket.aggregate([
            { $match: { date: { $regex: dateRegex } } },
            {
                $project: {
                    normalized_appliance: {
                        $switch: {
                            branches: [
                                { case: { $eq: ["$appliance_type", "electric_fan"] }, then: "electricfan" },
                                { case: { $eq: ["$appliance_type", "electricfan"] }, then: "electricfan" },
                                { case: { $eq: ["$appliance_type", "air_conditioner"] }, then: "aircon" },
                                { case: { $eq: ["$appliance_type", "aircon"] }, then: "aircon" },
                                { case: { $eq: ["$appliance_type", "refrigerator"] }, then: "refrigerator" }
                            ],
                            default: "$appliance_type"
                        }
                    },
                    daily_kwh: { $ifNull: ["$daily_summary.total_kwh", 0] }
                }
            },
            {
                $group: {
                    _id: "$normalized_appliance",
                    total_kwh: { $sum: "$daily_kwh" }
                }
            }
        ]);

        const appliance_totals_kwh = {
            aircon: 0,
            refrigerator: 0,
            electricfan: 0
        };

        summaryByAppliance.forEach((row) => {
            if (!row || !row._id) return;
            if (Object.prototype.hasOwnProperty.call(appliance_totals_kwh, row._id)) {
                appliance_totals_kwh[row._id] = Number(row.total_kwh || 0);
            }
        });

        const dailyFallbackMap = {};
        summaryByDaily.forEach((row) => {
            if (!row || !row._id) return;
            dailyFallbackMap[row._id] = Number(row.total_kwh || 0);
        });

        // If readings-based total is missing/zero, fallback to daily_summary totals.
        Object.keys(appliance_totals_kwh).forEach((key) => {
            if (appliance_totals_kwh[key] <= 0 && (dailyFallbackMap[key] || 0) > 0) {
                appliance_totals_kwh[key] = dailyFallbackMap[key];
            }
        });

        const totalRaw = appliance_totals_kwh.aircon + appliance_totals_kwh.refrigerator + appliance_totals_kwh.electricfan;
        const total_kwh = Number(totalRaw.toFixed(4));

        const rounded_appliance_totals_kwh = {
            aircon: Number(appliance_totals_kwh.aircon.toFixed(4)),
            refrigerator: Number(appliance_totals_kwh.refrigerator.toFixed(4)),
            electricfan: Number(appliance_totals_kwh.electricfan.toFixed(4))
        };

        res.status(200).json({
            month: targetMonth,
            total_kwh,
            appliance_totals_kwh: rounded_appliance_totals_kwh
        });

    } catch (error) {
        console.error("Monthly Summary Error:", error);
        res.status(500).json({ error: error.message });
    }
};
