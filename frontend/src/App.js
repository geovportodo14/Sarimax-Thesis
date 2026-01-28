import React, { useState, useEffect, useMemo, useCallback } from 'react';
import DashboardHeader from './components/DashboardHeader';
import ActualForecastChart from './components/ActualForecastChart';
import PreviousForecastChart from './components/PreviousForecastChart';
import ForecastControls from './components/ForecastControls';
import ConsumptionRanking from './components/ConsumptionRanking';
import EnergyForecastSummary from './components/EnergyForecastSummary';
import ApplianceChart from './components/ApplianceChart';
import { Card, CardBody, Skeleton } from './components/ui';

// Fixed appliance list - only these three appliances
const APPLIANCES = ['Electric Fan', 'Air Conditioner', 'Refrigerator'];

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================
function generateApplianceForecast(points, dummyData = null) {
  let fan = [], ac = [], ref = [];
  
  if (dummyData && dummyData.applianceRanges) {
    const ranges = dummyData.applianceRanges;
    for (let i = 0; i < points; i++) {
      fan.push(ranges['Electric Fan']?.min + Math.random() * (ranges['Electric Fan']?.max - ranges['Electric Fan']?.min) || 0.05 + Math.random() * 0.1);
      ac.push(ranges['Air Conditioner']?.min + Math.random() * (ranges['Air Conditioner']?.max - ranges['Air Conditioner']?.min) || 2.2 + Math.random() * 0.6);
      ref.push(ranges['Refrigerator']?.min + Math.random() * (ranges['Refrigerator']?.max - ranges['Refrigerator']?.min) || 1.1 + Math.random() * 0.3);
    }
  } else {
    for (let i = 0; i < points; i++) {
      fan.push(0.05 + Math.random() * 0.1);  // Electric Fan: ~50-150W
      ac.push(2.2 + Math.random() * 0.6);     // Air Conditioner: ~2.2-2.8 kWh
      ref.push(1.1 + Math.random() * 0.3);    // Refrigerator: ~1.1-1.4 kWh
    }
  }
  return { fan, ac, ref };
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
    if (sample.length >= points) {
      return sample.slice(0, points);
    } else {
      const baseValue = dummyData.actualBaseValue || 4.2;
      const increment = dummyData.actualIncrement || 0.15;
      const randomRange = dummyData.actualRandomRange || 0.8;
      return [...sample, ...Array(points - sample.length).fill().map((_, i) => 
        baseValue + (sample.length + i) * increment + Math.random() * randomRange
      )];
    }
  }
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
  const baseValue = dummyData?.forecastBaseValue || 4.1;
  const increment = dummyData?.forecastIncrement || 0.15;
  const randomRange = dummyData?.forecastRandomRange || 0.9;
  return Array(points).fill().map((_, i) => baseValue + i * increment + Math.random() * randomRange);
}

