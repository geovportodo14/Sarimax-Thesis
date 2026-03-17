import React, { useEffect, useMemo, useState } from 'react';
import { ArrowRight, Zap, ShieldCheck, PlayCircle, Cpu, CloudLightning, LayoutDashboard, Snowflake, Wind, ThermometerSnowflake, AlertTriangle, CheckCircle2, ReceiptText, TrendingDown, ChevronRight, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { calculateMeralcoBill } from '../utils/meralcoCalculator';
import BillBreakdownModal from '../components/BillBreakdownModal';
import { getApiUrl } from '../utils/api';

export default function LandingPage({ onEnterDashboard, monthlySummary, loadingSummary }) {
    const [budgetTarget, setBudgetTarget] = useState(4500);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [tomorrowForecast, setTomorrowForecast] = useState(null);
    const [showSavingStrategy, setShowSavingStrategy] = useState(false);

    useEffect(() => {
        if (!showSavingStrategy) return undefined;
        const handleEscape = (event) => {
            if (event.key === 'Escape') {
                setShowSavingStrategy(false);
            }
        };
        window.addEventListener('keydown', handleEscape);
        return () => window.removeEventListener('keydown', handleEscape);
    }, [showSavingStrategy]);

    useEffect(() => {
        const fetchTomorrowSummary = async () => {
            try {
                const tomorrow = new Date();
                tomorrow.setDate(tomorrow.getDate() + 1);
                const dateStr = new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Manila' }).format(tomorrow);
                const response = await fetch(getApiUrl(`/api/forecast/daily?date=${dateStr}`));
                const payload = await response.json();
                if (response.ok && (payload.status === 'success' || payload.status === 'no_data')) {
                    setTomorrowForecast(payload);
                }
            } catch (error) {
                console.error('Landing forecast fetch failed:', error);
            }
        };

        fetchTomorrowSummary();
    }, []);

    const tomorrowTotalKwh = useMemo(() => {
        if (tomorrowForecast?.appliances?.length) {
            return tomorrowForecast.appliances.reduce((sum, app) => sum + (app.total_predicted_kwh || 0), 0);
        }
        if (tomorrowForecast?.schedule?.appliances?.length) {
            return tomorrowForecast.schedule.appliances.reduce((sum, app) => sum + (app.baseline_total_kwh || 0), 0);
        }
        return 0;
    }, [tomorrowForecast]);

    const optimizationSummary = tomorrowForecast?.optimization_summary || tomorrowForecast?.schedule?.optimization_summary || null;
    const estimatedSavingsPhp = Number(
        tomorrowForecast?.schedule?.estimated_savings_php
        ?? optimizationSummary?.estimated_savings_php
        ?? 0
    );
    const peakReductionKwh = Number(
        tomorrowForecast?.schedule?.peak_reduction_kwh
        ?? optimizationSummary?.peak_reduction_kwh
        ?? 0
    );
    const hasOptimizationData = estimatedSavingsPhp > 0 || peakReductionKwh > 0;
    const formatApplianceName = (appliance) => {
        if (appliance === 'aircon') return 'Air Conditioner';
        if (appliance === 'electric_fan') return 'Electric Fan';
        if (appliance === 'refrigerator') return 'Refrigerator';
        return appliance;
    };
    const appliancePriorities = useMemo(() => {
        const scheduleApps = tomorrowForecast?.schedule?.appliances;
        if (!Array.isArray(scheduleApps)) return [];
        return scheduleApps
            .filter((app) => app.schedulable)
            .map((app) => ({
                appliance: app.appliance,
                label: formatApplianceName(app.appliance),
                shifted: Number(app.shifted_kwh || 0)
            }))
            .sort((a, b) => b.shifted - a.shifted)
            .slice(0, 2);
    }, [tomorrowForecast]);
    const topRecommendedAction = useMemo(() => {
        const topActions = optimizationSummary?.top_actions;
        if (Array.isArray(topActions) && topActions.length > 0) {
            return topActions[0];
        }

        const scheduleApps = tomorrowForecast?.schedule?.appliances;
        if (!Array.isArray(scheduleApps)) {
            return 'Follow the optimizer schedule to avoid peak-rate hours.';
        }

        const candidates = [];
        scheduleApps.forEach((app) => {
            (app.hourly || []).forEach((row) => {
                const reduction = Math.abs(Math.min(0, Number(row.delta_kwh || 0)));
                if (reduction < 0.03) return;
                candidates.push({
                    appliance: app.appliance,
                    hour: Number(row.hour ?? 0),
                    reduction,
                    tariff: Number(row.tariff_php_per_kwh || 0)
                });
            });
        });

        candidates.sort((a, b) => (b.reduction * b.tariff) - (a.reduction * a.tariff));
        if (candidates.length === 0) {
            return 'Shift discretionary usage away from peak-rate hours.';
        }

        const best = candidates[0];
        return `Reduce ${formatApplianceName(best.appliance)} around ${String(best.hour).padStart(2, '0')}:00.`;
    }, [optimizationSummary, tomorrowForecast]);
    const topOptimizerActions = useMemo(() => {
        const topActions = optimizationSummary?.top_actions;
        if (Array.isArray(topActions) && topActions.length > 0) {
            return topActions.slice(0, 3);
        }
        return [topRecommendedAction];
    }, [optimizationSummary, topRecommendedAction]);

    const now = new Date();
    const daysInMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate();
    const remainingDays = Math.max(daysInMonth - now.getDate(), 1);

    // Compute projected kWh from actual MTD + forecasted daily estimate for remaining days.
    const spentSoFarKwh = (monthlySummary && !loadingSummary) ? monthlySummary.total_kwh : 0;
    const forecastRemainderKwh = tomorrowTotalKwh > 0 ? (tomorrowTotalKwh * remainingDays) : 90;
    const projectedKwh = spentSoFarKwh > 0 ? (spentSoFarKwh + forecastRemainderKwh) : 280;

    // Run projected kWh through precise Meralco simulator
    const billData = calculateMeralcoBill(projectedKwh);
    const spentData = calculateMeralcoBill(spentSoFarKwh);

    const spentSoFarPhp = spentData.totalAmount;
    const projectedUsage = billData.totalAmount;

    const isOverBudget = projectedUsage > budgetTarget;
    const difference = Math.abs(projectedUsage - budgetTarget);
    const progressPercent = Math.min((projectedUsage / budgetTarget) * 100, 100);
    const spentPercent = Math.min((spentSoFarPhp / budgetTarget) * 100, 100);

    // 🌟 NEW: Smooth scroll function
    const scrollToHowItWorks = () => {
        const element = document.getElementById('how-it-works-section');
        if (element) {
            element.scrollIntoView({ behavior: 'smooth' });
        }
    };

    return (
        <div className="min-h-screen bg-[#fcfdfe] font-sans selection:bg-primary-100 selection:text-primary-900 relative overflow-hidden">
            {/* 🎨 PREMIUM BACKGROUND DECORATION */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none -z-10">
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 0.15 }}
                    transition={{ duration: 2 }}
                    className="absolute -top-[10%] -left-[10%] w-[50%] h-[50%] bg-gradient-to-br from-primary-400 to-blue-400 rounded-full blur-[120px]"
                />
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 0.1 }}
                    transition={{ duration: 2, delay: 0.5 }}
                    className="absolute top-[20%] -right-[5%] w-[40%] h-[60%] bg-gradient-to-tr from-indigo-400 to-teal-400 rounded-full blur-[100px]"
                />
            </div>

            {/* Navbar - Simplified */}
            <nav className="container mx-auto px-6 lg:px-10 py-5 flex items-center justify-end sticky top-0 z-50 transition-all duration-300 bg-[#fcfdfe]/80 border-b border-surface-100/30" style={{ backdropFilter: 'blur(16px)', WebkitBackdropFilter: 'blur(16px)' }}>
                <motion.div
                    initial={{ x: 20, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    className="flex items-center gap-6"
                >
                    <button
                        onClick={scrollToHowItWorks}
                        className="hidden md:block text-xs font-bold uppercase tracking-widest text-surface-400 hover:text-primary-600 transition-colors"
                    >
                        How it Works
                    </button>
                    <button
                        onClick={onEnterDashboard}
                        className="px-6 py-2.5 rounded-2xl text-xs font-black uppercase tracking-widest bg-surface-900 text-white hover:bg-black transition-all shadow-lg shadow-surface-200"
                    >
                        Go to Dashboard
                    </button>
                </motion.div>
            </nav>

            {/* ── HERO SECTION ── */}
            <main className="container mx-auto px-6 pt-12 pb-24 md:pt-16 lg:pt-20 relative z-10">
                <div className="grid md:grid-cols-2 gap-12 lg:gap-8 items-center">
                    <motion.div
                        initial={{ y: 30, opacity: 0 }}
                        animate={{ y: 0, opacity: 1 }}
                        transition={{ duration: 0.8 }}
                        className="max-w-2xl px-1 sm:px-0"
                    >
                        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/80 backdrop-blur-sm border border-emerald-100 text-emerald-700 text-[10px] sm:text-xs font-bold uppercase tracking-widest mb-8 shadow-sm">
                            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                            Thesis Edition • Real-Time Energy Analysis
                        </div>
                        <h1 className="text-4xl sm:text-5xl lg:text-7xl font-extrabold text-surface-900 leading-[1.05] mb-8 tracking-tight">
                            Lower your electric <br />
                            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-600 via-indigo-600 to-blue-500">
                                bill starting today.
                            </span>
                        </h1>
                        <p className="text-lg sm:text-xl text-surface-600 leading-relaxed mb-8 sm:mb-10 max-w-lg">
                            No more surprises when the bill arrives. We track your appliances and warn you before you overspend so you can stay within your budget.
                        </p>


                        <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 mb-8 sm:mb-10">
                            {/* Primary Button: Enters the App */}
                            <button
                                onClick={onEnterDashboard}
                                className="flex items-center justify-center gap-2 px-6 py-3.5 bg-primary-600 hover:bg-primary-700 text-white font-semibold rounded-xl transition-all shadow-lg shadow-primary-500/30 hover:shadow-primary-500/50 group"
                            >
                                Launch Dashboard
                                <ArrowRight size={18} className="transition-transform group-hover:translate-x-1" />
                            </button>

                            {/* 🌟 FIXED: Secondary Button now scrolls down instead of going to dashboard */}
                            <button
                                onClick={scrollToHowItWorks}
                                className="flex items-center justify-center gap-2 px-6 py-3.5 bg-white hover:bg-surface-50 text-surface-700 font-semibold rounded-xl border border-surface-200 transition-all shadow-sm"
                            >
                                <PlayCircle size={18} className="text-surface-400" />
                                How it Works
                            </button>
                        </div>

                        <div className="flex items-center flex-wrap gap-4 sm:gap-6 text-sm text-surface-500 font-medium pb-8 border-b border-surface-100/50 lg:border-none">
                            <div className="flex items-center gap-2"><ShieldCheck size={18} className="text-emerald-500" /> Secure Analysis</div>
                            <div className="flex items-center gap-2">SARIMAX Engine</div>
                        </div>
                    </motion.div>

                    <motion.div
                        initial={{ scale: 0.95, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        transition={{ duration: 0.8, delay: 0.2 }}
                        className="relative w-full max-w-md mx-auto lg:ml-auto"
                    >
                        {/* Glow effect behind card */}
                        <div className={`absolute inset-0 rounded-3xl blur-3xl opacity-30 transition-colors duration-1000 ${isOverBudget ? 'bg-red-400' : 'bg-primary-400'}`}></div>

                        <div
                            className="relative bg-white/80 border border-white/50 rounded-3xl shadow-[0_32px_64px_-16px_rgba(0,0,0,0.1)] p-6 sm:p-8"
                            style={{ backdropFilter: 'blur(24px)', WebkitBackdropFilter: 'blur(24px)' }}
                        >
                            <div className="mb-8 text-center relative">
                                <h3 className="text-2xl font-bold text-surface-900 mb-2">Budget Simulator</h3>
                                <p className="text-sm text-surface-500">Interactive live billing forecast</p>
                            </div>

                            <div className="space-y-8">
                                <div className="p-4 rounded-2xl bg-surface-50/50 border border-surface-100">
                                    <div className="flex justify-between items-end mb-4">
                                        <label className="text-xs font-bold uppercase tracking-wider text-surface-400">Monthly Budget</label>
                                        <span className={`text-xl font-black ${isOverBudget ? 'text-red-600' : 'text-primary-600'}`}>
                                            ₱{budgetTarget.toLocaleString()}
                                        </span>
                                    </div>
                                    <input
                                        type="range" min="2000" max="10000" step="100"
                                        value={budgetTarget}
                                        onChange={(e) => setBudgetTarget(Number(e.target.value))}
                                        className={`w-full h-1.5 rounded-lg appearance-none cursor-pointer transition-all ${isOverBudget ? 'accent-red-500 bg-red-100' : 'accent-primary-600 bg-surface-200'}`}
                                    />
                                    <div className="flex justify-between mt-2 text-[10px] font-bold text-surface-400">
                                        <span>2K</span><span>10K</span>
                                    </div>
                                </div>

                                <div className="space-y-5 px-1">
                                    <div className="flex justify-between items-center text-sm">
                                        <div className="flex items-center gap-2 text-surface-500">
                                            <div className="w-2 h-2 rounded-full bg-surface-300"></div>
                                            <span>Current Spend</span>
                                        </div>
                                        <span className="font-bold text-surface-900">
                                            {loadingSummary ? '---' : `₱${Math.round(spentSoFarPhp).toLocaleString()}`}
                                        </span>
                                    </div>

                                    <div className="flex justify-between items-center text-sm border-t border-surface-100 pt-4">
                                        <div className="flex items-center gap-2 text-surface-700 font-semibold">
                                            <div className="w-2 h-2 rounded-full bg-primary-500 animate-pulse"></div>
                                            <span>Projected End of Month</span>
                                        </div>
                                        <span className={`text-xl font-black ${isOverBudget ? 'text-red-600' : 'text-surface-900'}`}>
                                            ₱{Math.round(projectedUsage).toLocaleString()}
                                        </span>
                                    </div>

                                    {/* Premium Double-Layer Progress Bar */}
                                    <div className="h-4 w-full bg-surface-100 rounded-full overflow-hidden relative shadow-inner">
                                        <motion.div
                                            initial={{ width: 0 }}
                                            animate={{ width: `${progressPercent}%` }}
                                            className={`absolute top-0 left-0 h-full transition-all duration-1000 ${isOverBudget ? 'bg-red-400/30' : 'bg-primary-400/30'}`}
                                        ></motion.div>
                                        <motion.div
                                            initial={{ width: 0 }}
                                            animate={{ width: `${spentPercent}%` }}
                                            className={`absolute top-0 left-0 h-full transition-all duration-700 shadow-[0_0_12px_rgba(255,107,0,0.3)] ${isOverBudget ? 'bg-red-600' : 'bg-primary-600'}`}
                                        ></motion.div>
                                        {isOverBudget && (
                                            <div
                                                className="absolute top-0 h-full w-1 bg-red-900/50 z-10"
                                                style={{ left: `${(budgetTarget / projectedUsage) * 100}%` }}
                                            ></div>
                                        )}
                                    </div>
                                </div>

                                <AnimatePresence mode="wait">
                                    <motion.div
                                        key={isOverBudget ? 'warning' : 'success'}
                                        initial={{ y: 10, opacity: 0 }}
                                        animate={{ y: 0, opacity: 1 }}
                                        exit={{ y: -10, opacity: 0 }}
                                        className={`rounded-2xl p-4 flex items-start gap-3 border ${isOverBudget ? 'bg-red-50/80 border-red-100 text-red-800' : 'bg-emerald-50/80 border-emerald-100 text-emerald-800'}`}
                                    >
                                        {isOverBudget ? (
                                            <AlertTriangle className="text-red-500 mt-0.5 shrink-0" size={18} />
                                        ) : (
                                            <CheckCircle2 className="text-emerald-500 mt-0.5 shrink-0" size={18} />
                                        )}
                                        <div>
                                            <p className="text-sm font-bold">
                                                {isOverBudget ? 'Limit Exceeded' : 'Usage Optimized'}
                                            </p>
                                            <p className="text-xs mt-1 leading-relaxed opacity-90">
                                                {isOverBudget
                                                    ? `Forecasted overage: ₱${difference.toLocaleString()}. SARIMAX suggests lowering A/C runtime.`
                                                    : `You're tracking ₱${difference.toLocaleString()} under budget. Keep it up!`}
                                            </p>
                                        </div>
                                    </motion.div>
                                </AnimatePresence>

                                <div className="mb-2 relative">
                                    <button
                                        onClick={() => setShowSavingStrategy((prev) => !prev)}
                                        aria-expanded={showSavingStrategy}
                                        aria-controls="milp-strategy-popover"
                                        className="w-full py-3 px-4 rounded-2xl bg-indigo-50 border border-indigo-100 text-indigo-700 font-bold text-xs flex items-center justify-between group"
                                    >
                                        <div className="flex items-center gap-2">
                                            <div className="w-6 h-6 rounded-lg bg-indigo-600/10 flex items-center justify-center">
                                                <TrendingDown size={14} />
                                            </div>
                                            {showSavingStrategy ? 'Hide Optimization Strategy' : 'View Optimization Strategy'}
                                        </div>
                                        <motion.div animate={{ rotate: showSavingStrategy ? 90 : 0 }}>
                                            <ChevronRight size={16} />
                                        </motion.div>
                                    </button>
                                    <AnimatePresence>
                                        {showSavingStrategy && (
                                            <>
                                                <motion.button
                                                    type="button"
                                                    aria-label="Close optimization strategy popover"
                                                    className="fixed inset-0 z-30 bg-black/5 backdrop-blur-[1px]"
                                                    initial={{ opacity: 0 }}
                                                    animate={{ opacity: 1 }}
                                                    exit={{ opacity: 0 }}
                                                    onClick={() => setShowSavingStrategy(false)}
                                                />
                                                <motion.div
                                                    id="milp-strategy-popover"
                                                    role="dialog"
                                                    aria-modal="false"
                                                    initial={{ y: 12, opacity: 0, scale: 0.98 }}
                                                    animate={{ y: 0, opacity: 1, scale: 1 }}
                                                    exit={{ y: 8, opacity: 0, scale: 0.98 }}
                                                    transition={{ duration: 0.2 }}
                                                    className="absolute left-0 right-0 top-full mt-3 z-40"
                                                >
                                                    <div className="rounded-[2rem] border border-indigo-100 bg-gradient-to-br from-indigo-50/95 to-blue-50/95 p-5 sm:p-7 relative overflow-hidden shadow-2xl max-h-[70vh] overflow-y-auto">
                                                        <div className="absolute top-0 right-0 p-6 text-indigo-500/10 pointer-events-none">
                                                            <TrendingDown size={120} strokeWidth={1} />
                                                        </div>

                                                        <button
                                                            type="button"
                                                            onClick={() => setShowSavingStrategy(false)}
                                                            className="absolute top-4 right-4 w-8 h-8 rounded-lg bg-white/80 border border-indigo-100 text-indigo-700 hover:bg-white transition-colors flex items-center justify-center z-20"
                                                            aria-label="Close strategy popover"
                                                        >
                                                            <X size={14} />
                                                        </button>

                                                        <div className="relative z-10">
                                                            <div className="flex items-center justify-between gap-3 mb-5">
                                                                <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-indigo-600/10 text-indigo-700 text-[10px] font-black uppercase tracking-wider">
                                                                    <Cpu size={11} />
                                                                    Optimization Engine
                                                                </div>
                                                                <span className="text-[10px] font-black uppercase tracking-widest text-indigo-500 pr-10">
                                                                    MILP Strategy
                                                                </span>
                                                            </div>

                                                            <h4 className="text-xl font-black text-indigo-950 tracking-tight mb-4">Your Saving Strategy</h4>

                                                            {hasOptimizationData ? (
                                                                <div className="space-y-4">
                                                                    <div className="grid grid-cols-2 gap-3">
                                                                        <div className="rounded-2xl bg-white/90 border border-white shadow-sm p-3">
                                                                            <p className="text-[9px] font-black text-indigo-400 uppercase tracking-widest mb-1">Total Savings</p>
                                                                            <p className="text-2xl sm:text-3xl font-black text-indigo-950 tracking-tight tabular-nums">₱{estimatedSavingsPhp.toFixed(2)}</p>
                                                                        </div>
                                                                        <div className="rounded-2xl bg-white/90 border border-white shadow-sm p-3">
                                                                            <p className="text-[9px] font-black text-indigo-400 uppercase tracking-widest mb-1">Peak Reduction</p>
                                                                            <p className="text-2xl sm:text-3xl font-black text-indigo-950 tracking-tight tabular-nums">{peakReductionKwh.toFixed(2)}<span className="text-sm font-bold ml-1">kWh</span></p>
                                                                        </div>
                                                                    </div>

                                                                    <div className="rounded-2xl border border-indigo-100 bg-white/70 p-3">
                                                                        <p className="text-[9px] font-black text-indigo-500 uppercase tracking-widest mb-2">Priority Appliances</p>
                                                                        <div className="flex flex-wrap gap-2">
                                                                            {appliancePriorities.length > 0 ? (
                                                                                appliancePriorities.map((app) => (
                                                                                    <span
                                                                                        key={app.appliance}
                                                                                        className="px-2.5 py-1 rounded-full bg-indigo-100 text-indigo-800 text-[10px] font-bold uppercase tracking-wide"
                                                                                    >
                                                                                        {app.label}
                                                                                    </span>
                                                                                ))
                                                                            ) : (
                                                                                <span className="text-xs text-indigo-700">No schedulable appliance priorities yet.</span>
                                                                            )}
                                                                        </div>
                                                                    </div>

                                                                    <div className="bg-indigo-950 rounded-2xl p-4 text-white shadow-2xl flex items-center gap-4">
                                                                        <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-xl bg-indigo-800 flex items-center justify-center shrink-0 shadow-lg">
                                                                            <CloudLightning size={20} className="text-white" />
                                                                        </div>
                                                                        <div className="min-w-0">
                                                                            <p className="text-[9px] font-bold text-indigo-300 uppercase tracking-widest mb-1">Recommended Task</p>
                                                                            <p className="text-xs sm:text-sm font-bold leading-tight">{topRecommendedAction}</p>
                                                                        </div>
                                                                    </div>

                                                                    <div className="rounded-2xl border border-indigo-100 bg-white/85 p-3">
                                                                        <p className="text-[9px] font-black text-indigo-500 uppercase tracking-widest mb-2">Top Optimizer Actions</p>
                                                                        <div className="space-y-2">
                                                                            {topOptimizerActions.map((action, idx) => (
                                                                                <div key={`${action}-${idx}`} className="flex items-start gap-2 text-xs text-indigo-900">
                                                                                    <span className="w-5 h-5 mt-0.5 rounded-full bg-indigo-100 text-indigo-700 text-[10px] font-black flex items-center justify-center shrink-0">
                                                                                        {idx + 1}
                                                                                    </span>
                                                                                    <p className="leading-relaxed font-semibold">{action}</p>
                                                                                </div>
                                                                            ))}
                                                                        </div>
                                                                    </div>
                                                                </div>
                                                            ) : (
                                                                <div className="py-8 px-4 rounded-2xl bg-white/50 border border-dashed border-indigo-200 text-center">
                                                                    <div className="w-10 h-10 sm:w-12 sm:h-12 bg-indigo-50 rounded-full flex items-center justify-center mx-auto mb-4 text-indigo-300">
                                                                        <TrendingDown size={20} />
                                                                    </div>
                                                                    <p className="text-xs sm:text-sm text-indigo-800 font-medium leading-relaxed">
                                                                        Generate tomorrow forecast first to produce
                                                                        <span className="font-black text-indigo-600"> targeted appliance recommendations</span>.
                                                                    </p>
                                                                </div>
                                                            )}
                                                        </div>
                                                    </div>
                                                </motion.div>
                                            </>
                                        )}
                                    </AnimatePresence>
                                </div>

                                <div className="flex flex-col gap-3 pt-2">
                                    <button onClick={() => setIsModalOpen(true)} className="w-full py-2.5 flex items-center justify-center gap-2 text-surface-500 font-bold text-xs uppercase tracking-widest hover:text-primary-600 hover:bg-white rounded-xl transition-all border border-transparent hover:border-surface-100">
                                        <ReceiptText size={16} />
                                        Full Bill Breakdown
                                    </button>

                                    <button onClick={onEnterDashboard} className={`w-full py-4 flex items-center justify-center gap-2 text-white font-bold rounded-2xl transition-all shadow-lg active:scale-95 ${isOverBudget ? 'bg-red-600 hover:bg-red-700 shadow-red-200' : 'bg-surface-900 hover:bg-black shadow-surface-200'}`}>
                                        {isOverBudget ? 'Lower my bill now' : 'Open Dashboard'}
                                        <ChevronRight size={20} />
                                    </button>
                                </div>
                            </div>
                        </div>
                    </motion.div>
                </div>
            </main>

            {/* Render the Receipt Modal */}
            <BillBreakdownModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                billData={billData}
            />

            {/* ── HOW IT WORKS (Thesis Flow) ── */}
            <section id="how-it-works-section" className="relative py-32 bg-white overflow-hidden">
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-[800px] bg-gradient-to-b from-primary-50/20 to-transparent pointer-events-none -z-10"></div>

                <div className="container mx-auto px-6">
                    <motion.div
                        initial={{ y: 20, opacity: 0 }}
                        whileInView={{ y: 0, opacity: 1 }}
                        viewport={{ once: true }}
                        className="text-center max-w-3xl mx-auto mb-20"
                    >
                        <h2 className="text-4xl font-extrabold text-surface-900 mb-6 tracking-tight">How <span className="text-primary-600">SARIMAX</span> Works</h2>
                        <p className="text-lg text-surface-600 leading-relaxed">Our architecture combines real-time IoT telemetry with predictive modeling to bridge the gap between energy consumption and financial predictability.</p>
                    </motion.div>

                    <div className="grid md:grid-cols-3 gap-12">
                        {[
                            { icon: Cpu, color: 'text-blue-600', bg: 'bg-blue-50', title: '1. Watch', desc: 'We monitor your power use in real-time through smart hardware.' },
                            { icon: CloudLightning, color: 'text-indigo-600', bg: 'bg-indigo-50', title: '2. Predict', desc: 'The system calculates your likely monthly bill before it arrives.' },
                            { icon: LayoutDashboard, color: 'text-emerald-600', bg: 'bg-emerald-50', title: '3. Lower', desc: 'Get simple tips on when to use your appliances to save cash.' }
                        ].map((item, idx) => (
                            <motion.div
                                key={idx}
                                initial={{ y: 30, opacity: 0 }}
                                whileInView={{ y: 0, opacity: 1 }}
                                viewport={{ once: true }}
                                transition={{ delay: idx * 0.2 }}
                                className="group relative text-center p-8 rounded-3xl hover:bg-surface-50 transition-all duration-500 border border-transparent hover:border-surface-100"
                            >
                                <div className={`w-20 h-20 ${item.bg} ${item.color} rounded-[2rem] flex items-center justify-center mx-auto mb-8 transition-transform duration-500 group-hover:scale-110 group-hover:rotate-6 shadow-sm`}>
                                    <item.icon size={36} />
                                </div>
                                <h3 className="text-2xl font-bold text-surface-900 mb-4">{item.title}</h3>
                                <p className="text-surface-600 leading-relaxed">{item.desc}</p>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </section>

            {/* ── APPLIANCES TEASER ── */}
            <section className="py-32 bg-[#fcfdfe]">
                <div className="container mx-auto px-6 max-w-6xl">
                    <motion.div
                        initial={{ y: 40, opacity: 0 }}
                        whileInView={{ y: 0, opacity: 1 }}
                        viewport={{ once: true }}
                        className="bg-surface-900 rounded-[3rem] overflow-hidden shadow-2xl flex flex-col lg:flex-row relative"
                    >
                        {/* Decorative glow inside dark card */}
                        <div className="absolute top-0 right-0 w-full h-full bg-[radial-gradient(circle_at_top_right,rgba(255,107,0,0.1),transparent_50%)]"></div>

                        <div className="p-12 lg:p-16 lg:w-3/5 flex flex-col justify-center relative z-10">
                            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary-500/10 border border-primary-500/20 text-primary-400 text-[10px] font-bold uppercase tracking-widest mb-6">
                                Priority Monitoring
                            </div>
                            <h2 className="text-4xl lg:text-5xl font-extrabold text-white mb-6 tracking-tight">Meet the Power Hogs</h2>
                            <p className="text-xl text-surface-400 mb-10 leading-relaxed max-w-xl">
                                Our study isolates the top three highest-consuming device categories to provide granular visibility where it matters most.
                            </p>

                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                                {[
                                    { icon: Snowflake, text: 'Air Conditioner', detail: 'High-surge thermal load', color: 'text-sky-400' },
                                    { icon: ThermometerSnowflake, text: 'Refrigerator', detail: 'Constant 24/7 baseline', color: 'text-blue-400' },
                                    { icon: Wind, text: 'Electric Fan', detail: 'Continuous ambient load', color: 'text-teal-400' }
                                ].map((app, i) => (
                                    <div key={i} className="flex items-center gap-4 group">
                                        <div className="p-3 bg-surface-800 rounded-2xl group-hover:bg-primary-600 transition-colors duration-300">
                                            <app.icon size={24} className={app.color} />
                                        </div>
                                        <div>
                                            <p className="text-white font-bold group-hover:text-primary-400 transition-colors">{app.text}</p>
                                            <p className="text-surface-500 text-xs">{app.detail}</p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="lg:w-2/5 bg-gradient-to-br from-primary-600 via-primary-700 to-indigo-900 p-12 lg:p-16 flex items-center justify-center text-center relative">
                            <div className="relative z-10">
                                <motion.div
                                    animate={{ y: [0, -10, 0] }}
                                    transition={{ repeat: Infinity, duration: 3 }}
                                    className="text-primary-100/30 mb-8 flex justify-center"
                                >
                                    <Zap size={64} strokeWidth={1} />
                                </motion.div>
                                <h3 className="text-6xl font-black text-white mb-4">MAR 2026</h3>
                                <p className="text-primary-200 font-bold uppercase tracking-widest mb-10 opacity-80">Official Tariff Simulation</p>
                                <motion.button
                                    whileHover={{ scale: 1.05 }}
                                    whileTap={{ scale: 0.95 }}
                                    onClick={onEnterDashboard}
                                    className="w-full px-8 py-4 bg-white text-primary-900 font-black rounded-2xl shadow-xl hover:shadow-2xl transition-all"
                                >
                                    Analyze My Devices
                                </motion.button>
                            </div>
                        </div>
                    </motion.div>
                </div>
            </section>

        </div>
    );
}
