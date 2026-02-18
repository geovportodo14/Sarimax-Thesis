import { useMemo } from 'react';
import { useDashboard } from '../context/DashboardContext';
import { generateLabels, generateApplianceForecast, generateActual, generateForecastPast } from '../utils/forecastUtils';

export function useChartData(selectedFilter = 'All Appliances') {
    const {
        dummyData, loading,
        selectedPeriod, selectedLookback
    } = useDashboard();

    const labels = useMemo(() => {
        return generateLabels(selectedPeriod, selectedLookback);
    }, [selectedPeriod, selectedLookback]);

    const periodKey = useMemo(() => {
        return selectedPeriod === 1 ? '1hour' :
            selectedPeriod === 4 ? '4hours' :
                selectedPeriod === 8 ? '8hours' :
                    selectedPeriod === 24 ? '24hours' : null;
    }, [selectedPeriod]);

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
                customDatasets: null
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
        let customDatasets = null; // Re-use

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
                    pointRadius: 0
                },
                {
                    label: 'Refrigerator',
                    data: [...prevActualDataTotal.map(v => v * 0.25), ...nextApplianceForecasts.ref],
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.4,
                    pointRadius: 0
                },
                {
                    label: 'Electric Fan',
                    data: [...prevActualDataTotal.map(v => v * 0.10), ...nextApplianceForecasts.ef],
                    borderColor: '#8b5cf6',
                    backgroundColor: 'rgba(139, 92, 246, 0.1)',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.4,
                    pointRadius: 0
                },
                {
                    label: 'Others',
                    data: [...prevActualDataTotal.map(v => v * 0.05), ...Array(labels.nextPoints).fill(0).map(() => 0.05 + Math.random() * 0.05)],
                    borderColor: '#9ca3af',
                    backgroundColor: 'rgba(156, 163, 175, 0.1)',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.4,
                    pointRadius: 0
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

    return { labels, chartData };
}
