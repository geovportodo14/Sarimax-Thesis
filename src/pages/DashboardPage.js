import React, { useState, useMemo } from 'react';
import { useDashboard } from '../context/DashboardContext';
import DashboardHeader from '../components/DashboardHeader';
import DateNavigator from '../components/DateNavigator';
import ActualForecastChart from '../components/ActualForecastChart';
import PreviousForecastChart from '../components/PreviousForecastChart';
import ForecastControls from '../components/ForecastControls';
import ConsumptionRanking from '../components/ConsumptionRanking';

// Features
import LearningModeBanner from '../features/dashboard/LearningModeBanner';
import LockedBudgetCard from '../features/dashboard/LockedBudgetCard';
// import SetupChecklist from '../features/dashboard/SetupChecklist'; // Optional: Use if we want to show checklist on dashboard

import { useChartData } from '../hooks/useChartData';

import { format } from 'date-fns';

function DashboardPage() {
    const {
        // State from Context
        selectedPeriod, setSelectedPeriod,
        selectedLookback, setSelectedLookback,
        tariff, setTariff,
        budget, setBudget,
        allTime, setAllTime,
        currentDate, setCurrentDate,
        dummyData, loading,

        // Navigation handlers
        handlePrevDate, handleNextDate,

        // App Phase Logic
        appPhase, baselineDays, budgetUnlocked
    } = useDashboard();

    // Local UI state
    const [selectedFilter, setSelectedFilter] = useState('All Appliances');

    // Use custom hook for chart data
    const { labels, chartData } = useChartData(selectedFilter, selectedPeriod, selectedLookback, dummyData, loading);

    // Calculate totals and costs
    const calculations = useMemo(() => {
        if (!chartData || loading) return {
            prevTotal: 0, nextTotal: 0, prevCost: 0, nextCost: 0,
            appliances: [], topAppliance: 'None', budgetStatus: 'Unknown', selectedPeriodText: ''
        };

        const prevTotal = chartData.prevActualData.reduce((a, b) => (b || 0) + a, 0);
        const nextTotal = chartData.nextForecastData_Total.reduce((a, b) => (b || 0) + a, 0);
        const prevCost = prevTotal * tariff;
        const nextCost = nextTotal * tariff;

        const acKwh = chartData.nextApplianceForecasts.ac.reduce((a, b) => a + b, 0);
        const refKwh = chartData.nextApplianceForecasts.ref.reduce((a, b) => a + b, 0);
        const efKwh = chartData.nextApplianceForecasts.ef.reduce((a, b) => a + b, 0);

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

        const budgetStatus = nextCost < budget ? 'OK' : 'At-Risk';

        const selectedPeriodText =
            selectedPeriod === 1 ? 'Next 1 Hour' :
                selectedPeriod === 4 ? 'Next 4 Hours' :
                    selectedPeriod === 8 ? 'Next 8 Hours' : 'Next 24 Hours';

        return {
            prevTotal,
            nextTotal,
            prevCost,
            nextCost,
            appliances,
            topAppliance,
            budgetStatus,
            selectedPeriodText,
        };
    }, [chartData, tariff, budget, selectedPeriod]);

    if (loading) {
        return (
            <div className="min-h-screen bg-surface-50 flex items-center justify-center">
                <div className="text-center animate-fade-in">
                    <div className="relative">
                        <div className="animate-spin rounded-full h-16 w-16 border-4 border-primary-200 border-t-primary-600 mx-auto mb-4"></div>
                    </div>
                    <p className="text-surface-500 font-medium text-lg mt-4">Loading dashboard data...</p>
                </div>
            </div>
        );
    }

    if (!dummyData) {
        return (
            <div className="min-h-screen bg-surface-50 flex items-center justify-center p-4">
                <div className="text-center max-w-sm">
                    <div className="w-16 h-16 bg-surface-200 rounded-full flex items-center justify-center mx-auto mb-4 text-surface-500">
                        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                    </div>
                    <h2 className="text-lg font-bold text-surface-900 mb-2">Unable to load data</h2>
                    <p className="text-surface-500 mb-6">We couldn't fetch your energy data. Please check your connection and try again.</p>
                    <button
                        onClick={() => window.location.reload()}
                        className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
                    >
                        Retry
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-transparent py-4 px-4 transition-colors duration-300">
            <div className="container mx-auto max-w-7xl animate-fade-in">

                {/* Global Header (now responsible for nav only, date nav moved below) */}
                <DashboardHeader
                    notifications={[]} // Connect real notifications here later
                    settings={{}}
                    onSaveSettings={() => { }}
                />

                {/* Date Selection */}
                <DateNavigator
                    selectedDate={currentDate}
                    onDateChange={setCurrentDate}
                    onPrevClick={handlePrevDate}
                    onNextClick={handleNextDate}
                />

                {/* Learning Mode Banner */}
                {appPhase === 'learning' && (
                    <LearningModeBanner
                        daysCollected={baselineDays}
                        daysRequired={30}
                    />
                )}

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
                    <div className="lg:col-span-2">
                        <ActualForecastChart
                            labels={[...labels.prevLabels, ...labels.nextLabels]}
                            actualData={chartData.actualData}
                            forecastData={chartData.forecastSeries}
                            allTime={allTime}
                            onAllTimeChange={setAllTime}
                            selectedFilter={selectedFilter}
                            onFilterChange={setSelectedFilter}
                            applianceFilters={['All Appliances', 'All Appliances (Breakdown)', 'Electric Fan', 'Air Conditioner', 'Refrigerator']}
                            customDatasets={chartData.customDatasets}
                        />
                    </div>

                    <div>
                        <PreviousForecastChart
                            previousValue={calculations.prevTotal}
                            forecastValue={calculations.nextTotal}
                        />
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div>
                        {/* Budget Control: Gated by Learning Mode */}
                        {budgetUnlocked ? (
                            <ForecastControls
                                historyPeriod={selectedLookback}
                                forecastPeriod={selectedPeriod}
                                tariff={tariff}
                                budget={budget}
                                onHistoryChange={setSelectedLookback}
                                onForecastChange={setSelectedPeriod}
                                onTariffChange={setTariff}
                                onBudgetChange={setBudget}
                            />
                        ) : (
                            <LockedBudgetCard daysLeft={30 - baselineDays} />
                        )}
                    </div>

                    <ConsumptionRanking appliances={calculations.appliances} />
                </div>
            </div>
        </div>
    );
}

export default DashboardPage;