// =============================================================================
// LOADING SKELETON COMPONENT
// =============================================================================
function LoadingState() {
  return (
    <div className="min-h-screen bg-transparent">
      {/* Header skeleton */}
      <div className="bg-white border-b border-surface-100 px-4 sm:px-6 lg:px-8 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Skeleton width={40} height={40} rounded="xl" />
            <div className="hidden sm:block">
              <Skeleton width={150} height={20} className="mb-1" />
              <Skeleton width={200} height={14} />
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Skeleton width={40} height={40} rounded="xl" />
            <Skeleton width={160} height={40} rounded="xl" />
            <Skeleton width={40} height={40} rounded="xl" />
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Hero skeleton */}
        <div className="bg-white rounded-2xl border border-surface-100 p-6 mb-6">
          <div className="flex items-center gap-3 mb-4">
            <Skeleton width={40} height={40} rounded="xl" />
            <div>
              <Skeleton width={180} height={24} className="mb-1" />
              <Skeleton width={120} height={16} />
            </div>
          </div>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            {[1, 2, 3, 4].map((i) => (
              <Skeleton key={i} height={100} rounded="xl" />
            ))}
          </div>
          <div className="space-y-2">
            <Skeleton height={48} rounded="xl" />
            <Skeleton height={48} rounded="xl" />
            <Skeleton height={48} rounded="xl" />
          </div>
        </div>

        {/* Charts skeleton */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <Skeleton height={400} rounded="2xl" />
          </div>
          <Skeleton height={400} rounded="2xl" />
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// MAIN APP COMPONENT
// =============================================================================
function App() {
  // State
  const [selectedPeriod, setSelectedPeriod] = useState(1);
  const [selectedLookback, setSelectedLookback] = useState(1);
  const [tariff, setTariff] = useState(13.47);
  const [budget, setBudget] = useState(300);
  const [allTime, setAllTime] = useState(true);
  const [selectedFilter, setSelectedFilter] = useState('Electric Fan');
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
        
        if (data.settings) {
          if (data.settings.defaultTariff) setTariff(data.settings.defaultTariff);
          if (data.settings.defaultBudget) setBudget(data.settings.defaultBudget);
          if (data.settings.appliances && data.settings.appliances.length > 0) {
            setSelectedFilter(data.settings.appliances[0]);
          }
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

  // Generate data based on labels
  const chartData = useMemo(() => {
    if (loading) {
      return {
        prevActualData: [],
        prevForecastData: [],
        nextForecastData: [],
        forecastSeries: [],
        actualData: [],
        nextApplianceForecasts: { fan: [], ac: [], ref: [] },
      };
    }

    let nextApplianceForecasts;
    if (dummyData && dummyData.sampleData && periodKey && dummyData.sampleData[periodKey]?.forecast) {
      const sampleForecast = dummyData.sampleData[periodKey].forecast;
      const forecastLength = sampleForecast.ac?.length || 0;
      
      if (forecastLength >= labels.nextPoints) {
        nextApplianceForecasts = {
          fan: sampleForecast.electricFan?.slice(0, labels.nextPoints) || generateApplianceForecast(labels.nextPoints, dummyData).fan,
          ac: sampleForecast.ac.slice(0, labels.nextPoints),
          ref: sampleForecast.refrigerator.slice(0, labels.nextPoints),
        };
      } else {
        nextApplianceForecasts = generateApplianceForecast(labels.nextPoints, dummyData);
        if (sampleForecast.electricFan) {
          nextApplianceForecasts.fan = [...sampleForecast.electricFan, ...nextApplianceForecasts.fan.slice(forecastLength)];
        }
        if (sampleForecast.ac) {
          nextApplianceForecasts.ac = [...sampleForecast.ac, ...nextApplianceForecasts.ac.slice(forecastLength)];
        }
        if (sampleForecast.refrigerator) {
          nextApplianceForecasts.ref = [...sampleForecast.refrigerator, ...nextApplianceForecasts.ref.slice(forecastLength)];
        }
      }
    } else {
      nextApplianceForecasts = generateApplianceForecast(labels.nextPoints, dummyData);
    }

    const prevActualData = generateActual(labels.prevPoints, dummyData, periodKey);
    const prevForecastData = generateForecastPast(labels.prevPoints, dummyData, periodKey);
    const nextForecastData = nextApplianceForecasts.fan.map((v, i) =>
      v + nextApplianceForecasts.ac[i] + nextApplianceForecasts.ref[i]
    );
    const forecastSeries = [...prevForecastData, ...nextForecastData];
    const actualData = [...prevActualData, ...Array(labels.nextPoints).fill(null)];

    return {
      prevActualData,
      prevForecastData,
      nextForecastData,
      forecastSeries,
      actualData,
      nextApplianceForecasts,
    };
  }, [labels, dummyData, periodKey, loading]);

  // Calculate totals and costs
  const calculations = useMemo(() => {
    const prevTotal = chartData.prevActualData.reduce((a, b) => (b || 0) + a, 0);
    const nextTotal = chartData.nextForecastData.reduce((a, b) => (b || 0) + a, 0);
    const prevCost = prevTotal * tariff;
    const nextCost = nextTotal * tariff;

    const fanKwh = chartData.nextApplianceForecasts.fan.reduce((a, b) => a + b, 0);
    const acKwh = chartData.nextApplianceForecasts.ac.reduce((a, b) => a + b, 0);
    const refKwh = chartData.nextApplianceForecasts.ref.reduce((a, b) => a + b, 0);

    const fanPhp = fanKwh * tariff;
    const acPhp = acKwh * tariff;
    const refPhp = refKwh * tariff;

    // Only these three appliances
    const appliances = [
      { name: 'Electric Fan', kwh: fanKwh, php: fanPhp },
      { name: 'Air Conditioner', kwh: acKwh, php: acPhp },
      { name: 'Refrigerator', kwh: refKwh, php: refPhp },
    ];

    // Determine top appliance
    const maxPhp = Math.max(fanPhp, acPhp, refPhp);
    const topAppliance =
      acPhp === maxPhp ? 'Air Conditioner' :
      refPhp === maxPhp ? 'Refrigerator' : 'Electric Fan';

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
      // Individual appliance data for charts
      applianceData: {
        'Electric Fan': { kwh: fanKwh, php: fanPhp, data: chartData.nextApplianceForecasts.fan },
        'Air Conditioner': { kwh: acKwh, php: acPhp, data: chartData.nextApplianceForecasts.ac },
        'Refrigerator': { kwh: refKwh, php: refPhp, data: chartData.nextApplianceForecasts.ref },
      },
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

  // Scroll to charts section
  const handleViewDetails = useCallback(() => {
    const chartsSection = document.getElementById('charts-section');
    if (chartsSection) {
      chartsSection.scrollIntoView({ behavior: 'smooth' });
    }
  }, []);

  // Show loading state
  if (loading) {
    return <LoadingState />;
  }

  return (
    <div className="min-h-screen bg-transparent">
      {/* Sticky Header */}
      <DashboardHeader
        date={formattedDate}
        onPrevClick={handlePrevDate}
        onNextClick={handleNextDate}
      />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8">
        {/* =====================================================================
            SECTION 1: FORECAST SUMMARY (ABOVE THE FOLD)
            ===================================================================== */}
        <section className="mb-8 animate-fade-in">
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
            budget={budget}
            onViewDetails={handleViewDetails}
          />
        </section>

        {/* =====================================================================
            SECTION 2: TODAY'S QUICK STATS
            ===================================================================== */}
        <section className="mb-8 animate-slide-up">
          <h2 className="text-heading-md text-surface-700 mb-4 flex items-center gap-2">
            <svg className="w-5 h-5 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            Today at a Glance
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <Card>
              <CardBody className="p-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-sky-50 text-sky-600 flex items-center justify-center">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-caption text-surface-500">Current Rate</p>
                    <p className="text-heading-md text-surface-900 tabular-nums">₱{tariff.toFixed(2)}</p>
                    <p className="text-caption text-surface-400">per kWh</p>
                  </div>
                </div>
              </CardBody>
            </Card>
            
            <Card>
              <CardBody className="p-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-700 flex items-center justify-center">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-caption text-surface-500">Top Consumer</p>
                    <p className="text-body-md font-semibold text-surface-900 truncate">{calculations.topAppliance}</p>
                    <p className="text-caption text-surface-400">highest usage</p>
                  </div>
                </div>
              </CardBody>
            </Card>
            
            <Card>
              <CardBody className="p-4">
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                    calculations.budgetStatus === 'OK' ? 'bg-emerald-50 text-emerald-600' : 'bg-red-50 text-red-600'
                  }`}>
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-caption text-surface-500">Budget</p>
                    <p className="text-heading-md text-surface-900 tabular-nums">₱{budget}</p>
                    <p className={`text-caption ${calculations.budgetStatus === 'OK' ? 'text-emerald-600' : 'text-red-600'}`}>
                      {calculations.budgetStatus === 'OK' ? 'On track' : 'At risk'}
                    </p>
                  </div>
                </div>
              </CardBody>
            </Card>
            
            <Card>
              <CardBody className="p-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-caption text-surface-500">Forecast Period</p>
                    <p className="text-body-md font-semibold text-surface-900">{calculations.selectedPeriodText}</p>
                    <p className="text-caption text-surface-400">analysis range</p>
                  </div>
                </div>
              </CardBody>
            </Card>
          </div>
        </section>

        {/* =====================================================================
            SECTION 3: OVERALL CHARTS
            ===================================================================== */}
        <section id="charts-section" className="mb-8 scroll-mt-20">
          <h2 className="text-heading-md text-surface-700 mb-4 flex items-center gap-2">
            <svg className="w-5 h-5 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            Overall Energy Analytics
          </h2>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <ActualForecastChart
                labels={[...labels.prevLabels, ...labels.nextLabels]}
                actualData={chartData.actualData}
                forecastData={chartData.forecastSeries}
                allTime={allTime}
                onAllTimeChange={setAllTime}
                selectedFilter={selectedFilter}
                onFilterChange={setSelectedFilter}
                applianceFilters={['All Appliances', ...APPLIANCES]}
                riskStatus={calculations.budgetStatus}
              />
            </div>
            <div>
              <PreviousForecastChart
                previousValue={calculations.prevTotal}
                forecastValue={calculations.nextTotal}
                budgetThreshold={budget / tariff}
              />
            </div>
          </div>
        </section>

        {/* =====================================================================
            SECTION 4: INDIVIDUAL APPLIANCE CHARTS
            ===================================================================== */}
        <section className="mb-8">
          <h2 className="text-heading-md text-surface-700 mb-4 flex items-center gap-2">
            <svg className="w-5 h-5 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            Appliance Breakdown
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {APPLIANCES.map((appliance) => {
              const appData = calculations.applianceData[appliance];
              // Generate per-appliance actual data (proportional to forecast)
              const applianceActual = chartData.prevActualData.map((val, i) => {
                if (val === null) return null;
                // Distribute actual based on appliance's proportion
                const proportion = appData.kwh / (calculations.nextTotal || 1);
                return val * proportion;
              });
              const applianceForecast = [...applianceActual.slice(0, labels.prevPoints), ...appData.data];
              
              return (
                <ApplianceChart
                  key={appliance}
                  applianceName={appliance}
                  labels={[...labels.prevLabels, ...labels.nextLabels]}
                  actualData={[...applianceActual, ...Array(labels.nextPoints).fill(null)]}
                  forecastData={applianceForecast}
                  kwh={appData.kwh}
                  cost={appData.php}
                  budgetStatus={calculations.budgetStatus}
                />
              );
            })}
          </div>
        </section>

        {/* =====================================================================
            SECTION 5: CONTROLS & CONSUMPTION RANKING
            ===================================================================== */}
        <section className="mb-8">
          <h2 className="text-heading-md text-surface-700 mb-4 flex items-center gap-2">
            <svg className="w-5 h-5 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
            </svg>
            Settings & Consumption Ranking
          </h2>
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
        </section>

        {/* =====================================================================
            FOOTER
            ===================================================================== */}
        <footer className="text-center py-6 border-t border-surface-100">
          <p className="text-body-sm text-surface-400">
            Energy Forecast Dashboard • Powered by SARIMAX Model
          </p>
        </footer>
      </main>
    </div>
  );
}

export default App;
