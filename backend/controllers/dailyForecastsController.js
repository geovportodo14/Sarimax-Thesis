const mongoose = require('mongoose');
const fs = require('fs/promises');
const path = require('path');

const OUTPUTS_ROOT = path.join(__dirname, '..', 'forecasting', 'outputs');

function getManilaDateString(date = new Date()) {
    return new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Manila' }).format(date);
}

function normalizeApplianceName(name) {
    if (name === 'electricfan') return 'electric_fan';
    return name;
}

function toSortHour(log) {
    if (typeof log.timestamp === 'string' && /^\d{2}:\d{2}$/.test(log.timestamp)) {
        return Number.parseInt(log.timestamp.slice(0, 2), 10);
    }
    if (log.timestamp_dt) {
        const d = new Date(log.timestamp_dt);
        if (!Number.isNaN(d.getTime())) {
            const hh = new Intl.DateTimeFormat('en-US', {
                timeZone: 'Asia/Manila',
                hour: '2-digit',
                hour12: false
            }).format(d);
            return Number.parseInt(hh, 10);
        }
    }
    if (typeof log.timestamp === 'string') {
        const d = new Date(log.timestamp);
        if (!Number.isNaN(d.getTime())) {
            const hh = new Intl.DateTimeFormat('en-US', {
                timeZone: 'Asia/Manila',
                hour: '2-digit',
                hour12: false
            }).format(d);
            return Number.parseInt(hh, 10);
        }
    }
    return 99;
}

function asIsoTimestamp(log) {
    if (typeof log.timestamp === 'string' && /^\d{2}:\d{2}$/.test(log.timestamp) && log.forecast_date) {
        return `${log.forecast_date}T${log.timestamp}:00+08:00`;
    }
    if (log.timestamp_dt) {
        const d = new Date(log.timestamp_dt);
        if (!Number.isNaN(d.getTime())) return d.toISOString();
    }
    return log.timestamp;
}

function getGeneratedAtMs(log) {
    if (log && log.generated_at) {
        const t = new Date(log.generated_at).getTime();
        if (!Number.isNaN(t)) return t;
    }
    return 0;
}

async function loadScheduleForDate(forecastDate) {
    const filePath = path.join(OUTPUTS_ROOT, forecastDate, '_schedule.json');
    try {
        const raw = await fs.readFile(filePath, 'utf-8');
        return JSON.parse(raw);
    } catch {
        return null;
    }
}

// Helper to fetch and format the next 24-hr forecast stored by the Python pipeline
exports.getDailyForecasts = async (req, res) => {
    try {
        const { date } = req.query; // optional specific date

        // MongoDB stores records in the 'daily_forecasts' collection dynamically created by Python.
        // If it doesn't exist implicitly, mongoose.connection.db.collection gives direct access.
        const db = mongoose.connection.db;
        const collection = db.collection('daily_forecasts');

        let query = {};
        if (date) {
            query.forecast_date = date; // 'YYYY-MM-DD'
        } else {
            // Get tomorrow's date by default
            const tomorrow = new Date();
            tomorrow.setDate(tomorrow.getDate() + 1);
            query.forecast_date = getManilaDateString(tomorrow);
        }

        const rawLogs = await collection.find(query).toArray();
        const schedule = await loadScheduleForDate(query.forecast_date);

        if (!rawLogs || rawLogs.length === 0) {
            return res.status(200).json({
                status: 'no_data',
                forecast_date: query.forecast_date,
                appliances: [],
                schedule,
                optimization_summary: schedule?.optimization_summary ?? null
            });
        }

        // Deduplicate by appliance+hour and keep the latest generated row.
        const latestByKey = new Map();
        rawLogs.forEach(log => {
            const normApp = normalizeApplianceName(log.appliance);
            const hour = toSortHour(log);
            const key = `${normApp}|${hour}`;
            const existing = latestByKey.get(key);
            const row = { ...log, appliance: normApp };
            if (!existing || getGeneratedAtMs(row) >= getGeneratedAtMs(existing)) {
                latestByKey.set(key, row);
            }
        });
        const hourlyLogs = Array.from(latestByKey.values());
        hourlyLogs.sort((a, b) => {
            if (a.appliance !== b.appliance) return a.appliance.localeCompare(b.appliance);
            return toSortHour(a) - toSortHour(b);
        });

        // Group the hourly logs by appliance
        const grouped = hourlyLogs.reduce((acc, log) => {
            if (!acc[log.appliance]) {
                acc[log.appliance] = {
                    appliance: log.appliance,
                    forecast_date: log.forecast_date,
                    total_predicted_kwh: 0,
                    total_predicted_cost_php: 0,
                    hourly_forecast: []
                };
            }

            acc[log.appliance].total_predicted_kwh += (log.predicted_energy ?? log.predicted_kwh ?? 0);
            acc[log.appliance].total_predicted_cost_php += (log.predicted_cost ?? log.cost_php ?? 0);
            acc[log.appliance].hourly_forecast.push({
                timestamp: asIsoTimestamp(log),
                predicted_kwh: (log.predicted_energy ?? log.predicted_kwh ?? 0)
            });

            return acc;
        }, {});

        const formattedData = Object.values(grouped);

        res.status(200).json({
            status: 'success',
            forecast_date: query.forecast_date,
            appliances: formattedData,
            schedule,
            optimization_summary: schedule?.optimization_summary ?? null
        });

    } catch (error) {
        console.error("Error fetching daily forecasts:", error);
        res.status(500).json({ status: 'error', error: error.message });
    }
};
