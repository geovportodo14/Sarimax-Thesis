export const APPLIANCES = ['Electric Fan', 'Air Conditioner', 'Refrigerator'];

export function generateApplianceForecast(points, dummyData = null) {
    let fan = [], ac = [], ref = [];

    if (dummyData && dummyData.applianceRanges) {
        const ranges = dummyData.applianceRanges;
        for (let i = 0; i < points; i++) {
            fan.push(ranges['Electric Fan']?.min + Math.random() * (ranges['Electric Fan']?.max - ranges['Electric Fan']?.min) || 0.05 + Math.random() * 0.1);
            ac.push(ranges['Air Conditioner']?.min + Math.random() * (ranges['Air Conditioner']?.max - ranges['Air Conditioner']?.min) || 2.2 + Math.random() * 0.6);
            ref.push(ranges['Refrigerator']?.min + Math.random() * (ranges['Refrigerator']?.max - ranges['Refrigerator']?.min) || 1.1 + Math.random() * 0.3);
        }
    } else {
        for (let i = 0; i < points; i++) {
            fan.push(0.05 + Math.random() * 0.1);  // Electric Fan: ~50-150W
            ac.push(2.2 + Math.random() * 0.6);     // Air Conditioner: ~2.2-2.8 kWh
            ref.push(1.1 + Math.random() * 0.3);    // Refrigerator: ~1.1-1.4 kWh
        }
    }
    return { fan, ac, ref };
}

export function formatHour(date, offsetHours) {
    const d = new Date(date);
    d.setHours(d.getHours() + offsetHours);

    const mm = String(d.getMonth() + 1).padStart(2, '0');
    const dd = String(d.getDate()).padStart(2, '0');
    const yy = String(d.getFullYear()).slice(-2);
    const hh = String(d.getHours()).padStart(2, '0');
    const mi = String(d.getMinutes()).padStart(2, '0');

    return `${mm}/${dd}/${yy} ${hh}:${mi}`;
}

export function generateLabels(baseDate, forecastHours, lookbackHours) {
    const now = new Date(baseDate);
    const prevPoints = Math.max(1, lookbackHours);
    const nextPoints = Math.max(1, forecastHours);

    let prevLabels = [], nextLabels = [];
    for (let i = prevPoints; i > 0; i--) prevLabels.push(formatHour(now, -i));
    for (let i = 0; i < nextPoints; i++) nextLabels.push(formatHour(now, i));

    return { prevLabels, nextLabels, prevPoints, nextPoints };
}

export function generateActual(points, dummyData = null, periodKey = null) {
    if (dummyData && dummyData.sampleData && periodKey && dummyData.sampleData[periodKey]) {
        const sample = dummyData.sampleData[periodKey].lookback.actual;
        if (sample.length >= points) {
            return sample.slice(0, points);
        } else {
            const baseValue = dummyData.actualBaseValue || 4.2;
            const increment = dummyData.actualIncrement || 0.15;
            const randomRange = dummyData.actualRandomRange || 0.8;
            return [...sample, ...Array(points - sample.length).fill().map((_, i) =>
                baseValue + (sample.length + i) * increment + Math.random() * randomRange
            )];
        }
    }
    const baseValue = dummyData?.actualBaseValue || 4.2;
    const increment = dummyData?.actualIncrement || 0.15;
    const randomRange = dummyData?.actualRandomRange || 0.8;
    return Array(points).fill().map((_, i) => baseValue + i * increment + Math.random() * randomRange);
}

export function generateForecastPast(points, dummyData = null, periodKey = null) {
    if (dummyData && dummyData.sampleData && periodKey && dummyData.sampleData[periodKey]) {
        const sample = dummyData.sampleData[periodKey].lookback.forecast;
        if (sample.length >= points) {
            return sample.slice(0, points);
        } else {
            const baseValue = dummyData.forecastBaseValue || 4.1;
            const increment = dummyData.forecastIncrement || 0.15;
            const randomRange = dummyData.forecastRandomRange || 0.9;
            return [...sample, ...Array(points - sample.length).fill().map((_, i) =>
                baseValue + (sample.length + i) * increment + Math.random() * randomRange
            )];
        }
    }
    const baseValue = dummyData?.forecastBaseValue || 4.1;
    const increment = dummyData?.forecastIncrement || 0.15;
    const randomRange = dummyData?.forecastRandomRange || 0.9;
    return Array(points).fill().map((_, i) => baseValue + i * increment + Math.random() * randomRange);
}
