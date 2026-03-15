const axios = require('axios');
const mongoose = require('mongoose');
const EnergyBucket = require('./backend/models/EnergyBucket');
require('dotenv').config({ path: './.env' }); // Adjusted path to ensure MONGO_URI is loaded

async function testPredict() {
    await mongoose.connect(process.env.MONGO_URI, { useNewUrlParser: true, useUnifiedTopology: true });
    
    const date = '2026-03-10';
    const targetAppliances = ['aircon', 'refrigerator', 'electricfan'];
    
    const historyDate = new Date(date);
    historyDate.setDate(historyDate.getDate() - 1);
    const historyDateStr = new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Manila' }).format(historyDate);
    
    console.log("History date is:", historyDateStr);

    const hourlyHistory = await EnergyBucket.aggregate([
        { $match: { date: historyDateStr, appliance_type: { $in: targetAppliances } } },
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
    
    console.log("Hourly history length:", hourlyHistory.length);

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

        const FASTAPI_URL = process.env.FASTAPI_URL || 'http://127.0.0.1:8000';
        try {
            console.log(`Calling FASTAPI for ${appliance}...`);
            const pyRes = await axios.post(`${FASTAPI_URL}/predict`, {
                appliance,
                history: h_kwh,
                watts: h_watts,
                temps: h_temp,
                hums: h_hum,
                horizon: 24
            });
            return { appliance, forecast: pyRes.data.forecast };
        } catch (e) {
            console.error(`Error for ${appliance}:`, e.message);
            return { appliance, forecast: Array(24).fill(null) };
        }
    });

    const predictions = await Promise.all(predictionPromises);
    console.log("Predictions:", JSON.stringify(predictions, null, 2));
    mongoose.disconnect();
}
testPredict();
