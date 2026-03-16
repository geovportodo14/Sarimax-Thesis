import React, { useEffect, useMemo, useState } from 'react';
import { ArrowRight, Zap, ShieldCheck, PlayCircle, Cpu, CloudLightning, LayoutDashboard, Snowflake, Wind, ThermometerSnowflake, AlertTriangle, CheckCircle2, ReceiptText } from 'lucide-react';
import { calculateMeralcoBill } from '../utils/meralcoCalculator';
import BillBreakdownModal from '../components/BillBreakdownModal';
import { getApiUrl } from '../utils/api';

export default function LandingPage({ onEnterDashboard, monthlySummary, loadingSummary }) {
    const [budgetTarget, setBudgetTarget] = useState(4500);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [tomorrowForecast, setTomorrowForecast] = useState(null);

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
        <div className="min-h-screen bg-surface-50 font-sans selection:bg-primary-100 selection:text-primary-900">
            {/* Navbar */}
            <nav className="container mx-auto px-10 py-4 flex items-center justify-between">
                <div className="flex items-center">
                    <img src="/logo3.png" alt="Sarimax Logo" className="h-20   md:h-24 w-auto object-contain drop-shadow-sm" />
                </div>
                <button
                    onClick={onEnterDashboard}
                    className="text-body-sm font-semibold text-surface-600 hover:text-surface-900 transition-colors"
                >
                    Go to Dashboard
                </button>
            </nav>

            {/* ── HERO SECTION ── */}
            <main className="container mx-auto px-6 pt-12 pb-24 lg:pt-20">
                <div className="grid lg:grid-cols-2 gap-12 lg:gap-8 items-center">
                    <div className="max-w-2xl">
                        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-100 text-emerald-700 text-xs font-bold uppercase tracking-wide mb-6">
                            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                            100% Free • Thesis Prototype
                        </div>
                        <h1 className="text-5xl lg:text-6xl font-extrabold text-surface-900 leading-[1.1] mb-6 tracking-tight">
                            Never get surprised by your <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-600 to-blue-500">electricity bill</span> again.
                        </h1>
                        <p className="text-lg text-surface-600 leading-relaxed mb-8 max-w-lg">
                            Track your energy usage, pinpoint your biggest power hogs, and get custom alerts before you bust your budget. Powered by our advanced SARIMAX forecasting model.
                        </p>

                        <div className="flex flex-col sm:flex-row gap-4 mb-10">
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

                        <div className="flex items-center gap-6 text-sm text-surface-500 font-medium">
                            <div className="flex items-center gap-1.5"><ShieldCheck size={16} className="text-emerald-500" /> No account needed</div>
                            <div className="flex items-center gap-1.5"><Zap size={16} className="text-amber-500" /> Real-time forecasts</div>
                        </div>
                    </div>

                    <div className="relative w-full max-w-md mx-auto lg:ml-auto">
                        <div className="absolute inset-0 bg-gradient-to-tr from-primary-200 to-blue-200 rounded-3xl blur-3xl opacity-50"></div>
                        <div className="relative bg-white border border-surface-100 rounded-2xl shadow-2xl p-6 sm:p-8">
                            <div className="mb-6 text-center">
                                <h3 className="text-xl font-bold text-surface-900 mb-2">Budget Simulator</h3>
                                <p className="text-sm text-surface-500">See how SARIMAX forecasting keeps you on track with your budget.</p>
                            </div>
                            <div className="space-y-6">
                                <div>
                                    <div className="flex justify-between items-end mb-2">
                                        <label className="text-sm font-semibold text-surface-700">Set your monthly budget limit</label>
                                        <span className="text-lg font-bold text-primary-600">₱{budgetTarget.toLocaleString()}</span>
                                    </div>
                                    <input
                                        type="range" min="2000" max="10000" step="100"
                                        value={budgetTarget}
                                        onChange={(e) => setBudgetTarget(Number(e.target.value))}
                                        className={`w-full h-2 rounded-lg appearance-none cursor-pointer ${isOverBudget ? 'bg-red-200 accent-red-500' : 'bg-surface-200 accent-primary-600'}`}
                                    />
                                    <div className="flex justify-between mt-1 text-xs font-medium text-surface-400">
                                        <span>₱2k</span><span>₱10k</span>
                                    </div>
                                </div>

                                <div className="space-y-4 text-sm mt-4">
                                    <div className="flex justify-between items-center border-b border-surface-100 pb-2">
                                        <span className="text-surface-500">Spent So Far (MTD)</span>
                                        <span className="font-semibold text-surface-900">
                                            {loadingSummary ? (
                                                <span className="inline-block w-12 h-4 bg-surface-200 rounded animate-pulse"></span>
                                            ) : (
                                                `₱${Math.round(spentSoFarPhp).toLocaleString()} `
                                            )}
                                        </span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-surface-600 font-medium">Projected End of Month</span>
                                        <span className="font-bold text-surface-900 text-base">₱{Math.round(projectedUsage).toLocaleString()}</span>
                                    </div>

                                    {/* Progress Bar */}
                                    <div className="h-3 w-full bg-surface-100 rounded-full overflow-hidden relative">
                                        <div
                                            className={`absolute top-0 left-0 h-full transition-all duration-500 ${isOverBudget ? 'bg-red-400 opacity-60' : 'bg-emerald-400 opacity-60'}`}
                                            style={{ width: `${progressPercent}%` }}
                                        ></div>
                                        {/* Inner Spent Bar */}
                                        <div
                                            className={`absolute top-0 left-0 h-full transition-all duration-700 ${isOverBudget ? 'bg-red-600' : 'bg-emerald-600'}`}
                                            style={{ width: `${spentPercent}%` }}
                                        ></div>
                                        {/* Budget Marker line if over budget to show where budget was */}
                                        {isOverBudget && (
                                            <div
                                                className="absolute top-0 h-full w-0.5 bg-red-800 z-10"
                                                style={{ left: `${(budgetTarget / projectedUsage) * 100}%` }}
                                            ></div>
                                        )}
                                    </div>

                                </div>

                                <div className={`border rounded-xl p-4 flex items-start gap-3 ${isOverBudget ? 'bg-red-50 border-red-100' : 'bg-emerald-50 border-emerald-100'}`}>
                                    {isOverBudget ? (
                                        <AlertTriangle className="text-red-500 mt-0.5 shrink-0" size={20} />
                                    ) : (
                                        <CheckCircle2 className="text-emerald-500 mt-0.5 shrink-0" size={20} />
                                    )}
                                    <div>
                                        <p className={`text-sm font-bold ${isOverBudget ? 'text-red-800' : 'text-emerald-800'}`}>
                                            {isOverBudget ? 'Budget Exceeded Warning' : 'You are on track!'}
                                        </p>
                                        <p className={`text-xs mt-1 leading-relaxed ${isOverBudget ? 'text-red-600' : 'text-emerald-600'}`}>
                                            {isOverBudget
                                                ? `SARIMAX predicts you will exceed your budget by ₱${difference.toLocaleString()}. Try reducing A/C usage by 1 hour daily.`
                                                : `Great job! Based on your habits, you'll finish the month ₱${difference.toLocaleString()} under budget.`}
                                        </p>
                                    </div>
                                </div>

                                <div className="rounded-xl border border-blue-100 bg-blue-50 p-3">
                                    <p className="text-[11px] uppercase tracking-wide text-blue-700 mb-2">
                                        Tomorrow Scheduling Preview (MILP)
                                    </p>
                                    {hasOptimizationData ? (
                                        <div className="grid grid-cols-2 gap-3">
                                            <div className="rounded-lg border border-blue-200 bg-white px-3 py-2">
                                                <p className="text-[11px] uppercase tracking-wide text-blue-700">Estimated Savings</p>
                                                <p className="text-base font-bold text-blue-900">₱{estimatedSavingsPhp.toFixed(2)}</p>
                                            </div>
                                            <div className="rounded-lg border border-indigo-200 bg-white px-3 py-2">
                                                <p className="text-[11px] uppercase tracking-wide text-indigo-700">Peak Reduction</p>
                                                <p className="text-base font-bold text-indigo-900">{peakReductionKwh.toFixed(3)} kWh</p>
                                            </div>
                                        </div>
                                    ) : (
                                        <p className="text-xs text-blue-800 leading-relaxed">
                                            Optimization summary is not available yet for tomorrow. Run the latest pipeline to generate scheduling outputs.
                                        </p>
                                    )}
                                </div>

                                <div className="flex flex-col gap-2">
                                    <button onClick={() => setIsModalOpen(true)} className="w-full py-2 flex items-center justify-center gap-2 text-surface-600 font-medium text-sm hover:text-primary-600 hover:bg-surface-50 rounded-xl transition-colors">
                                        <ReceiptText size={16} />
                                        View Detailed Billing Breakdown
                                    </button>

                                    <button onClick={onEnterDashboard} className={`w-full py-3 flex items-center justify-center gap-2 text-white font-semibold rounded-xl transition-colors shadow-sm ${isOverBudget ? 'bg-red-600 hover:bg-red-700' : 'bg-surface-900 hover:bg-surface-800'}`}>
                                        {isOverBudget ? 'Manage appliances to lower bill' : 'Launch full dashboard'}
                                        <ArrowRight size={16} />
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </main>

            {/* Render the Receipt Modal */}
            <BillBreakdownModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                billData={billData}
            />

            {/* ── HOW IT WORKS (Thesis Flow) ── */}
            {/* 🌟 FIXED: Added an ID here so the button knows where to scroll to! */}
            <section id="how-it-works-section" className="bg-white py-20 border-y border-surface-100">
                <div className="container mx-auto px-6">
                    <div className="text-center max-w-2xl mx-auto mb-16">
                        <h2 className="text-3xl font-bold text-surface-900 mb-4">How Sarimax Works</h2>
                        <p className="text-surface-600">Our system integrates IoT hardware with advanced machine learning to predict your future energy consumption before the bill arrives.</p>
                    </div>
                    <div className="grid md:grid-cols-3 gap-8">
                        <div className="text-center p-6">
                            <div className="w-16 h-16 bg-blue-50 text-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-6 rotate-3">
                                <Cpu size={32} />
                            </div>
                            <h3 className="text-xl font-bold text-surface-900 mb-3">1. IoT Monitoring</h3>
                            <p className="text-surface-600 text-sm leading-relaxed">Smart plugs capture real-time power consumption data directly from your appliances at frequent intervals.</p>
                        </div>
                        <div className="text-center p-6">
                            <div className="w-16 h-16 bg-indigo-50 text-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-6 -rotate-3">
                                <CloudLightning size={32} />
                            </div>
                            <h3 className="text-xl font-bold text-surface-900 mb-3">2. AI Forecasting</h3>
                            <p className="text-surface-600 text-sm leading-relaxed">The SARIMAX algorithm processes historical data and exogenous variables (like temperature) to predict future usage.</p>
                        </div>
                        <div className="text-center p-6">
                            <div className="w-16 h-16 bg-emerald-50 text-emerald-600 rounded-2xl flex items-center justify-center mx-auto mb-6 rotate-3">
                                <LayoutDashboard size={32} />
                            </div>
                            <h3 className="text-xl font-bold text-surface-900 mb-3">3. Actionable Insights</h3>
                            <p className="text-surface-600 text-sm leading-relaxed">View localized Meralco cost estimations, track specific appliances, and receive email alerts before exceeding your budget.</p>
                        </div>
                    </div>
                </div>
            </section>

            {/* ── APPLIANCES TEASER ── */}
            <section className="py-20 bg-surface-50">
                <div className="container mx-auto px-6 max-w-5xl">
                    <div className="bg-surface-900 rounded-3xl overflow-hidden shadow-2xl flex flex-col md:flex-row">
                        <div className="p-10 md:w-1/2 flex flex-col justify-center">
                            <h2 className="text-3xl font-bold text-white mb-4">Meet the Power Hogs</h2>
                            <p className="text-surface-300 mb-8 leading-relaxed">
                                Not all appliances are created equal. Our study focuses on tracking the top three highest-consuming household devices so you know exactly where your money is going.
                            </p>
                            <div className="space-y-4">
                                <div className="flex items-center gap-4 text-white">
                                    <div className="p-2 bg-surface-800 rounded-lg"><Snowflake size={20} className="text-sky-400" /></div>
                                    <span className="font-semibold">Air Conditioner</span>
                                </div>
                                <div className="flex items-center gap-4 text-white">
                                    <div className="p-2 bg-surface-800 rounded-lg"><ThermometerSnowflake size={20} className="text-blue-400" /></div>
                                    <span className="font-semibold">Refrigerator</span>
                                </div>
                                <div className="flex items-center gap-4 text-white">
                                    <div className="p-2 bg-surface-800 rounded-lg"><Wind size={20} className="text-teal-400" /></div>
                                    <span className="font-semibold">Electric Fan</span>
                                </div>
                            </div>
                        </div>
                        <div className="md:w-1/2 bg-gradient-to-br from-primary-600 to-indigo-800 p-10 flex items-center justify-center">
                            <div className="text-center">
                                <h3 className="text-5xl font-extrabold text-white mb-2">MAR 2026</h3>
                                <p className="text-primary-200 font-medium uppercase tracking-wider mb-8">Official Tariff Simulation</p>
                                <button onClick={onEnterDashboard} className="px-8 py-3 bg-white text-primary-700 font-bold rounded-xl shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all">
                                    Analyze My Devices
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    );
}
