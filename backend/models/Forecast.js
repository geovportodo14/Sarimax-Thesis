const mongoose = require('mongoose');

/**
 * Schema for SARIMAX forecasts.
 * Collection: daily_forecasts
 */
const ForecastSchema = new mongoose.Schema({
    appliance: {
        type: String,
        required: true,
        enum: ['aircon', 'refrigerator', 'electric_fan'], // Matches Python pipeline keys
        index: true
    },
    forecast_date: { type: String, required: true, index: true }, // YYYY-MM-DD
    timestamp: { type: String, required: true }, // HH:00
    predicted_kwh: { type: Number, required: true },
    cost_php: { type: Number, required: true },
    generated_at: { type: Date, default: Date.now }
});

// Compound index for quick lookups in the history controller
ForecastSchema.index({ forecast_date: 1, appliance: 1, timestamp: 1 });

module.exports = mongoose.model('Forecast', ForecastSchema, 'daily_forecasts');
