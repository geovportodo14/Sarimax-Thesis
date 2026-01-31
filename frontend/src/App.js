import React, { useMemo, useEffect, useRef } from 'react';
import DashboardHeader from './components/DashboardHeader';
import ForecastControls from './components/ForecastControls';
import ConsumptionRanking from './components/ConsumptionRanking';
import EnergyForecastSummary from './components/EnergyForecastSummary';
import DateNavigator from './components/DateNavigator';
import { Card, CardBody, Skeleton } from './components/ui/index';
import IntroductionModal from './components/onboarding/IntroductionModal';
import GuidedTour from './components/onboarding/GuidedTour';
import { DashboardProvider, useDashboard } from './context/DashboardContext';
import { AnimationWrapper } from './components/ui/AnimationWrapper';
import ScenarioControls from './components/ScenarioControls';
import ComparisonChart from './components/ui/ComparisonChart';

import { APPLIANCES, generateApplianceForecast, generateLabels, generateActual, generateForecastPast } from './utils/mockData';
import { ApplianceIcons } from './components/ui/icons';
import EnergyLineChart from './components/ui/EnergyLineChart';

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
// MAIN APP COMPONENT (CONTENT)
// =============================================================================
function DashboardContent() {
  const {
    // ... (destructured values unchanged)
    selectedPeriod,
    selectedLookback,
    tariff,
    budget,
    allTime,
    currentDate,
    dummyData,
    loading,
    showIntroduction,
    runTour,
    settings,
    notifications,

    // Setters
    setSelectedPeriod,
    setSelectedLookback,
    setTariff,
    setBudget,
    setAllTime,
    setCurrentDate, // Added if missing in previous context
    setNotifications,

    // Handlers
    handleSkipIntroduction,
    handleStartTour,
    handleTourComplete,
    handleRevisitGuide,
    handlePrevDate,
    handleNextDate,
    handleSaveSettings,

    // Scenario Mode
    isScenarioMode,
    scenarioParams,

    // Forecast Horizon
    forecastHorizon,
    setForecastHorizon
  } = useDashboard();

  // Generate labels based on selected periods
  const labels = useMemo(() => {
    return generateLabels(currentDate, selectedPeriod, selectedLookback);
  }, [currentDate, selectedPeriod, selectedLookback]);

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
    // Apply Scenario Logic
    let effectiveTariff = tariff;
    let loadMultiplier = 1;

    if (isScenarioMode) {
      effectiveTariff = scenarioParams.tariffAdjustment;
      loadMultiplier = 1 + (scenarioParams.loadAdjustment / 100);
    }

    const prevTotal = chartData.prevActualData.reduce((a, b) => (b || 0) + a, 0);
    // Apply load adjustment to forecast total
    const nextTotalBase = chartData.nextForecastData.reduce((a, b) => (b || 0) + a, 0);
    const nextTotal = nextTotalBase * loadMultiplier;

    const prevCost = prevTotal * tariff; // History stays with actual tariff
    const nextCost = nextTotal * effectiveTariff;

    // Apply load adjustment to appliances
    const fanKwh = chartData.nextApplianceForecasts.fan.reduce((a, b) => a + b, 0) * loadMultiplier;
    const acKwh = chartData.nextApplianceForecasts.ac.reduce((a, b) => a + b, 0) * loadMultiplier;
    const refKwh = chartData.nextApplianceForecasts.ref.reduce((a, b) => a + b, 0) * loadMultiplier;

    const fanPhp = fanKwh * effectiveTariff;
    const acPhp = acKwh * effectiveTariff;
    const refPhp = refKwh * effectiveTariff;

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
      // Individual appliance data for charts (scaled by multiplier for consistency if needed, assuming charts show total forecast)
      // Note: Passing raw data to charts might show original query. 
      // ideally we map the data arrays too, but for summary correctness we pass the totals.
      applianceData: {
        'Electric Fan': { kwh: fanKwh, php: fanPhp, data: chartData.nextApplianceForecasts.fan.map(v => v * loadMultiplier) },
        'Air Conditioner': { kwh: acKwh, php: acPhp, data: chartData.nextApplianceForecasts.ac.map(v => v * loadMultiplier) },
        'Refrigerator': { kwh: refKwh, php: refPhp, data: chartData.nextApplianceForecasts.ref.map(v => v * loadMultiplier) },
      },
    };
  }, [chartData, tariff, budget, selectedPeriod, isScenarioMode, scenarioParams]);

  // Handle dynamic budget alerts & email notifications
  const lastEmailSent = useRef({ type: null, timestamp: 0 });

  useEffect(() => {
    if (loading || !settings.emailEnabled || !settings.emailAddress) return;

    const budgetUsagePercent = Math.round((calculations.nextCost / budget) * 100);
    const now = Date.now();
    const COOLDOWN = 4 * 60 * 60 * 1000; // 4 hours

    let alertType = null;
    if (budgetUsagePercent >= settings.thresholdCritical) {
      alertType = 'critical';
    } else if (budgetUsagePercent >= settings.thresholdApproaching) {
      alertType = 'warning';
    }

    // Trigger email if threshold met and not on cooldown for this type
    if (alertType && (lastEmailSent.current.type !== alertType || (now - lastEmailSent.current.timestamp) > COOLDOWN)) {
      const sendEmailAlert = async () => {
        try {
          await fetch('/api/alerts/threshold', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              email: settings.emailAddress,
              usage_percent: budgetUsagePercent,
              budget: budget,
              cost: calculations.nextCost
            })
          });
          lastEmailSent.current = { type: alertType, timestamp: now };
          console.log(`Email alert (${alertType}) sent to:`, settings.emailAddress);
        } catch (error) {
          console.error('Failed to send email alert:', error);
        }
      };

      sendEmailAlert();
    }

    // Update UI Notifications
    const newNotifications = [];
    if (budgetUsagePercent >= settings.thresholdCritical) {
      newNotifications.push({
        id: 'budget-critical',
        type: 'at-risk',
        priority: 'high',
        title: 'Budget Exceeded!',
        message: `Your forecasted spend (${settings.currency === 'PHP' ? '₱' : '$'}${Math.round(calculations.nextCost)}) exceeds your budget limit.`,
        time: 'Just now',
        action: 'Adjust Budget'
      });
    } else if (budgetUsagePercent >= settings.thresholdApproaching) {
      newNotifications.push({
        id: 'budget-approaching',
        type: 'approaching',
        priority: 'medium',
        title: 'Approaching Budget Limit',
        message: `You've reached ${budgetUsagePercent}% of your set energy budget for this period.`,
        time: 'Just now',
        action: 'View Details'
      });
    }

    setNotifications(newNotifications);
  }, [calculations.nextCost, budget, settings, loading, setNotifications]);

  // Scroll to main chart
  const handleViewDetails = () => {
    const mainChart = document.getElementById('tour-main-chart');
    if (mainChart) {
      mainChart.scrollIntoView({ behavior: 'smooth' });
    }
  };

  // Show loading state
  if (loading) {
    return <LoadingState />;
  }

  return (
    <div className="min-h-screen bg-transparent">
      {/* Sticky Header */}
      <DashboardHeader
        onHelpClick={handleRevisitGuide}
        notifications={notifications}
        settings={settings}
        onSaveSettings={handleSaveSettings}
      />

      <IntroductionModal
        isOpen={showIntroduction}
        onSkip={handleSkipIntroduction}
        onNext={handleStartTour}
      />

      <GuidedTour
        run={runTour}
        onComplete={handleTourComplete}
      />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8 space-y-8">

        {/* =====================================================================
            SECTION 0: SCENARIO SIMULATOR
            ===================================================================== */}
        <AnimationWrapper variant="slideDown" className="mb-8" id="tour-scenario">
          <ScenarioControls />
        </AnimationWrapper>

        {/* =====================================================================
            SECTION 1: FORECAST SUMMARY (ABOVE THE FOLD)
            ===================================================================== */}
        <AnimationWrapper variant="fade-in" id="tour-summary">
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
            thresholdApproaching={settings.thresholdApproaching}
            thresholdCritical={settings.thresholdCritical}
          />
        </AnimationWrapper>

        {/* =====================================================================
            SECTION 2: TODAY'S QUICK STATS
            ===================================================================== */}
        <AnimationWrapper variant="slide-up" delay={0.1}>
          <h2 className="text-heading-md text-surface-700 mb-4 flex items-center gap-2">
            <svg className="w-5 h-5 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            Today at a Glance
          </h2>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
            <Card>
              <CardBody className="p-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-sky-50 text-sky-600 flex items-center justify-center">
                    {ApplianceIcons.Default}
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
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${calculations.budgetStatus === 'OK' ? 'bg-emerald-50 text-emerald-600' : 'bg-red-50 text-red-600'}`}>
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

          <div id="tour-comparison">
            <ComparisonChart
              previousKwh={calculations.prevTotal}
              previousCost={calculations.prevCost}
              forecastKwh={calculations.nextTotal}
              forecastCost={calculations.nextCost}
            />
          </div>

          <DateNavigator
            selectedDate={currentDate}
            onDateChange={setCurrentDate}
            onPrevClick={handlePrevDate}
            onNextClick={handleNextDate}
          />
        </AnimationWrapper>

        {/* =====================================================================
            SECTION 3: OVERALL CHARTS
            ===================================================================== */}
        <AnimationWrapper variant="slide-up" delay={0.2} id="charts-section" className="scroll-mt-20">
          <h2 className="text-heading-md text-surface-700 mb-4 flex items-center gap-2">
            <svg className="w-5 h-5 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            Overall Energy Analytics
          </h2>
          <div className="grid grid-cols-1 gap-6">
            <div id="tour-main-chart">
              <EnergyLineChart
                title="Actual vs Forecast"
                subtitle="Total energy consumption comparison"
                icon={
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                }
                labels={[...labels.prevLabels, ...labels.nextLabels]}
                actualData={chartData.actualData}
                forecastData={chartData.forecastSeries}
                riskStatus={calculations.budgetStatus}
                extraAction={
                  <div className="flex items-center gap-3 flex-wrap">
                    <div className="flex items-center gap-2 bg-surface-50 rounded-lg px-3 py-2 border border-surface-100">
                      <span className="text-body-sm font-medium text-surface-600">All-time</span>
                      <button
                        onClick={() => setAllTime(!allTime)}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2 ${allTime ? 'bg-primary-600' : 'bg-surface-300'}`}
                        role="switch"
                        aria-checked={allTime}
                      >
                        <span className={`inline-block h-4 w-4 transform rounded-full bg-white shadow-sm transition-transform ${allTime ? 'translate-x-6' : 'translate-x-1'}`} />
                      </button>
                    </div>
                  </div>
                }
              />
            </div>
          </div>
        </AnimationWrapper>

        {/* =====================================================================
            SECTION 4: INDIVIDUAL APPLIANCE CHARTS
            ===================================================================== */}
        <AnimationWrapper variant="slide-up" delay={0.3}>
          <h2 className="text-heading-md text-surface-700 mb-4 flex items-center gap-2">
            <svg className="w-5 h-5 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            Appliance Breakdown
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6" id="tour-appliance-breakdown">
            {APPLIANCES.map((appliance) => {
              const appData = calculations.applianceData[appliance];
              const applianceActual = chartData.prevActualData.map((val, i) => {
                if (val === null) return null;
                const proportion = appData.kwh / (calculations.nextTotal || 1);
                return val * proportion;
              });
              const applianceForecast = [...applianceActual.slice(0, labels.prevPoints), ...appData.data];

              return (
                <EnergyLineChart
                  key={appliance}
                  title={appliance}
                  subtitle="Energy consumption"
                  icon={ApplianceIcons[appliance] || ApplianceIcons.Default}
                  labels={[...labels.prevLabels, ...labels.nextLabels]}
                  actualData={[...applianceActual, ...Array(labels.nextPoints).fill(null)]}
                  forecastData={applianceForecast}
                  height={220}
                  extraAction={
                    <div className="text-right">
                      <p className="text-heading-sm font-bold text-surface-900 tabular-nums">{appData.kwh.toFixed(2)} kWh</p>
                      <p className="text-caption text-surface-500">₱{appData.php.toFixed(2)}</p>
                    </div>
                  }
                />
              );
            })}
          </div>
        </AnimationWrapper>

        {/* =====================================================================
            SECTION 5: CONTROLS & CONSUMPTION RANKING
            ===================================================================== */}
        <AnimationWrapper variant="slide-up" delay={0.4}>
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
              forecastHorizon={forecastHorizon}
              onHistoryChange={setSelectedLookback}
              onForecastChange={setSelectedPeriod}
              onTariffChange={setTariff}
              onBudgetChange={setBudget}
              onHorizonChange={setForecastHorizon}
              containerId="tour-controls"
            />
            <div id="tour-ranking" className="h-full">
              <ConsumptionRanking appliances={calculations.appliances} />
            </div>
          </div>
        </AnimationWrapper>

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

function App() {
  return (
    <DashboardProvider>
      <DashboardContent />
    </DashboardProvider>
  );
}

export default App;
