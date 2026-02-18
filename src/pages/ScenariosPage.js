import React, { useMemo, useState } from 'react';
import { useDashboard } from '../context/DashboardContext';
import DashboardHeader from '../components/DashboardHeader';
import ScenarioControls from '../components/ScenarioControls';
import ActualForecastChart from '../components/ActualForecastChart';
import ScenarioOutcomeCard from '../features/scenarios/ScenarioOutcomeCard';
import { generateLabels, generateApplianceForecast, generateActual, generateForecastPast } from '../utils/forecastUtils';

export default function ScenariosPage() {
    const {
        dummyData, loading,
        currentDate,
        tariff,
        scenarioParams,
        isScenarioMode, setIsScenarioMode
    } = useDashboard();

    // Force scenario mode on when visiting this page
    React.useEffect(() => {
        if (!isScenarioMode) {
            setIsScenarioMode(true);
        }
    }, [isScenarioMode, setIsScenarioMode]);

    const labels = useMemo(() => generateLabels(24, 24), []); // Fixed 24h lookback/forecast for scenarios

    // Calculate baseline and scenario data
    const chartData = useMemo(() => {
        if (loading || !dummyData) return null;

        const baselineForecast = generateApplianceForecast(labels.nextPoints, dummyData);

        // Sum appliance forecasts for total baseline (Next 24h)
        const baselineTotalNext = baselineForecast.ac.map((v, i) =>
            v + baselineForecast.ref[i] + baselineForecast.wm[i] + baselineForecast.ef[i]
        );

        // Previous data (for context)
        const prevActual = generateActual(labels.prevPoints, dummyData, '24hours');

        // Apply Scenario Adjustments
        // Load Adjustment: Percentage change to forecast
        const loadMultiplier = 1 + (scenarioParams.loadAdjustment / 100);

        const scenarioTotalNext = baselineTotalNext.map(val => val * loadMultiplier);

        return {
            prevActual,
            baselineTotalNext,
            scenarioTotalNext
        };
    }, [dummyData, loading, labels, scenarioParams.loadAdjustment]);

    // Financial calculations
    const finances = useMemo(() => {
        if (!chartData) return { baseline: 0, scenario: 0 };

        const baselineKwh = chartData.baselineTotalNext.reduce((a, b) => a + b, 0);
        const scenarioKwh = chartData.scenarioTotalNext.reduce((a, b) => a + b, 0);

        const baselineCost = baselineKwh * tariff;
        const scenarioCost = scenarioKwh * scenarioParams.tariffAdjustment;

        return { baseline: baselineCost, scenario: scenarioCost };

    }, [chartData, tariff, scenarioParams.tariffAdjustment]);

    // Prepare chart datasets for comparison
    const comparisonDatasets = useMemo(() => {
        if (!chartData) return [];

        return [
            {
                label: 'Baseline Forecast',
                data: [...Array(labels.prevPoints).fill(null), ...chartData.baselineTotalNext],
                borderColor: '#9ca3af', // Gray
                borderDash: [5, 5],
                borderWidth: 2,
                fill: false,
                tension: 0.4,
                pointRadius: 0
            },
            {
                label: 'Scenario Projection',
                data: [...Array(labels.prevPoints).fill(null), ...chartData.scenarioTotalNext],
                borderColor: '#6366f1', // Indigo
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 0
            }
        ];
    }, [chartData, labels]);

    if (loading) return null;

    return (
        <div className="min-h-screen bg-surface-50">
            <DashboardHeader
                notifications={[]}
                settings={{}}
                onSaveSettings={() => { }}
            />

            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8 pt-6">
                <div className="mb-6">
                    <h1 className="text-display-sm text-surface-900">Scenario Simulator</h1>
                    <p className="text-surface-600">Simulate changes in tariff rates or consumption to see the financial impact.</p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
                    <div className="lg:col-span-2">
                        {/* Reusing ActualForecastChart but overriding data with custom comparison */}
                        <ActualForecastChart
                            labels={[...labels.prevLabels, ...labels.nextLabels]}
                            actualData={chartData?.prevActual || []}
                            forecastData={[]} // Hide default forecast
                            customDatasets={comparisonDatasets}
                            allTime={false} // Force recent view
                            onAllTimeChange={() => { }} // No-op
                            selectedFilter="Comparison" // Dummy
                            onFilterChange={() => { }} // No-op
                            applianceFilters={[]} // Hide filters
                        />
                    </div>

                    <div className="space-y-6">
                        <ScenarioControls hideToggle />
                        <ScenarioOutcomeCard
                            baselineCost={finances.baseline}
                            scenarioCost={finances.scenario}
                        />
                    </div>
                </div>
            </main>
        </div>
    );
}
