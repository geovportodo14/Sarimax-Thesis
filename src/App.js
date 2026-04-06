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
import SmartBudgetCard from './components/SmartBudgetCard';
import SettingsPopover from './components/SettingsPopover';
import MonthlyApplianceSummaryModal from './components/MonthlyApplianceSummaryModal';

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
  const formatMonthKey = (date) => (
    new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Manila' }).format(date).slice(0, 7)
  );

  const {
    selectedPeriod,
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
  const [prevDayData, setPrevDayData] = useState({ aggregate_total_kwh: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const hasInitialData = useRef(false);
  const [recommendedBudgetDraft, setRecommendedBudgetDraft] = useState(null);
  const [showMonthlySummaryModal, setShowMonthlySummaryModal] = useState(false);
  const [monthlyApplianceSummary, setMonthlyApplianceSummary] = useState({
    month: null,
    total_kwh: 0,
    appliance_totals_kwh: { aircon: 0, refrigerator: 0, electricfan: 0 }
  });
  const [loadingMonthlyApplianceSummary, setLoadingMonthlyApplianceSummary] = useState(false);
  const [selectedSummaryMonth, setSelectedSummaryMonth] = useState(() => formatMonthKey(new Date()));
  const [monthlySummaryError, setMonthlySummaryError] = useState('');
  const [monthlyRefreshTick, setMonthlyRefreshTick] = useState(0);

  // --- MANILA TIMEZONE HELPERS ---
  const isToday = useMemo(() => {
    const todayStr = new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Manila' }).format(new Date());
    const selectedStr = new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Manila' }).format(currentDate);
    return todayStr === selectedStr;
  }, [currentDate]);

  // Fetch True MongoDB Data
  useEffect(() => {
    const fetchDashboardData = async () => {
      // Only show full loading spinner on the very first load
      if (!hasInitialData.current) {
        setLoading(true);
      }
      setError(null);
      try {
        const dateStr = new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Manila' }).format(currentDate);
        let endpoint = '';

        if (isToday) {
          endpoint = getApiUrl(`/api/live?horizon=${selectedPeriod}&granularity=${granularity}`);
        } else {
          endpoint = getApiUrl(`/api/historical?date=${dateStr}&granularity=${granularity}`);
        }

        // Also fetch previous day data for accurate Period Comparison
        const prevDate = new Date(currentDate);
        prevDate.setDate(prevDate.getDate() - 1);
        const prevDateStr = new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Manila' }).format(prevDate);
        const prevEndpoint = getApiUrl(`/api/historical?date=${prevDateStr}&granularity=${granularity}`);

        const [response, prevResponse] = await Promise.all([
          fetch(endpoint),
          fetch(prevEndpoint)
        ]);

        const result = await response.json();
        const prevResult = await prevResponse.json();

        if (response.ok) {
          setChartData(result);
          hasInitialData.current = true;
        } else {
          throw new Error(result.error || "Failed to fetch backend data");
        }

        if (prevResponse.ok) {
          setPrevDayData(prevResult);
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

  const currentMonthKey = formatMonthKey(new Date());

  const fetchMonthlyTotalsFromHistorical = useCallback(async (monthKey) => {
    if (!monthKey) return null;
    const [yearStr, monthStr] = monthKey.split('-');
    const year = Number(yearStr);
    const month = Number(monthStr);
    if (!Number.isFinite(year) || !Number.isFinite(month)) return null;

    const todayStr = new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Manila' }).format(new Date());
    const todayMonthKey = todayStr.slice(0, 7);
    const todayDay = Number(todayStr.slice(8, 10));
    const lastDay = new Date(year, month, 0).getDate();
    const endDay = monthKey === todayMonthKey ? Math.min(todayDay, lastDay) : lastDay;

    const totals = { aircon: 0, refrigerator: 0, electricfan: 0 };
    let hadAnyDailyPayload = false;

    for (let day = 1; day <= endDay; day += 1) {
      const dateStr = `${monthKey}-${String(day).padStart(2, '0')}`;
      try {
        const dailyRes = await fetch(getApiUrl(`/api/historical?date=${dateStr}&granularity=60`));
        if (!dailyRes.ok) continue;
        const daily = await dailyRes.json();
        const appTotals = daily?.appliance_totals_kwh || daily?.appliance_totals;

        if (appTotals) {
          hadAnyDailyPayload = true;
          totals.aircon += Number(appTotals.aircon || 0);
          totals.refrigerator += Number(appTotals.refrigerator || 0);
          totals.electricfan += Number(appTotals.electricfan || 0);
          continue;
        }

        // Legacy safety: derive appliance totals from time-series breakdown if aggregate fields are absent.
        if (Array.isArray(daily?.data) && daily.data.length > 0) {
          let dayAircon = 0;
          let dayRefrigerator = 0;
          let dayElectricfan = 0;
          daily.data.forEach((point) => {
            dayAircon += Number(point?.breakdown?.aircon?.actual || 0);
            dayRefrigerator += Number(point?.breakdown?.refrigerator?.actual || 0);
            dayElectricfan += Number(point?.breakdown?.electricfan?.actual || 0);
          });
          if ((dayAircon + dayRefrigerator + dayElectricfan) > 0) {
            hadAnyDailyPayload = true;
            totals.aircon += dayAircon;
            totals.refrigerator += dayRefrigerator;
            totals.electricfan += dayElectricfan;
          }
        }
      } catch (err) {
        console.warn(`Monthly fallback failed for ${dateStr}:`, err);
      }
    }

    if (!hadAnyDailyPayload) return null;

    return {
      month: monthKey,
      appliance_totals_kwh: {
        aircon: Number(totals.aircon.toFixed(4)),
        refrigerator: Number(totals.refrigerator.toFixed(4)),
        electricfan: Number(totals.electricfan.toFixed(4))
      }
    };
  }, []);

  const applyMonthlySummaryResult = useCallback((monthKey, payload) => {
    const normalizedTotals = {
      aircon: Number(payload?.appliance_totals_kwh?.aircon || 0),
      refrigerator: Number(payload?.appliance_totals_kwh?.refrigerator || 0),
      electricfan: Number(payload?.appliance_totals_kwh?.electricfan || 0)
    };
    const computedTotal = normalizedTotals.aircon + normalizedTotals.refrigerator + normalizedTotals.electricfan;
    setMonthlyApplianceSummary({
      month: payload?.month || monthKey,
      total_kwh: Number(computedTotal.toFixed(4)),
      appliance_totals_kwh: normalizedTotals
    });
  }, []);

  // Keep ongoing month dynamic (MTD): refresh periodically while viewing current month
  useEffect(() => {
    if (selectedSummaryMonth !== currentMonthKey) return undefined;
    const intervalId = window.setInterval(() => {
      setMonthlyRefreshTick((v) => v + 1);
    }, 60 * 1000);
    return () => window.clearInterval(intervalId);
  }, [selectedSummaryMonth, currentMonthKey]);

  useEffect(() => {
    const fetchMonthlyApplianceSummary = async () => {
      if (!selectedSummaryMonth) return;
      setLoadingMonthlyApplianceSummary(true);
      setMonthlySummaryError('');
      try {
        const endpoint = getApiUrl(`/api/summary/month?date=${selectedSummaryMonth}`);
        const response = await fetch(endpoint);
        const result = await response.json();
        if (response.ok) {
          if (result.appliance_totals_kwh) {
            applyMonthlySummaryResult(selectedSummaryMonth, result);
          } else {
            const fallbackPayload = await fetchMonthlyTotalsFromHistorical(selectedSummaryMonth);
            if (fallbackPayload) {
              applyMonthlySummaryResult(selectedSummaryMonth, fallbackPayload);
            } else {
              setMonthlySummaryError('Monthly API payload is missing appliance breakdown and fallback daily data is unavailable.');
            }
          }
        } else {
          const fallbackPayload = await fetchMonthlyTotalsFromHistorical(selectedSummaryMonth);
          if (fallbackPayload) {
            applyMonthlySummaryResult(selectedSummaryMonth, fallbackPayload);
          } else {
            setMonthlySummaryError(result?.error || `Monthly summary request failed (${response.status}).`);
          }
        }
      } catch (err) {
        console.error("Monthly appliance summary fetch failed:", err);
        const fallbackPayload = await fetchMonthlyTotalsFromHistorical(selectedSummaryMonth);
        if (fallbackPayload) {
          applyMonthlySummaryResult(selectedSummaryMonth, fallbackPayload);
        } else {
          setMonthlySummaryError(err?.message || 'Monthly summary request failed.');
        }
      } finally {
        setLoadingMonthlyApplianceSummary(false);
      }
    };

    fetchMonthlyApplianceSummary();
  }, [selectedSummaryMonth, fetchMonthlyTotalsFromHistorical, applyMonthlySummaryResult, monthlyRefreshTick]);


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

    // Keep full timeline visible; forecast window is controlled by selectedPeriod.
    const currentGranularity = chartData.granularity || granularity || 60;
    const visibleData = chartData.data;

    // current_bucket_index tells us where "now" is in the data array.
    // For historical dates the field is absent (-1 sentinel = include all).
    // For today's live data we only count forecasts AFTER this index to
    // avoid double-counting hours that already have actuals.
    const currentBucketIndex = chartData.current_bucket_index ?? -1;

    const labels = visibleData.map(d => d.timestamp);
    const actuals = visibleData.map(d => d.actual_kwh);
    const forecasts = visibleData.map(d => d.forecast_kwh);

    const maxForecastBuckets = Math.floor((selectedPeriod * 60) / currentGranularity);

    // Sum only future-bucket forecasts (i > currentBucketIndex up to selected period limits)
    const totalForecastedKwh = forecasts.reduce((sum, val, i) => {
      if (i <= currentBucketIndex || i > currentBucketIndex + maxForecastBuckets) return sum;
      return sum + (val || 0);
    }, 0);

    const airconActuals = visibleData.map(d => d.breakdown?.aircon?.actual ?? null);
    const airconForecasts = visibleData.map(d => d.breakdown?.aircon?.forecast ?? null);
    const fridgeActuals = visibleData.map(d => d.breakdown?.refrigerator?.actual ?? null);
    const fridgeForecasts = visibleData.map(d => d.breakdown?.refrigerator?.forecast ?? null);
    const fanActuals = visibleData.map(d => d.breakdown?.electricfan?.actual ?? null);
    const fanForecasts = visibleData.map(d => d.breakdown?.electricfan?.forecast ?? null);

    // Projected totals: only future buckets bounded by selectedPeriod
    const projAircon = airconForecasts.reduce((sum, v, i) => {
      if (i <= currentBucketIndex || i > currentBucketIndex + maxForecastBuckets) return sum;
      return sum + (v || 0);
    }, 0);
    const projFridge = fridgeForecasts.reduce((sum, v, i) => {
      if (i <= currentBucketIndex || i > currentBucketIndex + maxForecastBuckets) return sum;
      return sum + (v || 0);
    }, 0);
    const projFan = fanForecasts.reduce((sum, v, i) => {
      if (i <= currentBucketIndex || i > currentBucketIndex + maxForecastBuckets) return sum;
      return sum + (v || 0);
    }, 0);

    return {
      labels, actuals, forecasts, totalForecastedKwh,
      airconActuals, airconForecasts, projAircon,
      fridgeActuals, fridgeForecasts, projFridge,
      fanActuals, fanForecasts, projFan
    };
  }, [chartData, selectedPeriod, granularity]);

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

    const appliances = [
      {
        name: 'Air Conditioner',
        kwh: (applianceTotals.aircon + processedChartData.projAircon) * loadMultiplier,
        php: (applianceTotals.aircon + processedChartData.projAircon) * loadMultiplier * effectiveTariff
      },
      {
        name: 'Refrigerator',
        kwh: (applianceTotals.refrigerator + processedChartData.projFridge) * loadMultiplier,
        php: (applianceTotals.refrigerator + processedChartData.projFridge) * loadMultiplier * effectiveTariff
      },
      {
        name: 'Electric Fan',
        kwh: (applianceTotals.electricfan + processedChartData.projFan) * loadMultiplier,
        php: (applianceTotals.electricfan + processedChartData.projFan) * loadMultiplier * effectiveTariff
      },
    ];

    const applianceData = {
      'Air Conditioner': {
        data: processedChartData.airconActuals,
        forecast: processedChartData.airconForecasts,
        kwh: appliances[0].kwh,
        php: appliances[0].php
      },
      'Refrigerator': {
        data: processedChartData.fridgeActuals,
        forecast: processedChartData.fridgeForecasts,
        kwh: appliances[1].kwh,
        php: appliances[1].php
      },
      'Electric Fan': {
        data: processedChartData.fanActuals,
        forecast: processedChartData.fanForecasts,
        kwh: appliances[2].kwh,
        php: appliances[2].php
      }
    };

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
      applianceData
    };
  }, [tariff, budget, isScenarioMode, scenarioParams, chartData, processedChartData, selectedPeriod]);

  const monthlyApplianceCards = useMemo(() => {
    const totals = monthlyApplianceSummary?.appliance_totals_kwh || { aircon: 0, refrigerator: 0, electricfan: 0 };
    const rows = [
      { key: 'aircon', label: 'Air Conditioner', kwh: Number(totals.aircon || 0) },
      { key: 'refrigerator', label: 'Refrigerator', kwh: Number(totals.refrigerator || 0) },
      { key: 'electricfan', label: 'Electric Fan', kwh: Number(totals.electricfan || 0) }
    ];
    const totalMonthKwh = rows.reduce((sum, row) => sum + row.kwh, 0);

    return rows.map((row) => {
      const share = totalMonthKwh > 0 ? (row.kwh / totalMonthKwh) * 100 : 0;
      const estCost = row.kwh * tariff;
      return {
        ...row,
        share,
        estCost
      };
    });
  }, [monthlyApplianceSummary, tariff]);
  const monthlyTotalKwh = useMemo(
    () => monthlyApplianceCards.reduce((sum, row) => sum + Number(row.kwh || 0), 0),
    [monthlyApplianceCards]
  );

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

  const handleApplyRecommendedBudget = (recommendedBudget) => {
    if (!Number.isFinite(recommendedBudget) || recommendedBudget <= 0) return;
    setRecommendedBudgetDraft({ value: recommendedBudget, ts: Date.now() });
    const controls = document.getElementById('tour-controls');
    if (controls) {
      controls.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
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
                prevKwh={prevDayData.aggregate_total_kwh || 0}
                prevPhp={(prevDayData.aggregate_total_kwh || 0) * tariff}
                actualKwh={chartData.aggregate_total_kwh || 0}
                actualPhp={(chartData.aggregate_total_kwh || 0) * tariff}
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

            {/* ── Smart Daily Budget Recommendation ── */}
            <AnimationWrapper variant="fade-in" delay={0.05}>
              <SmartBudgetCard
                forecastKwh={calculations.totalKwh}
                tariff={tariff}
                onApplyBudget={handleApplyRecommendedBudget}
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

              <div className="mb-6">
                <Card className="border border-cyan-100 bg-gradient-to-br from-cyan-50 via-white to-sky-50">
                  <CardBody className="p-5">
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                      <div>
                        <p className="text-[11px] font-bold uppercase tracking-widest text-cyan-700 mb-1">Monthly Appliance Summary</p>
                        <p className="text-body-md font-semibold text-surface-900">
                          {selectedSummaryMonth} total: {monthlyTotalKwh.toFixed(2)} kWh
                        </p>
                        <p className="text-caption text-surface-500 mt-1">
                          {loadingMonthlyApplianceSummary
                            ? 'Refreshing monthly totals...'
                            : 'Open detailed monthly breakdown with month picker and per-appliance insights.'}
                        </p>
                        {selectedSummaryMonth === currentMonthKey && (
                          <p className="text-caption text-emerald-700 mt-1">
                            Month-to-date mode: updates automatically as new daily readings arrive.
                          </p>
                        )}
                        {!!monthlySummaryError && (
                          <p className="text-caption text-red-600 mt-1">
                            {monthlySummaryError}
                          </p>
                        )}
                      </div>
                      <button
                        onClick={() => setShowMonthlySummaryModal(true)}
                        className="w-full sm:w-auto px-4 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-700 text-white text-body-sm font-semibold transition-colors shadow-sm"
                      >
                        View Monthly Breakdown
                      </button>
                    </div>
                  </CardBody>
                </Card>
              </div>

              <div id="tour-comparison">
                <ComparisonChart
                  previousKwh={prevDayData.aggregate_total_kwh || 0}
                  previousCost={(prevDayData.aggregate_total_kwh || 0) * tariff}
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
                      showSlider={true}
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
                  forecastPeriod={selectedPeriod}
                  disabledForecast={!isToday}
                  tariff={tariff}
                  budget={budget}
                  recommendedBudget={Math.round(calculations.totalKwh * tariff)}
                  recommendedBudgetDraft={recommendedBudgetDraft}
                  onForecastChange={(val) => { if (isToday) setSelectedPeriod(val); }}
                  onTariffChange={handleTariffChange}
                  onBudgetChange={handleBudgetChange}
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

      <MonthlyApplianceSummaryModal
        isOpen={showMonthlySummaryModal}
        onClose={() => setShowMonthlySummaryModal(false)}
        selectedMonth={selectedSummaryMonth}
        onMonthChange={setSelectedSummaryMonth}
        maxMonth={currentMonthKey}
        loading={loadingMonthlyApplianceSummary}
        error={monthlySummaryError}
        applianceCards={monthlyApplianceCards}
        totalKwh={monthlyTotalKwh}
        tariff={tariff}
      />
    </div>
  );
}

function App() {
  const [showDashboard, setShowDashboard] = useState(false);
  const [monthlySummary, setMonthlySummary] = useState(null);
  const [loadingSummary, setLoadingSummary] = useState(true);

  useEffect(() => {
    // Fetch real MTD summary for the Landing Page
    const fetchSummary = async () => {
      try {
        const res = await fetch(getApiUrl('/api/summary/month'));
        if (res.ok) {
          const data = await res.json();
          setMonthlySummary(data);
        }
      } catch (err) {
        console.error("Failed to fetch monthly summary for landing page:", err);
      } finally {
        setLoadingSummary(false);
      }
    };
    fetchSummary();
  }, []);

  if (!showDashboard) {
    return <LandingPage
      onEnterDashboard={() => setShowDashboard(true)}
      monthlySummary={monthlySummary}
      loadingSummary={loadingSummary}
    />;
  }

  return (
    <DashboardProvider>
      <DashboardContent />
    </DashboardProvider>
  );
}

export default App;
