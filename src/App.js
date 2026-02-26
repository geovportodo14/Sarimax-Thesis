import React, { useMemo, useEffect, useRef, useState, useCallback } from 'react';
import DashboardHeader from './components/DashboardHeader';
import DesktopSidebar from './components/DesktopSidebar';
import ForecastControls from './components/ForecastControls';
import ConsumptionRanking from './components/ConsumptionRanking';
import EnergyForecastSummary from './components/EnergyForecastSummary';
import DateNavigator from './components/DateNavigator';
import { Card, CardBody, Skeleton, Select } from './components/ui/index';
import IntroductionModal from './components/onboarding/IntroductionModal';
import GuidedTour from './components/onboarding/GuidedTour';
import OnboardingModal from './components/onboarding/OnboardingModal';
import { DashboardProvider, useDashboard } from './context/DashboardContext';
import { AnimationWrapper } from './components/ui/AnimationWrapper';
import ScenarioControls from './components/ScenarioControls';
import ComparisonChart from './components/ui/ComparisonChart';
import { RefreshCw, Bell } from 'lucide-react';
import NotificationPopover from './components/NotificationPopover';
import SettingsPopover from './components/SettingsPopover';

import { ApplianceIcons } from './components/ui/icons';
import EnergyLineChart from './components/ui/EnergyLineChart';
import { getApiUrl } from './utils/api';

import LandingPage from './pages/LandingPage';

