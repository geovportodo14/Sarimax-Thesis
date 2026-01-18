import React, { useState, useEffect, useMemo, useCallback } from 'react';
import DashboardHeader from './components/DashboardHeader';
import ActualForecastChart from './components/ActualForecastChart';
import PreviousForecastChart from './components/PreviousForecastChart';
import ForecastControls from './components/ForecastControls';
import ConsumptionRanking from './components/ConsumptionRanking';
import EnergyForecastSummary from './components/EnergyForecastSummary';

// Utility functions
function generateApplianceForecast(points, dummyData = null) {
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

function generateLabels(forecastHours, lookbackHours) {
  const now = new Date();

  const prevPoints = Math.max(1, lookbackHours);
  const nextPoints = Math.max(1, forecastHours);

  let prevLabels = [], nextLabels = [];
  for (let i = prevPoints; i > 0; i--) prevLabels.push(formatHour(now, -i));
  for (let i = 0; i < nextPoints; i++) nextLabels.push(formatHour(now, i));

  return { prevLabels, nextLabels, prevPoints, nextPoints };
}

function formatHour(date, offsetHours) {
  const d = new Date(date);
  d.setHours(d.getHours() + offsetHours);

  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  const yy = String(d.getFullYear()).slice(-2);
  const hh = String(d.getHours()).padStart(2, '0');
  const mi = String(d.getMinutes()).padStart(2, '0');

  return `${mm}/${dd}/${yy} ${hh}:${mi}`;
}

function generateActual(points, dummyData = null, periodKey = null) {
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

function generateForecastPast(points, dummyData = null, periodKey = null) {
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


function App() {
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
          // No longer overriding selectedFilter here to keep 'All Appliances' as default or let user choose
        }
      } catch (error) {
        console.error('Error loading dummy dataset:', error);
        // Continue with default values if JSON fails to load
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
      // Return empty data while loading
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

    // Check if we have sample data for the selected forecast period
    let nextApplianceForecasts;
    if (dummyData && dummyData.sampleData && periodKey && dummyData.sampleData[periodKey]?.forecast) {
      const sampleForecast = dummyData.sampleData[periodKey].forecast;
      const forecastLength = sampleForecast.ac.length;

      if (forecastLength >= labels.nextPoints) {
        // Use sample data, trim to match
        nextApplianceForecasts = {
          ac: sampleForecast.ac.slice(0, labels.nextPoints),
          ref: sampleForecast.refrigerator.slice(0, labels.nextPoints),
          wm: sampleForecast.washingMachine.slice(0, labels.nextPoints),
          ef: Array(labels.nextPoints).fill(0).map(() => 0.15 + Math.random() * 0.1), // Generate EF for sample too
        };
      } else {
        // Use sample as base, generate additional
        nextApplianceForecasts = generateApplianceForecast(labels.nextPoints, dummyData);
        // Overwrite first part with sample data
        nextApplianceForecasts.ac = [...sampleForecast.ac, ...nextApplianceForecasts.ac.slice(forecastLength)];
        nextApplianceForecasts.ref = [...sampleForecast.refrigerator, ...nextApplianceForecasts.ref.slice(forecastLength)];
        nextApplianceForecasts.wm = [...sampleForecast.washingMachine, ...nextApplianceForecasts.wm.slice(forecastLength)];
        // For EF, if sampleForecast had it, we'd use it, but for now, it's generated by generateApplianceForecast
      }
    } else {
      // Generate using ranges from JSON or fallback
      nextApplianceForecasts = generateApplianceForecast(labels.nextPoints, dummyData);
    }

    const prevActualDataTotal = generateActual(labels.prevPoints, dummyData, periodKey);
    const prevForecastDataTotal = generateForecastPast(labels.prevPoints, dummyData, periodKey);

    // Filter Logic
    let prevActualData, prevForecastData, nextForecastData;
    let customDatasets = null;

    if (selectedFilter === 'All Appliances') {
      prevActualData = prevActualDataTotal;
      prevForecastData = prevForecastDataTotal;
      nextForecastData = nextApplianceForecasts.ac.map((v, i) =>
        v + nextApplianceForecasts.ref[i] + nextApplianceForecasts.wm[i] + nextApplianceForecasts.ef[i]
      );
    } else if (selectedFilter === 'All Appliances (Breakdown)') {
      // Keep the totals for the summary calculations
      prevActualData = prevActualDataTotal;
      prevForecastData = prevForecastDataTotal;
      nextForecastData = nextApplianceForecasts.ac.map((v, i) => v + nextApplianceForecasts.ref[i] + nextApplianceForecasts.wm[i] + nextApplianceForecasts.ef[i]);

      // Create custom datasets for the chart
      customDatasets = [
        {
          label: 'Air Conditioner',
          data: [...prevActualDataTotal.map(v => v * 0.55), ...nextApplianceForecasts.ac],
          borderColor: '#3b82f6', // blue
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
          borderColor: '#10b981', // green
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
          borderColor: '#8b5cf6', // purple
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
          borderColor: '#9ca3af', // gray
          backgroundColor: 'rgba(156, 163, 175, 0.1)',
          borderWidth: 2,
          fill: false,
          tension: 0.4,
          pointRadius: 0,
          pointHoverRadius: 5
        }
      ];

    } else if (selectedFilter === 'Air Conditioner') {
      // Estimate historical data for AC (approx 55%)
      prevActualData = prevActualDataTotal.map(v => v * 0.55);
      prevForecastData = prevForecastDataTotal.map(v => v * 0.55);
      nextForecastData = nextApplianceForecasts.ac;
    } else if (selectedFilter === 'Refrigerator') {
      // Estimate historical data for Ref (approx 25%)
      prevActualData = prevActualDataTotal.map(v => v * 0.25);
      prevForecastData = prevForecastDataTotal.map(v => v * 0.25);
      nextForecastData = nextApplianceForecasts.ref;
    } else if (selectedFilter === 'Electric Fan') {
      // Estimate historical data for EF (approx 10%)
      prevActualData = prevActualDataTotal.map(v => v * 0.10);
      prevForecastData = prevForecastDataTotal.map(v => v * 0.10);
      nextForecastData = nextApplianceForecasts.ef;
    } else {
      // Fallback logic for other appliances (approx 5%)
      prevActualData = prevActualDataTotal.map(v => v * 0.05);
      prevForecastData = prevForecastDataTotal.map(v => v * 0.05);
      // Small random forecast for others
      nextForecastData = Array(labels.nextPoints).fill(0).map(() => 0.1 + Math.random() * 0.1);
    }

    const forecastSeries = [...prevForecastData, ...nextForecastData];
    const actualData = [...prevActualData, ...Array(labels.nextPoints).fill(null)];

    return {
      prevActualData: prevActualDataTotal, // Keep total for other calculations if needed
      prevForecastData: prevForecastDataTotal,
      nextForecastData_Total: nextApplianceForecasts.ac.map((v, i) => v + nextApplianceForecasts.ref[i] + nextApplianceForecasts.wm[i] + nextApplianceForecasts.ef[i]),
      forecastSeries,
      actualData,
      nextApplianceForecasts,
      customDatasets // Return this new property
    };
  }, [labels, dummyData, periodKey, loading, selectedFilter]);

  // Calculate totals and costs
  const calculations = useMemo(() => {
    // We want the Summary and Rankings to ALWAYS be based on the Totals, not the filtered view
    const prevTotal = chartData.prevActualData.reduce((a, b) => (b || 0) + a, 0);
    // Use the total forecast data we stored
    const nextTotal = chartData.nextForecastData_Total.reduce((a, b) => (b || 0) + a, 0);
    const prevCost = prevTotal * tariff;
    const nextCost = nextTotal * tariff;

    // Appliance calculations
    const acKwh = chartData.nextApplianceForecasts.ac.reduce((a, b) => a + b, 0);
    const refKwh = chartData.nextApplianceForecasts.ref.reduce((a, b) => a + b, 0);
    // const wmKwh = chartData.nextApplianceForecasts.wm.reduce((a, b) => a + b, 0);
    const efKwh = chartData.nextApplianceForecasts.ef.reduce((a, b) => a + b, 0);

    const acPhp = acKwh * tariff;
    const refPhp = refKwh * tariff;
    // const wmPhp = wmKwh * tariff;
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
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center">
        <div className="text-center animate-fade-in">
          <div className="relative">
            <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-200 border-t-blue-600 mx-auto mb-4"></div>
            <div className="absolute inset-0 flex items-center justify-center">
              <svg className="w-8 h-8 text-blue-600 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
          </div>
          <p className="text-gray-600 font-medium text-lg mt-4">Loading dashboard data...</p>
          <p className="text-gray-400 text-sm mt-2">Please wait a moment</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50/30 to-indigo-50/30 py-8 px-4">
      <div className="container mx-auto max-w-7xl">
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

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
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

          <EnergyForecastSummary
            nextKwh={calculations.nextTotal}
            nextPhp={calculations.nextCost}
            prevKwh={calculations.prevTotal}
            prevPhp={calculations.prevCost}
            actualKwh={calculations.prevTotal}
            actualPhp={calculations.prevCost}
            topAppliance={calculations.topAppliance}
            budgetStatus={calculations.budgetStatus}
            selectedPeriodText={calculations.selectedPeriodText}
          />
        </div>
      </div>
    </div>
  );
}

export default App;

