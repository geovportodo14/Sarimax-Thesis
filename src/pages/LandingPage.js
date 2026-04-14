import React, { useEffect, useMemo, useState } from 'react';
import { ArrowRight, Zap, ShieldCheck, Cpu, CloudLightning, LayoutDashboard, Snowflake, Wind, ThermometerSnowflake, AlertTriangle, CheckCircle2, ReceiptText, ChevronRight } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { calculateMeralcoBill } from '../utils/meralcoCalculator';
import BillBreakdownModal from '../components/BillBreakdownModal';
import { getApiUrl } from '../utils/api';

const TIME_ZONE = 'Asia/Manila';
const DEFAULT_FORECAST_KWH_PER_DAY = 90;
const DEFAULT_PROJECTED_KWH = 280;

const formatApplianceName = (appliance) => {
    const aliases = {
        aircon: 'Air Conditioner',
        electric_fan: 'Electric Fan',
        refrigerator: 'Refrigerator'
    };
    if (aliases[appliance]) return aliases[appliance];
    return String(appliance || '')
        .replace(/_/g, ' ')
        .replace(/\s+/g, ' ')
        .trim()
        .replace(/\b\w/g, (char) => char.toUpperCase());
};

const getManilaDateString = (daysFromToday = 0) => {
    const todayStr = new Intl.DateTimeFormat('en-CA', { timeZone: TIME_ZONE }).format(new Date());
    const todayManilaMidnight = new Date(`${todayStr}T00:00:00+08:00`);
    const target = new Date(todayManilaMidnight.getTime() + (daysFromToday * 24 * 60 * 60 * 1000));
    return new Intl.DateTimeFormat('en-CA', { timeZone: TIME_ZONE }).format(target);
};

