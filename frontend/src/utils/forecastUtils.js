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

export function generateApplianceForecast(points, dummyData = null) {
    let ac = [], ref = [], wm = [], ef = [];

    if (dummyData && dummyData.applianceRanges) {
        const ranges = dummyData.applianceRanges;
        for (let i = 0; i < points; i++) {
            ac.push(ranges['Air Conditioner'].min + Math.random() * (ranges['Air Conditioner'].max - ranges['Air Conditioner'].min));
            ref.push(ranges['Refrigerator'].min + Math.random() * (ranges['Refrigerator'].max - ranges['Refrigerator'].min));
            wm.push(ranges['Washing Machine'].min + Math.random() * (ranges['Washing Machine'].max - ranges['Washing Machine'].min));
            // Electric Fan (not in dummy ranges usually, so hardcode sensible defaults)
            ef.push(0.15 + Math.random() * 0.1);
        }
    } else {
        // Fallback to original generation
        for (let i = 0; i < points; i++) {
            ac.push(2.2 + Math.random() * 0.6);
            ref.push(1.1 + Math.random() * 0.3);
            wm.push(0.7 + Math.random() * 0.2);
            ef.push(0.15 + Math.random() * 0.1);
        }
    }
    return { ac, ref, wm, ef };
}

export function generateLabels(forecastHours, lookbackHours) {
    const now = new Date();

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
        // Use sample data if available, pad or trim to match points needed
        if (sample.length >= points) {
            return sample.slice(0, points);
        } else {
            // Use sample as base, generate additional points
            const baseValue = dummyData.actualBaseValue || 4.2;
            const increment = dummyData.actualIncrement || 0.15;
            const randomRange = dummyData.actualRandomRange || 0.8;
            return [...sample, ...Array(points - sample.length).fill().map((_, i) =>
                baseValue + (sample.length + i) * increment + Math.random() * randomRange
            )];
        }
    }
    // Fallback to original generation
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
    // Fallback to original generation
    const baseValue = dummyData?.forecastBaseValue || 4.1;
    const increment = dummyData?.forecastIncrement || 0.15;
    const randomRange = dummyData?.forecastRandomRange || 0.9;
    return Array(points).fill().map((_, i) => baseValue + i * increment + Math.random() * randomRange);
}
