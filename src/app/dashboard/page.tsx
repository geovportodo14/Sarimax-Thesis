'use client';

import React, { useMemo, useEffect, useRef } from 'react';
import { DashboardProvider, useDashboard } from '@/context/legacy/DashboardContext';

import DashboardHeader from '@/components/legacy/DashboardHeader';
import ForecastControls from '@/components/legacy/ForecastControls';
import ConsumptionRanking from '@/components/legacy/ConsumptionRanking';
import EnergyForecastSummary from '@/components/legacy/EnergyForecastSummary';
import DateNavigator from '@/components/legacy/DateNavigator';
import { Card, CardBody, Skeleton } from '@/components/legacy/ui/index';
import IntroductionModal from '@/components/legacy/onboarding/IntroductionModal';
import GuidedTour from '@/components/legacy/onboarding/GuidedTour';
import { AnimationWrapper } from '@/components/legacy/ui/AnimationWrapper';
import ScenarioControls from '@/components/legacy/ScenarioControls';
import ComparisonChart from '@/components/legacy/ui/ComparisonChart';
import EnergyLineChart from '@/components/legacy/ui/EnergyLineChart';
import { ApplianceIcons } from '@/components/legacy/ui/icons';

import {
    APPLIANCES,
    generateApplianceForecast,
    generateLabels,
    generateActual,
    generateForecastPast
} from '@/lib/legacy/mockData';

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
// MAIN DASHBOARD CONTENT
// =============================================================================
function DashboardContent() {
    const {
        selectedPeriod,
        selectedLookback,
        tariff,
        budget,
        hasSetBudget,
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
        handleBudgetChange,
        setAllTime,
        setCurrentDate,
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
        if (loading || !dummyData) {
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
            v + (nextApplianceForecasts.ac[i] || 0) + (nextApplianceForecasts.ref[i] || 0)
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
        if (!chartData) return null;

        // Apply Scenario Logic
        let effectiveTariff = tariff;
        let loadMultiplier = 1;

        if (isScenarioMode) {
            effectiveTariff = scenarioParams.tariffAdjustment;
            loadMultiplier = 1 + (scenarioParams.loadAdjustment / 100);
        }

        const prevTotal = chartData.prevActualData.reduce((a, b) => (b || 0) + a, 0);
        const nextTotalBase = chartData.nextForecastData.reduce((a, b) => (b || 0) + a, 0);
        const nextTotal = nextTotalBase * loadMultiplier;

        const prevCost = prevTotal * tariff;
        const nextCost = nextTotal * effectiveTariff;

        const fanKwh = chartData.nextApplianceForecasts.fan.reduce((a, b) => a + b, 0) * loadMultiplier;
        const acKwh = chartData.nextApplianceForecasts.ac.reduce((a, b) => a + b, 0) * loadMultiplier;
        const refKwh = chartData.nextApplianceForecasts.ref.reduce((a, b) => a + b, 0) * loadMultiplier;

        const fanPhp = fanKwh * effectiveTariff;
        const acPhp = acKwh * effectiveTariff;
        const refPhp = refKwh * effectiveTariff;

        const appliances = [
            { name: 'Electric Fan', kwh: fanKwh, php: fanPhp },
            { name: 'Air Conditioner', kwh: acKwh, php: acPhp },
            { name: 'Refrigerator', kwh: refKwh, php: refPhp },
        ];

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
            applianceData: {
                'Electric Fan': { kwh: fanKwh, php: fanPhp, data: chartData.nextApplianceForecasts.fan.map(v => v * loadMultiplier) },
                'Air Conditioner': { kwh: acKwh, php: acPhp, data: chartData.nextApplianceForecasts.ac.map(v => v * loadMultiplier) },
                'Refrigerator': { kwh: refKwh, php: refPhp, data: chartData.nextApplianceForecasts.ref.map(v => v * loadMultiplier) },
            },
        };
    }, [chartData, tariff, budget, selectedPeriod, isScenarioMode, scenarioParams]);

    const lastEmailSent = useRef({ type: null, timestamp: 0 });

    useEffect(() => {
        if (loading || !settings.emailEnabled || !settings.emailAddress || !calculations) return;

        const budgetUsagePercent = Math.round((calculations.nextCost / budget) * 100);
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
                message: `Your forecasted spend exceeds your budget limit.`,
                time: 'Just now',
                action: 'Adjust Budget'
            });
        } else if (budgetUsagePercent >= settings.thresholdApproaching) {
            newNotifications.push({
                id: 'budget-approaching',
                type: 'approaching',
                priority: 'medium',
                title: 'Approaching Budget Limit',
                message: `You've reached ${budgetUsagePercent}% of your set energy budget.`,
                time: 'Just now',
                action: 'View Details'
            });
        }
        setNotifications(newNotifications);
    }, [calculations?.nextCost, budget, settings, loading]);

    const handleViewDetails = () => {
        const mainChart = document.getElementById('tour-main-chart');
        if (mainChart) mainChart.scrollIntoView({ behavior: 'smooth' });
    };

    const handleSetBudget = () => {
        const controls = document.getElementById('tour-controls');
        if (controls) controls.scrollIntoView({ behavior: 'smooth', block: 'start' });
        setTimeout(() => {
            const input = document.getElementById('budget-input');
            if (input) input.focus();
        }, 250);
    };

    if (loading || !calculations) return <LoadingState />;

    return (
        <div className="min-h-screen bg-transparent">
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

            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8 space-y-8">
                <AnimationWrapper variant="slideDown" className="mb-8" id="tour-scenario">
                    <ScenarioControls />
                </AnimationWrapper>

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
                    />
                </AnimationWrapper>

                <AnimationWrapper variant="slide-up" delay={0.1}>
                    <h2 className="text-heading-md text-surface-700 mb-4 flex items-center gap-2">
                        Today at a Glance
                    </h2>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
                        <Card>
                            <CardBody className="p-4">
                                <p className="text-caption text-surface-500">Current Rate</p>
                                <p className="text-heading-md text-surface-900 tabular-nums">₱{tariff.toFixed(2)}</p>
                                <p className="text-caption text-surface-400">per kWh</p>
                            </CardBody>
                        </Card>
                        <Card>
                            <CardBody className="p-4">
                                <p className="text-caption text-surface-500">Top Consumer</p>
                                <p className="text-body-md font-semibold text-surface-900 truncate">{calculations.topAppliance}</p>
                                <p className="text-caption text-surface-400">highest usage</p>
                            </CardBody>
                        </Card>
                        <Card>
                            <CardBody className="p-4">
                                <p className="text-caption text-surface-500">Budget</p>
                                <p className="text-heading-md text-surface-900 tabular-nums">₱{budget}</p>
                                <p className={`text-caption ${calculations.budgetStatus === 'OK' ? 'text-emerald-600' : 'text-red-600'}`}>
                                    {calculations.budgetStatus === 'OK' ? 'On track' : 'At risk'}
                                </p>
                            </CardBody>
                        </Card>
                        <Card>
                            <CardBody className="p-4">
                                <p className="text-caption text-surface-500">Forecast Period</p>
                                <p className="text-body-md font-semibold text-surface-900">{calculations.selectedPeriodText}</p>
                                <p className="text-caption text-surface-400">analysis range</p>
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

                <AnimationWrapper variant="slide-up" delay={0.2} id="charts-section" className="scroll-mt-20">
                    <h2 className="text-heading-md text-surface-700 mb-4">Overall Energy Analytics</h2>
                    <div id="tour-main-chart">
                        <EnergyLineChart
                            title="Actual vs Forecast"
                            subtitle="Total energy consumption comparison"
                            labels={[...labels.prevLabels, ...labels.nextLabels]}
                            actualData={chartData.actualData}
                            forecastData={chartData.forecastSeries}
                            riskStatus={calculations.budgetStatus}
                        />
                    </div>
                </AnimationWrapper>

                <AnimationWrapper variant="slide-up" delay={0.3}>
                    <h2 className="text-heading-md text-surface-700 mb-4">Appliance Breakdown</h2>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6" id="tour-appliance-breakdown">
                        {APPLIANCES.map((appliance) => {
                            const appData = calculations.applianceData[appliance];
                            const applianceActual = chartData.prevActualData.map((val) => {
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

                <AnimationWrapper variant="slide-up" delay={0.4}>
                    <h2 className="text-heading-md text-surface-700 mb-4">Settings & Consumption Ranking</h2>
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
            </main>
        </div>
    );
}

export default function DashboardPage() {
    return (
        <DashboardProvider>
            <DashboardContent />
        </DashboardProvider>
    );
}
