import React, { useState, useEffect, useMemo, useCallback } from 'react';
import DashboardHeader from '../components/DashboardHeader';
import ActualForecastChart from '../components/ActualForecastChart';
import PreviousForecastChart from '../components/PreviousForecastChart';
import ForecastControls from '../components/ForecastControls';
import ConsumptionRanking from '../components/ConsumptionRanking';

function DashboardPage() {
    const [selectedPeriod, setSelectedPeriod] = useState(4); // default 4 hours
    const [selectedLookback, setSelectedLookback] = useState(1);
    const [tariff, setTariff] = useState(13.47);
    const [budget, setBudget] = useState(300);
    const [allTime, setAllTime] = useState(true);
    const [selectedFilter, setSelectedFilter] = useState('All Appliances');
    const [currentDate, setCurrentDate] = useState(new Date());
    
    // --- LIVE API STATE ---
    const [chartData, setChartData] = useState({
        aggregate_total_kwh: 0,
        data: []
    });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // --- MANILA TIMEZONE HELPERS ---
    const isToday = useMemo(() => {
        const todayStr = new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Manila' }).format(new Date());
        const selectedStr = new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Manila' }).format(currentDate);
        return todayStr === selectedStr;
    }, [currentDate]);

    // Fetch True MongoDB Data
    useEffect(() => {
        const fetchDashboardData = async () => {
            setLoading(true);
            setError(null);
            try {
                const dateStr = new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Manila' }).format(currentDate);
                let endpoint = '';
                
                if (isToday) {
                    // LIVE FORECAST (Today)
                    endpoint = `/api/live?horizon=${selectedPeriod}`;
                } else {
                    // HISTORICAL DATE
                    endpoint = `/api/historical?date=${dateStr}`;
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
    }, [currentDate, selectedPeriod, isToday]);


    // Extract the Arrays for Recharts
    const processedChartData = useMemo(() => {
        if (!chartData || !chartData.data) return { labels: [], actuals: [], forecasts: [] };

        const labels = chartData.data.map(d => d.timestamp);
        const actuals = chartData.data.map(d => d.actual_w);
        const forecasts = chartData.data.map(d => d.forecast_w);

        return { labels, actuals, forecasts };
    }, [chartData]);


    const calculations = useMemo(() => {
        const totalKwh = chartData.aggregate_total_kwh || 0;
        const currentCost = totalKwh * tariff;
        
        // Very basic appliance estimation because Phase 1 only tracks Aggregate Total in UI
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
    }, [chartData.aggregate_total_kwh, tariff, budget]);

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
                        {/* Modified the Recharts wrapper to consume the flat arrays generated by out /api/live controller */}
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
                        />
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
        </div>
    );
}

export default DashboardPage;
