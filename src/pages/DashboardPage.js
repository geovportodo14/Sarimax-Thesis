import React, { useState, useEffect, useMemo, useCallback } from 'react';
import DashboardHeader from '../components/DashboardHeader';
import ActualForecastChart from '../components/ActualForecastChart';
import PreviousForecastChart from '../components/PreviousForecastChart';
import ForecastControls from '../components/ForecastControls';
import ConsumptionRanking from '../components/ConsumptionRanking';
import { getApiUrl } from '../utils/api';
import { calculateMeralcoBill } from '../utils/meralcoCalculator';
import BillBreakdownModal from '../components/BillBreakdownModal';
import { ReceiptText } from 'lucide-react';

function DashboardPage() {
    const [selectedPeriod, setSelectedPeriod] = useState(4); // default 4 hours
    const [selectedLookback, setSelectedLookback] = useState(1);
    const [tariff, setTariff] = useState(13.47);
    const [budget, setBudget] = useState(300);
    const [allTime, setAllTime] = useState(true);
    const [selectedFilter, setSelectedFilter] = useState('All Appliances');
    const [currentDate, setCurrentDate] = useState(new Date());
    const [isModalOpen, setIsModalOpen] = useState(false);

    // --- LIVE API STATE ---
    const [chartData, setChartData] = useState({
        aggregate_total_kwh: 0,
        data: []
    });

    // NEW: Tomorrow's ML Forecast State
    const [dailyForecastData, setDailyForecastData] = useState(null);
    const [loadingForecast, setLoadingForecast] = useState(false);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // --- MANILA TIMEZONE HELPERS ---
    const isToday = useMemo(() => {
        const todayStr = new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Manila' }).format(new Date());
        const selectedStr = new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Manila' }).format(currentDate);
        return todayStr === selectedStr;
    }, [currentDate]);

    const isTomorrow = useMemo(() => {
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        const tomorrowStr = new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Manila' }).format(tomorrow);
        const selectedStr = new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Manila' }).format(currentDate);
        return tomorrowStr === selectedStr;
    }, [currentDate]);

    // Fetch True MongoDB Data (Historical/Live or Tomorrow's ML Forecast)
    useEffect(() => {
        const fetchDashboardData = async () => {
            const dateStr = new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Manila' }).format(currentDate);

            // ── IF TOMORROW: Fetch ML Daily Forecast ──
            if (isTomorrow) {
                setLoadingForecast(true);
                setError(null);
                try {
                    const response = await fetch(getApiUrl(`/api/forecast/daily?date=${dateStr}`));
                    const result = await response.json();

                    if (response.ok && (result.status === 'success' || result.status === 'no_data')) {
                        setDailyForecastData(result);
                        // Mock empty chart for tomorrow (since it runs daily, chart isn't intra-day)
                        setChartData({ aggregate_total_kwh: 0, data: [] });
                    } else {
                        setDailyForecastData(null); // No data generated yet
                    }
                } catch (err) {
                    console.error("Forecast API Error:", err);
                    setError("Failed to fetch next-day forecast");
                } finally {
                    setLoadingForecast(false);
                    setLoading(false);
                }
                return;
            }

            // ── IF TODAY OR PAST: Fetch Normal Telemetry ──
            setLoading(true);
            setError(null);
            setDailyForecastData(null); // Clear ML state

            try {
                let endpoint = '';
                if (isToday) {
                    // LIVE FORECAST (Today)
                    endpoint = getApiUrl(`/api/live?horizon=${selectedPeriod}`);
                } else {
                    // HISTORICAL DATE
                    endpoint = getApiUrl(`/api/historical?date=${dateStr}`);
                }

                const response = await fetch(endpoint);
                const result = await response.json();

                if (response.ok) {
                    setChartData(result);
                } else {
                    throw new Error(result.error || "Failed to fetch dashboard data");
                }
            } catch (err) {
                console.error("API Error:", err);
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchDashboardData();
    }, [currentDate, selectedPeriod, isToday, isTomorrow]);


    // Extract the Arrays for Recharts
    const processedChartData = useMemo(() => {
        if (!chartData || !chartData.data) return { labels: [], actuals: [], forecasts: [] };

        const currentGranularity = chartData.granularity || 60;
        const maxForecastBuckets = Math.floor((selectedPeriod * 60) / currentGranularity);

        const currentBucketIndex = chartData.current_bucket_index ?? -1;

        const labels = chartData.data.map(d => d.timestamp);
        const actuals = chartData.data.map(d => d.actual_kwh);
        const forecasts = chartData.data.map(d => d.forecast_kwh);

        // Calculate sum of forecasts strictly bounded by the selected horizon limit
        const totalForecastedKwh = forecasts.reduce((sum, val, i) => {
            if (i <= currentBucketIndex || i > currentBucketIndex + maxForecastBuckets) return sum;
            return sum + (val || 0);
        }, 0);

        return { labels, actuals, forecasts, totalForecastedKwh };
    }, [chartData, selectedPeriod]);

    // Format ML Data for Recharts
    const processedMLChartData = useMemo(() => {
        if (!dailyForecastData || !dailyForecastData.appliances || dailyForecastData.appliances.length === 0) {
            return { labels: [], actuals: [], forecasts: [] };
        }

        // Sum up all appliances for each hour
        const firstApp = dailyForecastData.appliances[0];
        if (!firstApp || !firstApp.hourly_forecast) return { labels: [], actuals: [], forecasts: [] };

        const labels = firstApp.hourly_forecast.map(h => {
            const d = new Date(h.timestamp);
            const hours = d.getHours().toString().padStart(2, '0');
            const minutes = d.getMinutes().toString().padStart(2, '0');
            return `${hours}:${minutes}`;
        });

        const forecasts = new Array(firstApp.hourly_forecast.length).fill(0);
        dailyForecastData.appliances.forEach(app => {
            app.hourly_forecast.forEach((h, i) => {
                forecasts[i] += h.predicted_kwh;
            });
        });

        // Actuals is empty for tomorrow
        const actuals = new Array(firstApp.hourly_forecast.length).fill(null);

        return { labels, actuals, forecasts };
    }, [dailyForecastData]);

    const scheduleInsights = useMemo(() => {
        const schedule = dailyForecastData?.schedule;
        const summary = dailyForecastData?.optimization_summary || schedule?.optimization_summary || null;
        if (!schedule) {
            return {
                hasSchedule: false,
                baselineCost: null,
                optimizedCost: null,
                savings: null,
                peakReduction: null,
                topActions: [],
                actionRows: []
            };
        }

        const actionRows = [];
        (schedule.appliances || []).forEach(app => {
            (app.hourly || []).forEach(row => {
                if (Math.abs(row.delta_kwh || 0) >= 0.03 && row.action !== 'Keep baseline usage') {
                    actionRows.push({
                        appliance: app.appliance,
                        hour: row.hour,
                        action: row.action,
                        delta: row.delta_kwh
                    });
                }
            });
        });
        actionRows.sort((a, b) => Math.abs(b.delta) - Math.abs(a.delta));

        return {
            hasSchedule: true,
            baselineCost: schedule.baseline_total_cost_php ?? null,
            optimizedCost: schedule.optimized_total_cost_php ?? null,
            savings: schedule.estimated_savings_php ?? summary?.estimated_savings_php ?? null,
            peakReduction: schedule.peak_reduction_kwh ?? summary?.peak_reduction_kwh ?? null,
            topActions: summary?.top_actions || [],
            actionRows: actionRows.slice(0, 6)
        };
    }, [dailyForecastData]);


    const calculations = useMemo(() => {
        // Handle Tomorrow's ML Data
        if (isTomorrow && dailyForecastData && dailyForecastData.appliances && dailyForecastData.appliances.length > 0) {
            let totalKwh = 0;
            let currentCost = 0;
            const appliances = [];

            dailyForecastData.appliances.forEach(app => {
                totalKwh += app.total_predicted_kwh;
                currentCost += app.total_predicted_cost_php;

                const appName = app.appliance === 'electric_fan' ? 'Electric Fan' :
                    app.appliance === 'aircon' ? 'Air Conditioner' :
                        app.appliance === 'refrigerator' ? 'Refrigerator' : app.appliance;

                appliances.push({
                    name: appName,
                    kwh: app.total_predicted_kwh,
                    php: app.total_predicted_cost_php
                });
            });

            // Fallback ranking if empty
            appliances.sort((a, b) => b.php - a.php);
            const topAppliance = appliances.length > 0 ? appliances[0].name : 'Air Conditioner';
            const budgetStatus = currentCost < budget ? 'OK' : 'At-Risk';

            return { totalKwh, currentCost, appliances, topAppliance, budgetStatus };
        }
        if (isTomorrow && dailyForecastData?.schedule) {
            const schedule = dailyForecastData.schedule;
            const appliances = (schedule.appliances || []).map(app => ({
                name: app.appliance === 'electric_fan' ? 'Electric Fan' :
                    app.appliance === 'aircon' ? 'Air Conditioner' :
                        app.appliance === 'refrigerator' ? 'Refrigerator' : app.appliance,
                kwh: app.optimized_total_kwh ?? app.baseline_total_kwh ?? 0,
                php: (app.optimized_total_kwh ?? app.baseline_total_kwh ?? 0) * tariff
            }));
            const totalKwh = appliances.reduce((sum, app) => sum + (app.kwh || 0), 0);
            const currentCost = schedule.optimized_total_cost_php ?? (totalKwh * tariff);
            appliances.sort((a, b) => b.php - a.php);
            const topAppliance = appliances.length > 0 ? appliances[0].name : 'Air Conditioner';
            const budgetStatus = currentCost < budget ? 'OK' : 'At-Risk';
            return { totalKwh, currentCost, appliances, topAppliance, budgetStatus };
        }

        // Handle Today/Past Telemetry Data
        const actualSoFarKwh = chartData.aggregate_total_kwh || 0;
        const projectedUpcomingKwh = processedChartData.totalForecastedKwh || 0;
        const totalKwh = actualSoFarKwh + projectedUpcomingKwh;
        const currentCost = totalKwh * tariff;

        const acKwh = totalKwh * 0.55;
        const refKwh = totalKwh * 0.25;
        const efKwh = totalKwh * 0.20;

        const acPhp = acKwh * tariff;
        const refPhp = refKwh * tariff;
        const efPhp = efKwh * tariff;

        const appliances = [
            { name: 'Air Conditioner', kwh: acKwh, php: acPhp },
            { name: 'Refrigerator', kwh: refKwh, php: refPhp },
            { name: 'Electric Fan', kwh: efKwh, php: efPhp },
        ];

        const topAppliance =
            acPhp >= refPhp && acPhp >= efPhp ? 'Air Conditioner' :
                refPhp >= acPhp && refPhp >= efPhp ? 'Refrigerator' : 'Electric Fan';

        const budgetStatus = currentCost < budget ? 'OK' : 'At-Risk';

        return {
            totalKwh,
            currentCost,
            appliances,
            topAppliance,
            budgetStatus
        };
    }, [chartData.aggregate_total_kwh, tariff, budget, isTomorrow, dailyForecastData, processedChartData.totalForecastedKwh]);

    const formattedDate = useMemo(() => {
        const options = { month: 'long', day: 'numeric', year: 'numeric' };
        return currentDate.toLocaleDateString('en-US', options);
    }, [currentDate]);

    const handlePrevDate = useCallback(() => {
        const newDate = new Date(currentDate);
        newDate.setDate(newDate.getDate() - 1);
        setCurrentDate(newDate);
    }, [currentDate]);

    const handleNextDate = useCallback(() => {
        const newDate = new Date(currentDate);
        newDate.setDate(newDate.getDate() + 1);
        setCurrentDate(newDate);
    }, [currentDate]);

    if (loading) {
        return (
            <div className="min-h-screen bg-transparent flex items-center justify-center">
                <div className="text-center animate-fade-in">
                    <div className="relative">
                        <div className="animate-spin rounded-full h-16 w-16 border-4 border-primary-200 border-t-primary-600 mx-auto mb-4"></div>
                    </div>
                    <p className="text-[var(--color-text-secondary)] font-medium text-lg mt-4">Loading real MongoDB data...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-transparent flex items-center justify-center">
                <div className="text-center">
                    <p className="text-red-500 font-bold mb-4">Error loading data</p>
                    <p className="text-gray-600">{error}</p>
                </div>
            </div>
        )
    }

    return (
        <div className="min-h-screen bg-transparent py-8 px-4 transition-colors duration-300">
            <div className="container mx-auto max-w-7xl animate-fade-in">
                <DashboardHeader
                    date={formattedDate}
                    selectedDate={currentDate}
                    onDateChange={setCurrentDate}
                    onPrevClick={handlePrevDate}
                    onNextClick={handleNextDate}
                />

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
                    <div className="lg:col-span-2">
                        {isTomorrow ? (
                            <div className="bg-white rounded-3xl p-6 lg:p-8 shadow-sm border border-surface-200 min-h-[400px] flex flex-col items-center justify-center text-center">
                                {loadingForecast ? (
                                    <div className="animate-pulse flex flex-col items-center">
                                        <div className="h-12 w-12 bg-primary-100 rounded-full mb-4"></div>
                                        <div className="h-4 w-48 bg-surface-200 rounded mb-2"></div>
                                        <div className="h-3 w-32 bg-surface-100 rounded"></div>
                                    </div>
                                ) : (!dailyForecastData || ((dailyForecastData.appliances?.length || 0) === 0 && !dailyForecastData.schedule)) ? (
                                    <div className="max-w-md">
                                        <div className="w-16 h-16 bg-blue-50 text-blue-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
                                            <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                            </svg>
                                        </div>
                                        <h3 className="text-xl font-bold text-surface-900 mb-2">Forecast Pending</h3>
                                        <p className="text-surface-600">The SARIMAX pipeline runs nightly at 11:30 PM. Check back tomorrow for the detailed 24-hr layout.</p>
                                    </div>
                                ) : (
                                    <div className="w-full text-left flex flex-col h-full">
                                        <div className="mb-4 flex justify-between items-center bg-gradient-to-r from-primary-50 to-blue-50 p-4 border border-primary-100 rounded-2xl shrink-0">
                                            <div>
                                                <h3 className="text-lg font-bold text-primary-900">Tomorrow's Exact Pipeline Details</h3>
                                                <p className="text-sm text-primary-700">
                                                    SARIMAX forecast + MILP appliance scheduling recommendations
                                                </p>
                                            </div>
                                            <div className="text-right flex flex-col items-end">
                                                <div className="text-2xl font-black text-primary-800">₱{calculations.currentCost.toFixed(2)}</div>
                                                {scheduleInsights.hasSchedule && scheduleInsights.savings > 0 && (
                                                    <span className="text-xs font-bold mt-1 px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700">
                                                        Save ₱{Number(scheduleInsights.savings).toFixed(2)}
                                                    </span>
                                                )}
                                                <button
                                                    onClick={() => setIsModalOpen(true)}
                                                    className="flex items-center gap-1.5 text-xs font-bold text-primary-600 hover:text-primary-800 transition-colors mt-1"
                                                >
                                                    <ReceiptText size={14} />
                                                    View Receipt
                                                </button>
                                            </div>
                                        </div>

                                        {scheduleInsights.hasSchedule && (
                                            <div className="mb-4 space-y-3">
                                                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                                                    <div className="rounded-xl border border-surface-200 bg-surface-50 px-3 py-2">
                                                        <p className="text-[11px] uppercase tracking-wide text-surface-500">Before Cost</p>
                                                        <p className="text-lg font-bold text-surface-900">
                                                            ₱{Number(scheduleInsights.baselineCost ?? calculations.currentCost).toFixed(2)}
                                                        </p>
                                                    </div>
                                                    <div className="rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-2">
                                                        <p className="text-[11px] uppercase tracking-wide text-emerald-700">After Scheduling</p>
                                                        <p className="text-lg font-bold text-emerald-800">
                                                            ₱{Number(scheduleInsights.optimizedCost ?? calculations.currentCost).toFixed(2)}
                                                        </p>
                                                    </div>
                                                    <div className="rounded-xl border border-blue-200 bg-blue-50 px-3 py-2">
                                                        <p className="text-[11px] uppercase tracking-wide text-blue-700">Peak Reduction</p>
                                                        <p className="text-lg font-bold text-blue-800">
                                                            {Number(scheduleInsights.peakReduction ?? 0).toFixed(3)} kWh
                                                        </p>
                                                    </div>
                                                </div>

                                                {(scheduleInsights.topActions.length > 0 || scheduleInsights.actionRows.length > 0) && (
                                                    <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3">
                                                        <p className="text-xs font-bold text-amber-800 mb-2">Suggested Appliance Actions</p>
                                                        <ul className="space-y-1 text-xs text-amber-900">
                                                            {(scheduleInsights.topActions.length > 0
                                                                ? scheduleInsights.topActions.slice(0, 2)
                                                                : scheduleInsights.actionRows.map(item => (
                                                                    `${item.appliance.replace('_', ' ')} ${item.action} at ${String(item.hour).padStart(2, '0')}:00`
                                                                )).slice(0, 2)
                                                            ).map((line, idx) => (
                                                                <li key={`${line}-${idx}`}>- {line}</li>
                                                            ))}
                                                        </ul>
                                                    </div>
                                                )}
                                            </div>
                                        )}

                                        <div className="flex-grow w-full min-h-[300px]">
                                            {processedMLChartData.labels.length > 0 ? (
                                                <ActualForecastChart
                                                    labels={processedMLChartData.labels}
                                                    actualData={processedMLChartData.actuals}
                                                    forecastData={processedMLChartData.forecasts}
                                                    allTime={allTime}
                                                    onAllTimeChange={setAllTime}
                                                    selectedFilter={selectedFilter}
                                                    onFilterChange={setSelectedFilter}
                                                    applianceFilters={['All Appliances']}
                                                    customDatasets={null}
                                                    showSlider={true}
                                                />
                                            ) : (
                                                <div className="h-full rounded-2xl border border-surface-200 bg-surface-50 flex items-center justify-center text-center px-6">
                                                    <p className="text-sm text-surface-600">
                                                        Hourly SARIMAX curve is unavailable from MongoDB for this date, but schedule optimization summary is ready.
                                                    </p>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                )}
                            </div>
                        ) : (
                            <ActualForecastChart
                                labels={processedChartData.labels}
                                actualData={processedChartData.actuals}
                                forecastData={processedChartData.forecasts}
                                allTime={allTime}
                                onAllTimeChange={setAllTime}
                                selectedFilter={selectedFilter}
                                onFilterChange={setSelectedFilter}
                                applianceFilters={['All Appliances']}
                                customDatasets={null}
                                showSlider={true}
                            />
                        )}
                    </div>

                    <div>
                        <PreviousForecastChart
                            previousValue={calculations.totalKwh * 0.9}
                            forecastValue={calculations.totalKwh}
                        />
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <ForecastControls
                        historyPeriod={selectedLookback}
                        forecastPeriod={selectedPeriod}
                        disabledForecast={!isToday}
                        tariff={tariff}
                        budget={budget}
                        onHistoryChange={setSelectedLookback}
                        onForecastChange={setSelectedPeriod}
                        onTariffChange={setTariff}
                        onBudgetChange={setBudget}
                    />

                    <ConsumptionRanking appliances={calculations.appliances} />
                </div>
            </div>

            {/* Render the Receipt Modal */}
            <BillBreakdownModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                billData={calculateMeralcoBill(calculations.totalKwh)}
            />
        </div>
    );
}

export default DashboardPage;
