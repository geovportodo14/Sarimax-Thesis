import React, { useState } from 'react';
import { useDashboard } from '../context/DashboardContext';
import DashboardHeader from '../components/DashboardHeader';
import DateNavigator from '../components/DateNavigator';
import ActualForecastChart from '../components/ActualForecastChart';
import ForecastControls from '../components/ForecastControls';
import { useChartData } from '../hooks/useChartData';

export default function ForecastPage() {
    const {
        currentDate, setCurrentDate,
        handlePrevDate, handleNextDate,
        tariff, setTariff,
        budget, setBudget,
        selectedPeriod, setSelectedPeriod,
        selectedLookback, setSelectedLookback,
        allTime, setAllTime,
        dummyData
    } = useDashboard();

    const [selectedFilter, setSelectedFilter] = useState('All Appliances (Breakdown)');
    const { labels, chartData } = useChartData(selectedFilter);

    if (!dummyData) return null;

    return (
        <div className="min-h-screen bg-surface-50">
            <DashboardHeader
                notifications={[]}
                settings={{}}
                onSaveSettings={() => { }}
            />

            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8 pt-6">
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h1 className="text-display-sm text-surface-900">Detailed Forecast</h1>
                        <p className="text-surface-600">Deep dive into your appliance usage patterns.</p>
                    </div>
                    <DateNavigator
                        selectedDate={currentDate}
                        onDateChange={setCurrentDate}
                        onPrevClick={handlePrevDate}
                        onNextClick={handleNextDate}
                    />
                </div>

                <div className="bg-white rounded-2xl p-6 shadow-sm border border-surface-200 mb-6">
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

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <div className="lg:col-span-1">
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
                    </div>
                    <div className="lg:col-span-2 bg-surface-100 rounded-xl p-6 flex items-center justify-center text-surface-500">
                        <p>Additional Analysis Widgets Coming Soon</p>
                    </div>
                </div>
            </main>
        </div>
    );
}
