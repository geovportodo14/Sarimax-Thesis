<<<<<<< Updated upstream
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { DashboardProvider } from './context/DashboardContext';

// Pages
import LandingPage from './pages/LandingPage';
import HowItWorksPage from './pages/HowItWorksPage';
import TariffSetupPage from './pages/TariffSetupPage';
import DeviceSetupPage from './pages/DeviceSetupPage';
import DashboardPage from './pages/DashboardPage';
import ForecastPage from './pages/ForecastPage';
import BudgetPage from './pages/BudgetPage';
import ScenariosPage from './pages/ScenariosPage';
=======
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
import LearningStateBanner from './components/onboarding/LearningStateBanner';
// import SectionTabs from './components/ui/SectionTabs'; // Removed as per request

import Sidebar from './components/layout/Sidebar';
import ApplianceAnalytics from './components/ApplianceAnalytics';
import UserGuideModal from './components/onboarding/UserGuideModal';

import { generateApplianceForecast, generateLabels, generateActual, generateForecastPast } from './utils/mockData';
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
    hasSetBudget,
    // allTime, // Removed unused
    currentDate,
    dummyData,
    loading,
    showIntroduction,
    runTour,
    settings,
    notifications,
    showGuide,
    setShowGuide,

    // Setters
    setSelectedPeriod,
    setSelectedLookback,
    setTariff,
    handleBudgetChange,
    // setAllTime, // Removed unused
    setCurrentDate, // Added if missing in previous context
    setNotifications,

    // Handlers
    handleSkipIntroduction,
    handleStartTour,
    handleTourComplete,
    // handleRevisitGuide, // Removed unused
    // guide handled locally below
    handlePrevDate,
    handleNextDate,
    handleSaveSettings,

    // Scenario Mode
    isScenarioMode,
    scenarioParams,

    // Forecast Horizon
    forecastHorizon,
    setForecastHorizon,

    // Data Sufficiency
    dataSufficiencyState
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

  const handleSetBudget = () => {
    const controls = document.getElementById('tour-controls');
    if (controls) {
      controls.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    // Focus the budget input after scroll
    window.setTimeout(() => {
      const input = document.getElementById('budget-input');
      if (input && typeof input.focus === 'function') input.focus();
    }, 250);
  };

  // Show loading state
  if (loading) {
    return <LoadingState />;
  }

  return (
    <div className="min-h-screen flex flex-col lg:flex-row">
      {/* Sidebar (Desktop Only) */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header - Stays sticky top, adjusted for sidebar offset if needed (but flex handles it) */}
        <DashboardHeader
          onHelpClick={() => setShowGuide(true)}
          notifications={notifications}
          settings={settings}
          onSaveSettings={handleSaveSettings}
        />

        <IntroductionModal
          isOpen={showIntroduction}
          onSkip={handleSkipIntroduction}
          onNext={handleStartTour}
        />

        <UserGuideModal
          isOpen={showGuide}
          onClose={() => setShowGuide(false)}
        />

        <GuidedTour
          run={runTour}
          onComplete={handleTourComplete}
        />

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8 space-y-8">

          {/* =====================================================================
            SECTION: LEARNING STATE BANNER
            ===================================================================== */}
          {dataSufficiencyState === 'learning' && (
            <AnimationWrapper variant="slideDown" className="mb-6">
              <LearningStateBanner progress={30} daysRemaining={3} />
            </AnimationWrapper>
          )}

          {/* =====================================================================
            SECTION: TABS (STICKY)
            ===================================================================== */}
          {/* =====================================================================
            SECTION: TABS (STICKY) - REMOVED
            ===================================================================== */}
          {/* <SectionTabs /> */}

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
              hasSetBudget={hasSetBudget}
              onViewDetails={handleViewDetails}
              onSetBudget={handleSetBudget}
              thresholdApproaching={settings.thresholdApproaching}
              thresholdCritical={settings.thresholdCritical}
              isLearning={dataSufficiencyState === 'learning'}
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
          <AnimationWrapper variant="slide-up" delay={0.2} id="charts-section">
            <EnergyLineChart
              title="Energy Forecast"
              subtitle="Actual vs Predicted Consumption"
              labels={[...labels.prevLabels, ...labels.nextLabels]}
              actualData={chartData.actualData}
              forecastData={chartData.forecastSeries}
              riskStatus={calculations.budgetStatus}
              unit="kWh"
            />
          </AnimationWrapper>


          {/* =====================================================================
            SECTION 4: INDIVIDUAL APPLIANCE CHARTS
            ===================================================================== */}
          <AnimationWrapper variant="slide-up" delay={0.3}>
            <h2 className="text-heading-md text-surface-700 mb-4 flex items-center gap-2">
              <svg className="w-5 h-5 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Appliance Analytics
            </h2>
            <div id="tour-appliance-breakdown">
              <ApplianceAnalytics
                calculations={calculations}
                chartData={chartData}
                tariff={tariff}
                labels={labels}
              />
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
                onBudgetChange={handleBudgetChange}
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
    </div>
  );
}
>>>>>>> Stashed changes

function App() {
  return (
    <BrowserRouter>
      <DashboardProvider>
        <Routes>
          {/* Onboarding */}
          <Route path="/welcome" element={<LandingPage />} />
          <Route path="/how-it-works" element={<HowItWorksPage />} />
          <Route path="/setup/tariff" element={<TariffSetupPage />} />
          <Route path="/setup/device" element={<DeviceSetupPage />} />

          {/* Main App */}
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/forecast" element={<ForecastPage />} />
          <Route path="/budget" element={<BudgetPage />} />
          <Route path="/scenarios" element={<ScenariosPage />} />

          {/* Default redirect */}
          <Route path="/" element={<Navigate to="/welcome" replace />} />
          <Route path="*" element={<Navigate to="/welcome" replace />} />
        </Routes>
      </DashboardProvider>
    </BrowserRouter>
  );
}

export default App;
