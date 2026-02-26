const mongoose = require('mongoose');
require('dotenv').config();

async function test() {
    await mongoose.connect(process.env.MONGODB_URI);
    const EnergyBucket = require('./backend/models/EnergyBucket');
    const targetAppliances = ['aircon', 'refrigerator', 'electricfan'];
    const dateStr = "2026-02-12";

    const summaryDocs = await EnergyBucket.find(
        { date: dateStr, appliance_type: { $in: targetAppliances } },
        { 'daily_summary.total_kwh': 1, 'readings.processed_data': 1, _id: 0 }
    );

    console.log(`Docs found for ${dateStr}:`, summaryDocs.length);
    if (summaryDocs.length > 0) {
        console.log("First doc summary:", JSON.stringify(summaryDocs[0].daily_summary));
    }

    const hourlyAggregation = await EnergyBucket.aggregate([
        { $match: { date: dateStr, appliance_type: { $in: targetAppliances } } },
        { $unwind: "$readings" },
        {
            $addFields: {
                hour: { $hour: { date: "$readings.timestamp", timezone: "Asia/Manila" } }
            }
        },
        { $group: { _id: "$hour", actual_w: { $sum: "$readings.processed_data.power_w" } } }
    ]);

    console.log("Aggregation output length:", hourlyAggregation.length);
    if (hourlyAggregation.length > 0) {
        console.log("Sample hour aggregation:", hourlyAggregation[0]);
    }

    process.exit(0);
}
test();
