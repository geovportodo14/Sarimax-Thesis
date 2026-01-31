import React, { useState, useEffect, useMemo, useCallback } from 'react';
import DashboardHeader from '../components/DashboardHeader';
import ActualForecastChart from '../components/ActualForecastChart';
import PreviousForecastChart from '../components/PreviousForecastChart';
import ForecastControls from '../components/ForecastControls';
import ConsumptionRanking from '../components/ConsumptionRanking';

import { generateLabels, generateApplianceForecast, generateActual, generateForecastPast } from '../utils/forecastUtils';

function DashboardPage() {
    const [selectedPeriod, setSelectedPeriod] = useState(1);
    const [selectedLookback, setSelectedLookback] = useState(1);
    const [tariff, setTariff] = useState(13.47);
    const [budget, setBudget] = useState(300);
    const [allTime, setAllTime] = useState(true);
    const [selectedFilter, setSelectedFilter] = useState('All Appliances');
    const [currentDate, setCurrentDate] = useState(new Date());
    const [dummyData, setDummyData] = useState(null);
    const [loading, setLoading] = useState(true);

    // Load dummy dataset from JSON file
    useEffect(() => {
        const loadDummyData = async () => {
            try {
                const response = await fetch('/data/dummydataset.json');
                const data = await response.json();
                setDummyData(data);

                // Initialize tariff and budget from JSON if available
                if (data.settings) {
                    if (data.settings.defaultTariff) setTariff(data.settings.defaultTariff);
                    if (data.settings.defaultBudget) setBudget(data.settings.defaultBudget);
                }
            } catch (error) {
                console.error('Error loading dummy dataset:', error);
            } finally {
                setLoading(false);
            }
        };

        loadDummyData();
    }, []);

    // Generate labels based on selected periods
    const labels = useMemo(() => {
        return generateLabels(selectedPeriod, selectedLookback);
    }, [selectedPeriod, selectedLookback]);

    // Get period key for JSON lookup
    const periodKey = useMemo(() => {
        return selectedPeriod === 1 ? '1hour' :
            selectedPeriod === 4 ? '4hours' :
                selectedPeriod === 8 ? '8hours' :
                    selectedPeriod === 24 ? '24hours' : null;
    }, [selectedPeriod]);

    // Generate data based on labels, using dummy dataset if available
    const chartData = useMemo(() => {
        if (loading) {
            return {
                prevActualData: [],
                prevForecastData: [],
                nextForecastData: [],
                nextForecastData_Total: [],
                forecastSeries: [],
                actualData: [],
                nextApplianceForecasts: { ac: [], ref: [], wm: [], ef: [] },
            };
        }

        let nextApplianceForecasts;
        if (dummyData && dummyData.sampleData && periodKey && dummyData.sampleData[periodKey]?.forecast) {
            const sampleForecast = dummyData.sampleData[periodKey].forecast;
            const forecastLength = sampleForecast.ac.length;

            if (forecastLength >= labels.nextPoints) {
                nextApplianceForecasts = {
                    ac: sampleForecast.ac.slice(0, labels.nextPoints),
                    ref: sampleForecast.refrigerator.slice(0, labels.nextPoints),
                    wm: sampleForecast.washingMachine.slice(0, labels.nextPoints),
                    ef: Array(labels.nextPoints).fill(0).map(() => 0.15 + Math.random() * 0.1),
                };
            } else {
                nextApplianceForecasts = generateApplianceForecast(labels.nextPoints, dummyData);
                nextApplianceForecasts.ac = [...sampleForecast.ac, ...nextApplianceForecasts.ac.slice(forecastLength)];
                nextApplianceForecasts.ref = [...sampleForecast.refrigerator, ...nextApplianceForecasts.ref.slice(forecastLength)];
                nextApplianceForecasts.wm = [...sampleForecast.washingMachine, ...nextApplianceForecasts.wm.slice(forecastLength)];
            }
        } else {
            nextApplianceForecasts = generateApplianceForecast(labels.nextPoints, dummyData);
        }

        const prevActualDataTotal = generateActual(labels.prevPoints, dummyData, periodKey);
        const prevForecastDataTotal = generateForecastPast(labels.prevPoints, dummyData, periodKey);

        let prevActualData, prevForecastData, nextForecastData;
        let customDatasets = null;

        if (selectedFilter === 'All Appliances') {
            prevActualData = prevActualDataTotal;
            prevForecastData = prevForecastDataTotal;
            nextForecastData = nextApplianceForecasts.ac.map((v, i) =>
                v + nextApplianceForecasts.ref[i] + nextApplianceForecasts.wm[i] + nextApplianceForecasts.ef[i]
            );
        } else if (selectedFilter === 'All Appliances (Breakdown)') {
            prevActualData = prevActualDataTotal;
            prevForecastData = prevForecastDataTotal;
            nextForecastData = nextApplianceForecasts.ac.map((v, i) => v + nextApplianceForecasts.ref[i] + nextApplianceForecasts.wm[i] + nextApplianceForecasts.ef[i]);

            customDatasets = [
                {
                    label: 'Air Conditioner',
                    data: [...prevActualDataTotal.map(v => v * 0.55), ...nextApplianceForecasts.ac],
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 5
                },
                {
                    label: 'Refrigerator',
                    data: [...prevActualDataTotal.map(v => v * 0.25), ...nextApplianceForecasts.ref],
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 5
                },
                {
                    label: 'Electric Fan',
                    data: [...prevActualDataTotal.map(v => v * 0.10), ...nextApplianceForecasts.ef],
                    borderColor: '#8b5cf6',
                    backgroundColor: 'rgba(139, 92, 246, 0.1)',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 5
                },
                {
                    label: 'Others',
                    data: [...prevActualDataTotal.map(v => v * 0.05), ...Array(labels.nextPoints).fill(0).map(() => 0.05 + Math.random() * 0.05)],
                    borderColor: '#9ca3af',
                    backgroundColor: 'rgba(156, 163, 175, 0.1)',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 5
                }
            ];

        } else if (selectedFilter === 'Air Conditioner') {
            prevActualData = prevActualDataTotal.map(v => v * 0.55);
            prevForecastData = prevForecastDataTotal.map(v => v * 0.55);
            nextForecastData = nextApplianceForecasts.ac;
        } else if (selectedFilter === 'Refrigerator') {
            prevActualData = prevActualDataTotal.map(v => v * 0.25);
            prevForecastData = prevForecastDataTotal.map(v => v * 0.25);
            nextForecastData = nextApplianceForecasts.ref;
        } else if (selectedFilter === 'Electric Fan') {
            prevActualData = prevActualDataTotal.map(v => v * 0.10);
            prevForecastData = prevForecastDataTotal.map(v => v * 0.10);
            nextForecastData = nextApplianceForecasts.ef;
        } else {
            prevActualData = prevActualDataTotal.map(v => v * 0.05);
            prevForecastData = prevForecastDataTotal.map(v => v * 0.05);
            nextForecastData = Array(labels.nextPoints).fill(0).map(() => 0.1 + Math.random() * 0.1);
        }

        const forecastSeries = [...prevForecastData, ...nextForecastData];
        const actualData = [...prevActualData, ...Array(labels.nextPoints).fill(null)];

        return {
            prevActualData: prevActualDataTotal,
            prevForecastData: prevForecastDataTotal,
            nextForecastData_Total: nextApplianceForecasts.ac.map((v, i) => v + nextApplianceForecasts.ref[i] + nextApplianceForecasts.wm[i] + nextApplianceForecasts.ef[i]),
            forecastSeries,
            actualData,
            nextApplianceForecasts,
            customDatasets
        };
    }, [labels, dummyData, periodKey, loading, selectedFilter]);

    const calculations = useMemo(() => {
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

    // Format current date for header
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
                    <p className="text-[var(--color-text-secondary)] font-medium text-lg mt-4">Loading dashboard data...</p>
                </div>
            </div>
        );
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

                    <ConsumptionRanking appliances={calculations.appliances} />
                </div>
            </div>
        </div>
    );
}

export default DashboardPage;