function LoadingState() {
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

function DashboardContent() {
  const {
    selectedPeriod,
    selectedLookback,
    tariff,
    budget,
    hasSetBudget,
    allTime,
    currentDate,
    showIntroduction,
    runTour,
    settings,
    notifications,

    setSelectedPeriod,
    setSelectedLookback,
    setTariff,
    handleBudgetChange,
    handleTariffChange,
    setAllTime,
    setNotifications,

    handleSkipIntroduction,
    handleStartTour,
    handleTourComplete,
    handleSaveSettings,

    isScenarioMode,
    scenarioParams,
    forecastHorizon,
    setForecastHorizon,

    setActiveSection,
    isSidebarCollapsed,

    setCurrentDate,
    handlePrevDate,
    handleNextDate,

    showSettings,
    setShowSettings,
    showNotifications,
    setShowNotifications,

    handleTriggerSetup,
    granularity,
    setGranularity
  } = useDashboard();

  // --- LIVE API STATE ---
  const [chartData, setChartData] = useState({
    aggregate_total_kwh: 0,
    appliance_totals: { aircon: 0, refrigerator: 0, electricfan: 0 },
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
          endpoint = getApiUrl(`/api/live?horizon=${selectedPeriod}&granularity=${granularity}`);
        } else {
          endpoint = getApiUrl(`/api/historical?date=${dateStr}&granularity=${granularity}`);
        }

        const response = await fetch(endpoint);
        const result = await response.json();

        if (response.ok) {
          setChartData(result);
        } else {
          throw new Error(result.error || "Failed to fetch backend data");
        }
      } catch (err) {
        console.error("API Error:", err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [currentDate, selectedPeriod, isToday, granularity]);


  const toggleNotificationRead = (id) => {
    setNotifications(notifications.map(n => n.id === id ? { ...n, read: true } : n));
  };

  const clearAllNotifications = () => {
    setNotifications([]);
  };

  useEffect(() => {
    // ... (observer logic remains same)
  }, [setActiveSection]);

  const processedChartData = useMemo(() => {
    if (!chartData || !chartData.data) return { labels: [], actuals: [], forecasts: [] };

    const labels = chartData.data.map(d => d.timestamp);
    const actuals = chartData.data.map(d => d.actual_kwh);
    const forecasts = chartData.data.map(d => d.forecast_kwh);

    // Calculate sum of forecasts for the requested horizon
    const totalForecastedKwh = forecasts.reduce((sum, val) => sum + (val || 0), 0);

    const airconActuals = chartData.data.map(d => d.breakdown ? d.breakdown.aircon : null);
    const fridgeActuals = chartData.data.map(d => d.breakdown ? d.breakdown.refrigerator : null);
    const fanActuals = chartData.data.map(d => d.breakdown ? d.breakdown.electricfan : null);

    return { labels, actuals, forecasts, totalForecastedKwh, airconActuals, fridgeActuals, fanActuals };
  }, [chartData]);

  const calculations = useMemo(() => {
    let effectiveTariff = tariff;
    let loadMultiplier = 1;

    if (isScenarioMode) {
      effectiveTariff = scenarioParams.tariffAdjustment;
      loadMultiplier = 1 + (scenarioParams.loadAdjustment / 100);
    }

    const actualSoFarKwh = (chartData.aggregate_total_kwh || 0);
    const projectedUpcomingKwh = processedChartData.totalForecastedKwh || 0;

    // Total Kwh = Actual today + Future forecasted window
    const totalKwh = (actualSoFarKwh + projectedUpcomingKwh) * loadMultiplier;
    const currentCost = totalKwh * effectiveTariff;

    const applianceTotals = chartData.appliance_totals_kwh || { aircon: 0, refrigerator: 0, electricfan: 0 };

    // Calculate distribution weights based on actuals so far
    const airconWeight = actualSoFarKwh > 0 ? (applianceTotals.aircon / actualSoFarKwh) : 0.55;
    const fridgeWeight = actualSoFarKwh > 0 ? (applianceTotals.refrigerator / actualSoFarKwh) : 0.25;
    const fanWeight = actualSoFarKwh > 0 ? (applianceTotals.electricfan / actualSoFarKwh) : 0.20;

    const appliances = [
      {
        name: 'Air Conditioner',
        kwh: (applianceTotals.aircon + (projectedUpcomingKwh * airconWeight)) * loadMultiplier,
        php: (applianceTotals.aircon + (projectedUpcomingKwh * airconWeight)) * loadMultiplier * effectiveTariff
      },
      {
        name: 'Refrigerator',
        kwh: (applianceTotals.refrigerator + (projectedUpcomingKwh * fridgeWeight)) * loadMultiplier,
        php: (applianceTotals.refrigerator + (projectedUpcomingKwh * fridgeWeight)) * loadMultiplier * effectiveTariff
      },
      {
        name: 'Electric Fan',
        kwh: (applianceTotals.electricfan + (projectedUpcomingKwh * fanWeight)) * loadMultiplier,
        php: (applianceTotals.electricfan + (projectedUpcomingKwh * fanWeight)) * loadMultiplier * effectiveTariff
      },
    ];

    const maxPhp = Math.max(...appliances.map(a => a.php));
    const topApplianceObj = appliances.find(a => a.php === maxPhp);
    const topAppliance = topApplianceObj ? topApplianceObj.name : 'None';

    const budgetStatus = currentCost < budget ? 'OK' : 'At-Risk';

    const selectedPeriodText =
      selectedPeriod === 1 ? 'Next 1 Hour' :
        selectedPeriod === 4 ? 'Next 4 Hours' :
          selectedPeriod === 8 ? 'Next 8 Hours' : 'Next 24 Hours';

    return {
      totalKwh,
      currentCost,
      appliances,
      topAppliance,
      budgetStatus,
      selectedPeriodText,
      applianceData: {
        'Air Conditioner': {
          kwh: applianceTotals.aircon,
          php: applianceTotals.aircon * effectiveTariff,
          data: processedChartData.airconActuals,
          forecast: processedChartData.forecasts.map(f => f !== null ? f * 0.55 : null) // Using 55% as predicted weight for AC
        },
        'Refrigerator': {
          kwh: applianceTotals.refrigerator,
          php: applianceTotals.refrigerator * effectiveTariff,
          data: processedChartData.fridgeActuals,
          forecast: processedChartData.forecasts.map(f => f !== null ? f * 0.25 : null)
        },
        'Electric Fan': {
          kwh: applianceTotals.electricfan,
          php: applianceTotals.electricfan * effectiveTariff,
          data: processedChartData.fanActuals,
          forecast: processedChartData.forecasts.map(f => f !== null ? f * 0.20 : null)
        }
      },
    };
  }, [chartData.aggregate_total_kwh, chartData.appliance_totals, processedChartData, tariff, budget, selectedPeriod, isScenarioMode, scenarioParams]);

  const lastEmailSent = useRef({ type: null, timestamp: 0 });

  useEffect(() => {
    if (loading || !settings.emailEnabled || !settings.emailAddress) return;

    const budgetUsagePercent = Math.round((calculations.currentCost / budget) * 100);
    const now = Date.now();
    const COOLDOWN = 4 * 60 * 60 * 1000;

    let alertType = null;
    if (budgetUsagePercent >= settings.thresholdCritical) {
      alertType = 'critical';
    } else if (budgetUsagePercent >= settings.thresholdApproaching) {
      alertType = 'warning';
    }

    if (alertType && (lastEmailSent.current.type !== alertType || (now - lastEmailSent.current.timestamp) > COOLDOWN)) {
      const sendEmailAlert = async () => {
        try {
          await fetch(getApiUrl('/api/alerts/threshold'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              email: settings.emailAddress,
              usage_percent: budgetUsagePercent,
              budget: budget,
              cost: calculations.currentCost
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

    const newNotifications = [];
    if (budgetUsagePercent >= settings.thresholdCritical) {
      newNotifications.push({
        id: 'budget-critical',
        type: 'at-risk',
        priority: 'high',
        title: 'Budget Exceeded!',
        message: `Your forecasted spend (${settings.currency === 'PHP' ? '₱' : '$'}${Math.round(calculations.currentCost)}) exceeds your budget limit.`,
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
  }, [calculations.currentCost, budget, settings, loading, setNotifications]);

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
    window.setTimeout(() => {
      const input = document.getElementById('budget-input');
      if (input && typeof input.focus === 'function') input.focus();
    }, 250);
  };

  if (loading) {
    return <LoadingState />;
  }

  return (
    <div className="min-h-screen bg-transparent">
      {/* ── Desktop Floating Header ── */}
      <div className="fixed top-6 right-8 z-[100] hidden lg:flex items-center gap-6 bg-white/95 backdrop-blur-md px-4 py-2 rounded-full shadow-md border border-gray-100">
        <div className="flex items-center gap-4 border-r border-gray-200 pr-4">
          <div className="relative">
            <Bell
              className="w-5 h-5 text-gray-600 cursor-pointer hover:text-primary-600 transition-colors"
              onClick={() => setShowNotifications(!showNotifications)}
            />
            {notifications.some(n => !n.read) && (
              <span className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-red-500 border-2 border-white rounded-full" />
            )}
            <NotificationPopover
              isOpen={showNotifications}
              onClose={() => setShowNotifications(false)}
              notifications={notifications}
              onToggleRead={toggleNotificationRead}
              onClearAll={clearAllNotifications}
            />
          </div>
          <RefreshCw
            className="w-5 h-5 text-gray-600 cursor-pointer hover:text-primary-600 transition-colors"
            onClick={() => window.location.reload()}
          />
        </div>

        <div className="relative">
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="flex items-center gap-3 hover:bg-surface-50 transition-all px-1 py-1 rounded-full"
          >
            <div className="text-right hidden xl:block pl-2">
              <p className="text-[11px] font-bold text-surface-900 leading-tight">Geovanny Portodo</p>
            </div>
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center text-white text-[11px] font-bold shadow-sm">
              GP
            </div>
          </button>
          <SettingsPopover
            isOpen={showSettings}
            onClose={() => setShowSettings(false)}
            settings={settings}
            onSave={(newSettings) => {
              handleSaveSettings(newSettings);
              setShowSettings(false);
            }}
          />
        </div>
      </div>

      <div className="flex min-h-screen bg-transparent">
        <DesktopSidebar
          onHelpClick={handleStartTour}
        />

        <main className={`flex-1 transition-all duration-300 min-w-0 ${isSidebarCollapsed ? 'lg:pl-20' : 'lg:pl-64'} pt-0 lg:pt-24`}>
          <DashboardHeader
            onHelpClick={handleStartTour}
            settings={settings}
            onSaveSettings={handleSaveSettings}
            notifications={notifications}
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

          <OnboardingModal />

          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8 space-y-8">
            <AnimationWrapper variant="slideDown" className="mb-8" id="tour-scenario">
              <ScenarioControls />
            </AnimationWrapper>

            <AnimationWrapper variant="fade-in" id="tour-summary">
              <EnergyForecastSummary
                nextKwh={calculations.totalKwh}
                nextPhp={calculations.currentCost}
                prevKwh={calculations.totalKwh * 0.9} // Simple mockup reference for previous period comparisons
                prevPhp={(calculations.totalKwh * 0.9) * tariff}
                actualKwh={calculations.totalKwh}
                actualPhp={calculations.currentCost}
                topAppliance={calculations.topAppliance}
                budgetStatus={calculations.budgetStatus}
                selectedPeriodText={calculations.selectedPeriodText}
                budget={budget}
                hasSetBudget={hasSetBudget}
                onViewDetails={handleViewDetails}
                onSetBudget={handleSetBudget}
                thresholdApproaching={settings.thresholdApproaching}
                thresholdCritical={settings.thresholdCritical}
              />
            </AnimationWrapper>

            <AnimationWrapper variant="slide-up" delay={0.1}>
              <h2 className="text-heading-md text-surface-700 mb-4 flex items-center gap-2">
                <svg className="w-5 h-5 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                Today at a Glance
              </h2>

              <div className="grid grid-cols-2 gap-3 lg:grid-cols-4 lg:gap-4 mb-6">
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
                  previousKwh={calculations.totalKwh * 0.9}
                  previousCost={(calculations.totalKwh * 0.9) * tariff}
                  forecastKwh={calculations.totalKwh}
                  forecastCost={calculations.currentCost}
                />
              </div>

              <DateNavigator
                selectedDate={currentDate}
                onDateChange={setCurrentDate}
                onPrevClick={handlePrevDate}
                onNextClick={handleNextDate}
              />
            </AnimationWrapper>

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
                    subtitle="Total energy consumption comparison (kW Demand)"
                    icon={
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                      </svg>
                    }
                    labels={processedChartData.labels}
                    actualData={processedChartData.actuals}
                    forecastData={processedChartData.forecasts}
                    riskStatus={calculations.budgetStatus}
                    extraAction={
                      <div className="flex items-center gap-2">
                        <span className="text-caption font-medium text-surface-400 uppercase tracking-wider">Granularity:</span>
                        <Select
                          value={granularity}
                          onChange={(e) => setGranularity(parseInt(e.target.value))}
                          options={[
                            { value: 10, label: '10 Min' },
                            { value: 30, label: '30 Min' },
                            { value: 60, label: '1 Hour' },
                          ]}
                          size="sm"
                          selectClassName="min-w-[100px] bg-surface-50 border-surface-200"
                        />
                      </div>
                    }
                    unit="kWh"
                    showSlider={true}
                  />
                </div>
              </div>
            </AnimationWrapper>

            <AnimationWrapper variant="slide-up" delay={0.3}>
              <h2 className="text-heading-md text-surface-700 mb-4 flex items-center gap-2">
                <svg className="w-5 h-5 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                Appliance Breakdown
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6" id="tour-appliance-breakdown">
                {['Electric Fan', 'Air Conditioner', 'Refrigerator'].map((appliance) => {
                  const appData = calculations.applianceData[appliance];

                  return (
                    <EnergyLineChart
                      key={appliance}
                      title={appliance}
                      subtitle="Energy consumption"
                      icon={ApplianceIcons[appliance] || ApplianceIcons.Default}
                      labels={processedChartData.labels}
                      actualData={appData.data}
                      forecastData={appData.forecast}
                      height={220}
                      unit="kWh"
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
                  disabledForecast={!isToday}
                  tariff={tariff}
                  budget={budget}
                  granularity={granularity}
                  forecastHorizon={forecastHorizon}
                  onHistoryChange={setSelectedLookback}
                  onForecastChange={setSelectedPeriod}
                  onTariffChange={handleTariffChange}
                  onBudgetChange={handleBudgetChange}
                  onGranularityChange={setGranularity}
                  onHorizonChange={setForecastHorizon}
                  containerId="tour-controls"
                />
                <div id="tour-ranking" className="h-full">
                  <ConsumptionRanking appliances={calculations.appliances} />
                </div>
              </div>
            </AnimationWrapper>

            <footer className="text-center py-6 border-t border-surface-100 flex flex-col items-center gap-3">
              <p className="text-body-sm text-surface-400">
                Energy Forecast Dashboard • Powered by SARIMAX Model
              </p>
              <button
                onClick={handleTriggerSetup}
                className="text-body-sm font-medium text-surface-500 hover:text-primary-600 transition-colors underline decoration-surface-300 hover:decoration-primary-600 underline-offset-4"
              >
                Reset Setup Wizard Tour
              </button>
            </footer>
          </div>
        </main>
      </div>
    </div>
  );
}

function App() {
  const [showDashboard, setShowDashboard] = useState(false);

  if (!showDashboard) {
    return <LandingPage onEnterDashboard={() => setShowDashboard(true)} />;
  }

  return (
    <DashboardProvider>
      <DashboardContent />
    </DashboardProvider>
  );
}

export default App;