export default function LandingPage({ onEnterDashboard, monthlySummary, loadingSummary }) {
    const [budgetTarget, setBudgetTarget] = useState(4500);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [tomorrowForecast, setTomorrowForecast] = useState(null);

    useEffect(() => {
        const controller = new AbortController();

        const fetchTomorrowSummary = async () => {
            try {
                const dateStr = getManilaDateString(1);
                const response = await fetch(
                    getApiUrl(`/api/forecast/daily?date=${dateStr}`),
                    { signal: controller.signal }
                );
                const payload = await response.json();
                if (response.ok && (payload.status === 'success' || payload.status === 'no_data')) {
                    setTomorrowForecast(payload);
                }
            } catch (error) {
                if (error.name === 'AbortError') return;
                console.error('Landing forecast fetch failed:', error);
            }
        };

        fetchTomorrowSummary();
        return () => controller.abort();
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

    const manilaDateString = getManilaDateString(0);
    const manilaDate = new Date(`${manilaDateString}T00:00:00+08:00`);
    const manilaYear = manilaDate.getUTCFullYear();
    const manilaMonth = manilaDate.getUTCMonth();
    const manilaDay = manilaDate.getUTCDate();
    const daysInMonth = new Date(Date.UTC(manilaYear, manilaMonth + 1, 0)).getUTCDate();
    const remainingDays = Math.max(daysInMonth - manilaDay, 1);
    const currentMonthLabel = new Intl.DateTimeFormat('en-US', {
        month: 'short',
        year: 'numeric',
        timeZone: TIME_ZONE
    }).format(manilaDate);
    const simulatorFreshnessLabel = tomorrowTotalKwh > 0
        ? 'Forecast available'
        : 'Forecast run pending';

    // Compute projected kWh from actual MTD + forecasted daily estimate for remaining days.
    const spentSoFarKwh = (monthlySummary && !loadingSummary) ? monthlySummary.total_kwh : 0;
    const forecastRemainderKwh = tomorrowTotalKwh > 0 ? (tomorrowTotalKwh * remainingDays) : DEFAULT_FORECAST_KWH_PER_DAY;
    const projectedKwh = spentSoFarKwh > 0 ? (spentSoFarKwh + forecastRemainderKwh) : DEFAULT_PROJECTED_KWH;

    // Run projected kWh through precise Meralco simulator
    const billData = calculateMeralcoBill(projectedKwh);
    const spentData = calculateMeralcoBill(spentSoFarKwh);

    const spentSoFarPhp = spentData.totalAmount;
    const projectedUsage = billData.totalAmount;

    const isOverBudget = projectedUsage > budgetTarget;
    const difference = Math.abs(projectedUsage - budgetTarget);
    const progressPercent = Math.min((projectedUsage / budgetTarget) * 100, 100);
    const spentPercent = Math.min((spentSoFarPhp / budgetTarget) * 100, 100);

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
                        className="text-xs font-bold uppercase tracking-widest text-surface-400 hover:text-primary-600 transition-colors"
                    >
                        How it Works
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

                        <div className="mb-8 sm:mb-10">
                            {/* Primary Button: Enters the App */}
                            <button
                                onClick={onEnterDashboard}
                                className="flex items-center justify-center gap-2 px-6 py-3.5 bg-primary-600 hover:bg-primary-700 text-white font-semibold rounded-xl transition-all shadow-lg shadow-primary-500/30 hover:shadow-primary-500/50 group"
                            >
                                Launch Dashboard
                                <ArrowRight size={18} className="transition-transform group-hover:translate-x-1" />
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
                                <p className="text-sm text-surface-500">Month-end estimate from MTD usage + next-day model</p>
                                <div className="mt-3 flex flex-wrap items-center justify-center gap-2 text-[10px] font-bold uppercase tracking-wider">
                                    <span className="px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-100">
                                        {simulatorFreshnessLabel}
                                    </span>
                                    <span className="px-2.5 py-1 rounded-full bg-surface-100 text-surface-600 border border-surface-200">
                                        {currentMonthLabel}
                                    </span>
                                </div>
                            </div>

                            <div className="space-y-8">
                                <div className="p-4 rounded-2xl bg-surface-50/50 border border-surface-100">
                                    <div className="flex justify-between items-end mb-4">
                                        <label htmlFor="budget-target-slider" className="text-xs font-bold uppercase tracking-wider text-surface-400">Monthly Budget Target</label>
                                        <span className={`text-xl font-black ${isOverBudget ? 'text-red-600' : 'text-primary-600'}`}>
                                            ₱{budgetTarget.toLocaleString()}
                                        </span>
                                    </div>
                                    <input
                                        id="budget-target-slider"
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
                                            <span>Spent so far (MTD)</span>
                                        </div>
                                        <span className="font-bold text-surface-900">
                                            {loadingSummary ? '---' : `₱${Math.round(spentSoFarPhp).toLocaleString()}`}
                                        </span>
                                    </div>

                                    <div className="flex justify-between items-center text-sm border-t border-surface-100 pt-4">
                                        <div className="flex items-center gap-2 text-surface-700 font-semibold">
                                            <div className="w-2 h-2 rounded-full bg-primary-500 animate-pulse"></div>
                                            <span>Estimated month-end bill</span>
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

                                <div className="rounded-2xl border border-surface-200 bg-white/80 p-4">
                                    <p className="text-[10px] font-bold uppercase tracking-widest text-surface-500 mb-2">Simulation Basis</p>
                                    <div className="space-y-1.5 text-xs text-surface-600">
                                        <p>Remaining days this month: <span className="font-semibold text-surface-800">{remainingDays}</span></p>
                                        <p>
                                            Forecast basis: <span className="font-semibold text-surface-800">
                                                {tomorrowTotalKwh > 0 ? `${tomorrowTotalKwh.toFixed(2)} kWh/day` : 'Fallback baseline (forecast pending)'}
                                            </span>
                                        </p>
                                    </div>
                                </div>

                                <p className="text-[11px] text-surface-400 italic text-center leading-relaxed">
                                    Meralco charges change per month (per season and depends on billing). Projected costs may differ from your actual bill.
                                </p>

                                <div className="flex flex-col gap-3 pt-2">
                                    {isOverBudget && (
                                        <button onClick={onEnterDashboard} className="w-full py-4 flex items-center justify-center gap-2 text-white font-bold rounded-2xl transition-all shadow-lg active:scale-95 bg-red-600 hover:bg-red-700 shadow-red-200">
                                            Lower my bill now
                                            <ChevronRight size={20} />
                                        </button>
                                    )}

                                    <button onClick={() => setIsModalOpen(true)} className="w-full py-2.5 flex items-center justify-center gap-2 text-surface-500 font-bold text-xs uppercase tracking-widest hover:text-primary-600 hover:bg-white rounded-xl transition-all border border-transparent hover:border-surface-100">
                                        <ReceiptText size={16} />
                                        Full Bill Breakdown
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
                                <h3 className="text-6xl font-black text-white mb-4">{currentMonthLabel.toUpperCase()}</h3>
                                <p className="text-primary-200 font-bold uppercase tracking-widest mb-10 opacity-80">Live Tariff Simulation</p>
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
