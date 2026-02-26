const mongoose = require('mongoose');
require('dotenv').config();

async function test() {
    await mongoose.connect(process.env.MONGODB_URI);
    const EnergyBucket = require('./backend/models/EnergyBucket');
    const targetAppliances = ['aircon', 'refrigerator', 'electricfan'];
    const dateStr = "2026-02-12";

    const hourlyAggregation = await EnergyBucket.aggregate([
        { $match: { date: dateStr, appliance_type: { $in: targetAppliances } } },
        { $unwind: "$readings" },
        {
            $addFields: {
                hour: { $hour: { date: "$readings.timestamp", timezone: "Asia/Manila" } }
            }
        },
        { $group: { _id: "$hour", actual_w: { $sum: "$readings.processed_data.power_w" } } },
        { $sort: { _id: 1 } },
        { $project: { _id: 0, hour_index: "$_id", actual_w: { $round: ["$actual_w", 2] } } }
    ]);

    console.log(`Aggregation length for ${dateStr}:`, hourlyAggregation.length);
    console.log(hourlyAggregation);

    process.exit(0);
}
test();
