const fs = require('fs');
const scheduleData = require('./backend/forecasting/outputs/2026-03-20/_schedule.json');

const scheduleAppliances = Array.isArray(scheduleData?.appliances) ? scheduleData.appliances : [];
const byHour = Array.from({ length: 24 }, (_, hour) => ({
    hour,
    baseline: 0,
    optimized: 0
}));

scheduleAppliances.forEach((app) => {
    (app.hourly || []).forEach((row) => {
        const hour = Number(row.hour ?? -1);
        if (hour >= 0 && hour <= 23) {
            byHour[hour].baseline += Number(row.baseline_kwh || 0);
            byHour[hour].optimized += Number(row.optimized_kwh || 0);
        }
    });
});

const maxKwh = Math.max(...byHour.map(h => Math.max(h.baseline, h.optimized)), 0.001);
const profile = byHour.map(h => ({
    hour: h.hour,
    baselinePct: (h.baseline / maxKwh) * 100,
    optimizedPct: (h.optimized / maxKwh) * 100
}));

console.log("Profile length:", profile.length);
console.log("First element:", profile[0]);
