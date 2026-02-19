export const generateMockData = (daysActive: number) => {
    const data = []
    const now = new Date()

    // Generate 24 hours of data points
    for (let i = 0; i < 24; i++) {
        const time = new Date(now)
        time.setHours(now.getHours() - (23 - i))

        // Simulate usage curve (peak in evening)
        const hour = time.getHours()
        let baseLoad = 0.5
        if (hour >= 18 && hour <= 22) baseLoad = 2.5 // Evening peak
        if (hour >= 9 && hour <= 17) baseLoad = 1.0 // Day use

        // Add noise
        const actual = Math.max(0, baseLoad + (Math.random() * 0.5 - 0.25))

        // Forecast data (future points or overlapping for comparison)
        // For this chart: "Actual" is up to now, "Forecast" is future
        // But to show comparison, let's say "Forecast" exists for the whole day

        data.push({
            time: time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            actual: i < 24 ? parseFloat(actual.toFixed(2)) : null, // All past
            forecast: parseFloat((actual * 1.05).toFixed(2)) // Slight variance
        })
    }
    return data
}
