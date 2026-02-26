const mongoose = require('mongoose');

const ReadingSchema = new mongoose.Schema({
    timestamp: { type: Date, required: true },
    processed_data: {
        power_w: { type: Number, required: true },
        total_kwh_accumulated: { type: Number, required: true },
    }
}, { _id: false });

const DailySummarySchema = new mongoose.Schema({
    total_kwh: { type: Number, required: true }
}, { _id: false });

const EnergyBucketSchema = new mongoose.Schema({
    date: { type: String, required: true, index: true },
    device_id: { type: String, required: true },
    appliance_type: {
        type: String,
        enum: ['aircon', 'refrigerator', 'electricfan'], // Audit fix: removed underscore
        required: true,
        index: true
    },
    readings: [ReadingSchema],
    daily_summary: DailySummarySchema
});

EnergyBucketSchema.index({ date: 1, appliance_type: 1 });

// Explicitly naming the collection to match Python's write target
module.exports = mongoose.model('EnergyBucket', EnergyBucketSchema, 'energybuckets');