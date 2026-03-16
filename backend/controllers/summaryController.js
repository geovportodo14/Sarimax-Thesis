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

        // Fast Regex Query to match 'YYYY-MM-DD' against 'YYYY-MM'
        // Example matches: ^2026-03
        const dateRegex = new RegExp(`^${targetMonth}`);

        // Aggregate actual usage (sum of all devices' daily_summary.total_kwh for this month)
        const summary = await EnergyBucket.aggregate([
            { $match: { date: { $regex: dateRegex } } },
            {
                $group: {
                    _id: null,
                    total_kwh: { $sum: "$daily_summary.total_kwh" }
                }
            }
        ]);

        const total_kwh = summary.length > 0 ? Number(summary[0].total_kwh.toFixed(2)) : 0;

        res.status(200).json({
            month: targetMonth,
            total_kwh: total_kwh
        });

    } catch (error) {
        console.error("Monthly Summary Error:", error);
        res.status(500).json({ error: error.message });
    }
};
