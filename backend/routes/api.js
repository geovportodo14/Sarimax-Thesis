const express = require('express');
const router = express.Router();
const historicalController = require('../controllers/historicalController');
const liveForecastController = require('../controllers/liveForecastController');
const summaryController = require('../controllers/summaryController');
const dailyForecastsController = require('../controllers/dailyForecastsController');
const axios = require('axios');

// Proxy for Alerts (FastAPI on Port 8000)
// The dashboard context calls these at /api/alerts/...
const FASTAPI_URL = process.env.FASTAPI_URL || 'http://127.0.0.1:8000';

router.post('/alerts/:type', async (req, res) => {
    try {
        const { type } = req.params;
        const response = await axios.post(`${FASTAPI_URL}/api/alerts/${type}`, req.body);
        res.status(response.status).json(response.data);
    } catch (error) {
        console.error(`Alert Proxy Error (${req.params.type}):`, error.message);
        res.status(error.response?.status || 500).json({
            status: 'error',
            message: error.response?.data?.detail || 'Failed to proxy alert to FastAPI'
        });
    }
});

// Define Phase 2 Routes
router.get('/historical', historicalController.getHistoricalData);
router.get('/live', liveForecastController.getLiveForecast);
router.get('/summary/month', summaryController.getMonthlySummary);
router.get('/forecast/daily', dailyForecastsController.getDailyForecasts);
router.get('/schedule/dates', dailyForecastsController.getScheduleDates);

module.exports = router;
