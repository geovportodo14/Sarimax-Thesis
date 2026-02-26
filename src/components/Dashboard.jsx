import React, { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer
} from 'recharts';

const Dashboard = () => {
    // ---------------------------------------------------------------------------
    // State Management (Strictly locked to Manila Time to match backend)
    // ---------------------------------------------------------------------------
    const systemDate = useMemo(() => {
        // Enforce Asia/Manila timezone for the frontend to prevent "Time Travel" desyncs
        return new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Manila' }).format(new Date());
    }, []);

    const [selectedDate, setSelectedDate] = useState(systemDate);
    const [horizon, setHorizon] = useState(4);
    const [chartData, setChartData] = useState([]);
    const [aggregateTotalKwh, setAggregateTotalKwh] = useState(0);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const isHistoricalView = selectedDate !== systemDate;

    // ---------------------------------------------------------------------------
    // Data Fetching & Time Travel UI Logic
    // ---------------------------------------------------------------------------
    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            setError(null);
            try {
                let response;
                if (isHistoricalView) {
                    response = await axios.get(`/api/historical?date=${selectedDate}`);
                } else {
                    response = await axios.get(`/api/live?horizon=${horizon}`);
                }

                const { data, aggregate_total_kwh } = response.data;
                setChartData(data);
                setAggregateTotalKwh(aggregate_total_kwh);
            } catch (err) {
                console.error("Error fetching dashboard data", err);
                setError("Failed to load energy data.");
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [selectedDate, horizon, isHistoricalView]);

    useEffect(() => {
        if (isHistoricalView) setHorizon(4);
    }, [isHistoricalView]);

    // Using raw hex variables extracted directly from Tailwind config for Recharts props
    const COLOR_ACTUAL = '#002855'; // Deep Navy Blue
    const COLOR_FORECAST = '#FF7F00'; // Vibrant Orange

    // ---------------------------------------------------------------------------
    // Render (Reskinned with Meralco Tailwind Theme)
    // ---------------------------------------------------------------------------
    return (
        <div className="min-h-screen bg-surface-muted p-6 lg:p-10 font-sans text-accent">

            <div className="max-w-7xl mx-auto space-y-8">
                {/* Header Title */}
                <header className="flex items-center justify-between">
                    <h1 className="text-3xl font-bold tracking-tight text-accent">
                        Household Energy Consumption
                    </h1>
                </header>

                {/* Total Aggregate Summary Card (High Visual Weight) */}
                <div className="bg-accent rounded-xl shadow-card p-8 border hover:shadow-lg transition-shadow">
                    <div className="flex flex-col items-center justify-center text-center">
                        <h2 className="text-surface font-medium uppercase tracking-widest text-sm mb-2 opacity-80">
                            Forecast Summary (3 Appliances)
                        </h2>
                        <div className="flex items-baseline space-x-2 text-white">
                            <span className="text-6xl font-extrabold tracking-tight">
                                {loading ? '...' : aggregateTotalKwh}
                            </span>
                            <span className="text-2xl font-semibold opacity-90">kWh</span>
                        </div>
                    </div>
                </div>

                {/* Dashboard Controls (Date Picker & Horizon Toggles) */}
                <div className="bg-surface rounded-xl shadow-card p-6 border border-surface-border flex flex-col sm:flex-row items-center justify-between space-y-4 sm:space-y-0">

                    {/* Time Travel Date Picker */}
                    <div className="flex items-center space-x-3 w-full sm:w-auto">
                        <label htmlFor="datePicker" className="text-sm font-semibold text-accent opacity-80 uppercase tracking-wider">
                            Select Date:
                        </label>
                        <input
                            type="date"
                            id="datePicker"
                            className="px-4 py-2 border border-surface-border rounded-lg text-accent font-medium shadow-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
                            value={selectedDate}
                            max={systemDate}
                            onChange={(e) => setSelectedDate(e.target.value)}
                        />
                    </div>

                    {/* Conditional Forecast Horizon Buttons */}
                    <div className="flex items-center space-x-3 w-full sm:w-auto">
                        <span className="text-sm font-semibold text-accent opacity-80 uppercase tracking-wider">
                            Prediction Horizon:
                        </span>
                        <div className="flex space-x-2">
                            {[1, 4, 8, 24].map(h => (
                                <button
                                    key={h}
                                    onClick={() => setHorizon(h)}
                                    disabled={isHistoricalView}
                                    className={`
                    px-5 py-2 rounded-lg text-sm font-bold tracking-wide transition-all shadow-sm
                    ${isHistoricalView
                                            ? 'bg-surface-muted text-gray-400 opacity-50 cursor-not-allowed border outline-none'
                                            : horizon === h
                                                ? 'bg-primary text-white hover:bg-primary-hover border border-transparent shadow-md' // Active (Orange)
                                                : 'bg-surface text-accent hover:bg-surface-muted border border-surface-border' // Inactive (White/Gray)
                                        }
                  `}
                                >
                                    {h} HR
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Chart Viewport */}
                <div className="bg-surface rounded-xl shadow-card p-6 border border-surface-border h-[500px] w-full flex flex-col">
                    <h3 className="text-lg font-bold text-accent mb-6 ml-2">Appliance Power Load (Actual vs SARIMAX Model)</h3>

                    {loading ? (
                        <div className="flex-grow flex items-center justify-center text-accent animate-pulse font-medium">
                            Loading chart telemetry...
                        </div>
                    ) : error ? (
                        <div className="flex-grow flex items-center justify-center text-red-500 font-medium bg-red-50 rounded-lg">
                            {error}
                        </div>
                    ) : (
                        <div className="flex-grow">
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart
                                    data={chartData}
                                    margin={{ top: 10, right: 30, left: 10, bottom: 5 }}
                                >
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                                    <XAxis
                                        dataKey="timestamp"
                                        tick={{ fill: '#002855' }}
                                        tickMargin={10}
                                        axisLine={false}
                                        tickLine={false}
                                    />
                                    <YAxis
                                        label={{ value: 'Watts (w)', angle: -90, position: 'insideLeft', fill: '#002855', fontWeight: 'bold' }}
                                        tick={{ fill: '#002855' }}
                                        axisLine={false}
                                        tickLine={false}
                                    />
                                    {/* Styled Tooltip container */}
                                    <Tooltip
                                        contentStyle={{ borderRadius: '8px', border: '1px solid #E2E8F0', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}
                                    />
                                    <Legend
                                        wrapperStyle={{ paddingTop: '20px' }}
                                        iconType="circle"
                                    />

                                    {/* Actual Consumption (Deep Navy Blue, Solid) */}
                                    <Line
                                        type="monotone"
                                        dataKey="actual_w"
                                        name="Actual Ground Truth"
                                        stroke={COLOR_ACTUAL}
                                        strokeWidth={4}
                                        dot={{ r: 3, fill: COLOR_ACTUAL, strokeWidth: 0 }}
                                        activeDot={{ r: 6 }}
                                        connectNulls={false}
                                    />

                                    {/* Predicted Consumption (Vibrant Orange, Dashed) */}
                                    <Line
                                        type="monotone"
                                        dataKey="forecast_w"
                                        name="SARIMAX Predictive Trend"
                                        stroke={COLOR_FORECAST}
                                        strokeWidth={3}
                                        strokeDasharray="6 6"
                                        dot={false}
                                        activeDot={{ r: 6, fill: COLOR_FORECAST, strokeWidth: 0 }}
                                        connectNulls={false}
                                    />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
