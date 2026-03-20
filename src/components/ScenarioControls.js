import React from 'react';
import { useDashboard } from '../context/DashboardContext';
import { AnimationWrapper } from './ui/AnimationWrapper';

export default function ScenarioControls({ baselineCost = 0, scenarioCost = 0 }) {
    const {
        isScenarioMode,
        setIsScenarioMode,
        scenarioParams,
        setScenarioParams,
        tariff
    } = useDashboard();

    // Initialize scenario params when mode is toggled on if not set
    const handleToggle = () => {
        if (!isScenarioMode) {
            setScenarioParams(prev => ({
                ...prev,
                tariffAdjustment: tariff, // Start with current tariff
                loadAdjustment: 0
            }));
        }
        setIsScenarioMode(!isScenarioMode);
    };

    const handleTariffChange = (e) => {
        setScenarioParams(prev => ({
            ...prev,
            tariffAdjustment: parseFloat(e.target.value)
        }));
    };

    const handleLoadChange = (e) => {
        setScenarioParams(prev => ({
            ...prev,
            loadAdjustment: parseInt(e.target.value, 10)
        }));
    };

    const applyPreset = (nextTariff, nextLoad) => {
        setScenarioParams(prev => ({
            ...prev,
            tariffAdjustment: Math.max(5, Math.min(30, nextTariff)),
            loadAdjustment: Math.max(-50, Math.min(50, nextLoad))
        }));
    };

    const resetToBaseline = () => {
        setScenarioParams(prev => ({
            ...prev,
            tariffAdjustment: tariff,
            loadAdjustment: 0
        }));
    };

    const tariffDeltaPct = tariff > 0
        ? ((scenarioParams.tariffAdjustment - tariff) / tariff) * 100
        : 0;
    const combinedMultiplier = tariff > 0
        ? (scenarioParams.tariffAdjustment / tariff) * (1 + (scenarioParams.loadAdjustment / 100))
        : 1;
    const overallBillDeltaPct = (combinedMultiplier - 1) * 100;
    const costDelta = scenarioCost - baselineCost;
    const hasCostPreview = Number.isFinite(baselineCost) && baselineCost > 0;
    const fmtPeso = (value) => `₱${Math.abs(Math.round(value)).toLocaleString()}`;

    return (
        <Card className={`overflow-hidden border-l-4 transition-all duration-300 ${isScenarioMode ? 'border-l-indigo-500 shadow-elevated ring-1 ring-indigo-100' : 'border-l-transparent hover:border-l-indigo-300'
            }`}>
            {/* ── INACTIVE STATE: The Call to Action ── */}
            {!isScenarioMode && (
                <div className="p-5 sm:p-6 bg-gradient-to-br from-indigo-50/50 to-white flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                    <div className="flex items-start gap-4">
                        <div className="p-3 rounded-xl bg-indigo-100 text-indigo-600 shadow-sm">
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.384-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                            </svg>
                        </div>
                        <div>
                            <h3 className="text-heading-sm font-bold text-surface-900">Wondering about next 24 hours bill?</h3>
                            <p className="text-body-sm text-surface-500 mt-1 max-w-md">
                                Run a "What-If" scenario to see how potential rate hikes or lifestyle changes will impact your forecasted energy costs.
                            </p>
                            <p className="text-[11px] text-surface-400 mt-1">
                                Simulation only: your saved tariff/budget and historical data are not changed.
                            </p>
                        </div>
                    </div>
                    <button
                        onClick={handleToggle}
                        className="w-full sm:w-auto whitespace-nowrap px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-body-sm font-semibold rounded-xl transition-all shadow-sm hover:shadow-md flex items-center justify-center gap-2 group"
                    >
                        <svg className="w-4 h-4 transition-transform group-hover:rotate-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                        Start Simulation
                    </button>
                </div>
            )}

            {/* ── ACTIVE STATE: The Controls ── */}
            {isScenarioMode && (
                <div className="p-4 sm:p-5">
                    <div className="flex flex-wrap items-center justify-between gap-4 mb-5">
                        <div className="flex items-center gap-3">
                            <div className="p-2 rounded-lg bg-indigo-50 text-indigo-600 animate-pulse">
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.384-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                                </svg>
                            </div>
                            <div>
                                <h3 className="text-heading-sm font-bold text-indigo-900">Simulation Active</h3>
                                <p className="text-caption text-indigo-600/80">Your dashboard is now showing projected values</p>
                            </div>
                        </div>

                        <button
                            onClick={handleToggle}
                            className="px-4 py-2 bg-surface-100 hover:bg-surface-200 text-surface-700 text-body-sm font-medium rounded-lg transition-colors flex items-center gap-2"
                        >
                            Exit Simulation
                        </button>
                    </div>

                    <AnimationWrapper variant="fade-in" layout>
                        <div className="space-y-6 pt-4 border-t border-surface-100">
                            {/* How to use */}
                            <div className="rounded-xl border border-indigo-100 bg-indigo-50 p-3">
                                <p className="text-[11px] font-bold uppercase tracking-wide text-indigo-600 mb-2">How to use</p>
                                <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                                    <div className="rounded-lg bg-white px-3 py-2 text-xs text-surface-700">
                                        1. Pick a preset or move sliders
                                    </div>
                                    <div className="rounded-lg bg-white px-3 py-2 text-xs text-surface-700">
                                        2. Check the estimated bill delta
                                    </div>
                                    <div className="rounded-lg bg-white px-3 py-2 text-xs text-surface-700">
                                        3. Use results to plan budget decisions
                                    </div>
                                </div>
                            </div>

                            {/* Cost Preview */}
                            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                                <div className="rounded-xl border border-surface-100 bg-white p-3">
                                    <p className="text-[10px] uppercase tracking-wide text-surface-400">Baseline Cost</p>
                                    <p className="text-sm font-bold text-surface-800 tabular-nums">
                                        {hasCostPreview ? fmtPeso(baselineCost) : 'Waiting for data'}
                                    </p>
                                </div>
                                <div className="rounded-xl border border-indigo-100 bg-indigo-50 p-3">
                                    <p className="text-[10px] uppercase tracking-wide text-indigo-500">Scenario Cost</p>
                                    <p className="text-sm font-bold text-indigo-800 tabular-nums">
                                        {hasCostPreview ? fmtPeso(scenarioCost) : 'Waiting for data'}
                                    </p>
                                </div>
                                <div className="rounded-xl border border-surface-100 bg-white p-3">
                                    <p className="text-[10px] uppercase tracking-wide text-surface-400">Cost Difference</p>
                                    <p className={`text-sm font-bold tabular-nums ${costDelta > 0 ? 'text-red-600' : costDelta < 0 ? 'text-emerald-600' : 'text-surface-700'}`}>
                                        {hasCostPreview ? `${costDelta > 0 ? '+' : costDelta < 0 ? '-' : ''}${fmtPeso(costDelta)}` : 'Waiting for data'}
                                    </p>
                                </div>
                            </div>

                            {hasCostPreview && (
                                <div className={`rounded-xl px-3 py-2 text-xs font-medium ${costDelta > 0 ? 'bg-red-50 text-red-700 border border-red-100' :
                                    costDelta < 0 ? 'bg-emerald-50 text-emerald-700 border border-emerald-100' :
                                        'bg-surface-50 text-surface-600 border border-surface-100'
                                    }`}>
                                    {costDelta > 0
                                        ? `This setup may increase your bill by about ${fmtPeso(costDelta)} for the selected forecast window.`
                                        : costDelta < 0
                                            ? `This setup may reduce your bill by about ${fmtPeso(Math.abs(costDelta))} for the selected forecast window.`
                                            : 'This setup keeps your bill near your current baseline for the selected forecast window.'}
                                </div>
                            )}

                            {/* Simulation Quick Presets */}
                            <div>
                                <div className="flex items-center justify-between mb-2">
                                    <p className="text-body-sm font-semibold text-surface-800">Quick Presets</p>
                                    <button
                                        onClick={resetToBaseline}
                                        className="text-xs font-semibold text-surface-500 hover:text-indigo-700 transition-colors"
                                    >
                                        Reset to baseline
                                    </button>
                                </div>
                                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                                    <button
                                        onClick={() => applyPreset(tariff, -10)}
                                        className="px-3 py-2 rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-700 text-xs font-semibold transition-colors"
                                    >
                                        Saver -10%
                                    </button>
                                    <button
                                        onClick={() => applyPreset(Number((tariff * 1.1).toFixed(2)), 0)}
                                        className="px-3 py-2 rounded-lg bg-amber-50 hover:bg-amber-100 text-amber-700 text-xs font-semibold transition-colors"
                                    >
                                        Rate +10%
                                    </button>
                                    <button
                                        onClick={() => applyPreset(tariff, 25)}
                                        className="px-3 py-2 rounded-lg bg-rose-50 hover:bg-rose-100 text-rose-700 text-xs font-semibold transition-colors"
                                    >
                                        Heat Wave +25%
                                    </button>
                                    <button
                                        onClick={() => applyPreset(Number((tariff * 1.15).toFixed(2)), 30)}
                                        className="px-3 py-2 rounded-lg bg-indigo-50 hover:bg-indigo-100 text-indigo-700 text-xs font-semibold transition-colors"
                                    >
                                        Stress Test
                                    </button>
                                </div>
                            </div>

                            {/* Impact Summary */}
                            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                                <div className="rounded-xl border border-surface-100 bg-white p-3">
                                    <p className="text-[10px] uppercase tracking-wide text-surface-400">Tariff Impact</p>
                                    <p className={`text-sm font-bold tabular-nums ${tariffDeltaPct > 0 ? 'text-red-600' : tariffDeltaPct < 0 ? 'text-emerald-600' : 'text-surface-700'}`}>
                                        {tariffDeltaPct > 0 ? '+' : ''}{tariffDeltaPct.toFixed(1)}%
                                    </p>
                                </div>
                                <div className="rounded-xl border border-surface-100 bg-white p-3">
                                    <p className="text-[10px] uppercase tracking-wide text-surface-400">Load Impact</p>
                                    <p className={`text-sm font-bold tabular-nums ${scenarioParams.loadAdjustment > 0 ? 'text-red-600' : scenarioParams.loadAdjustment < 0 ? 'text-emerald-600' : 'text-surface-700'}`}>
                                        {scenarioParams.loadAdjustment > 0 ? '+' : ''}{scenarioParams.loadAdjustment.toFixed(0)}%
                                    </p>
                                </div>
                                <div className="rounded-xl border border-indigo-100 bg-indigo-50 p-3">
                                    <p className="text-[10px] uppercase tracking-wide text-indigo-500">Estimated Bill Delta</p>
                                    <p className={`text-sm font-bold tabular-nums ${overallBillDeltaPct > 0 ? 'text-red-600' : overallBillDeltaPct < 0 ? 'text-emerald-600' : 'text-indigo-700'}`}>
                                        {overallBillDeltaPct > 0 ? '+' : ''}{overallBillDeltaPct.toFixed(1)}%
                                    </p>
                                </div>
                            </div>

                            {/* Tariff Adjustment */}
                            <div className="bg-surface-50 p-4 rounded-xl border border-surface-100/50">
                                <div className="flex justify-between mb-3">
                                    <label className="text-body-sm font-semibold text-surface-900">Virtual Tariff Rate</label>
                                    <span className="text-body-sm font-bold text-indigo-600 tabular-nums bg-indigo-50 px-2 py-0.5 rounded-md">
                                        ₱{scenarioParams.tariffAdjustment.toFixed(2)}
                                    </span>
                                </div>
                                <input
                                    type="range"
                                    min="5"
                                    max="30"
                                    step="0.01"
                                    value={scenarioParams.tariffAdjustment}
                                    onChange={handleTariffChange}
                                    className="w-full h-2 bg-surface-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                                />
                                <div className="flex justify-between mt-2">
                                    <span className="text-caption font-medium text-surface-400">₱5.00</span>
                                    <span className="text-caption font-medium text-surface-500 bg-white px-2 py-0.5 rounded border border-surface-100">
                                        Current: ₱{tariff.toFixed(2)}
                                    </span>
                                    <span className="text-caption font-medium text-surface-400">₱30.00</span>
                                </div>
                            </div>

                            {/* Load Adjustment */}
                            <div className="bg-surface-50 p-4 rounded-xl border border-surface-100/50">
                                <div className="flex justify-between mb-3">
                                    <label className="text-body-sm font-semibold text-surface-900">Usage Adjustments</label>
                                    <span className={`text-body-sm font-bold tabular-nums px-2 py-0.5 rounded-md ${scenarioParams.loadAdjustment > 0 ? 'bg-red-50 text-red-600' :
                                        scenarioParams.loadAdjustment < 0 ? 'bg-emerald-50 text-emerald-600' :
                                            'bg-surface-100 text-surface-600'
                                        }`}>
                                        {scenarioParams.loadAdjustment > 0 ? '+' : ''}{scenarioParams.loadAdjustment}%
                                    </span>
                                </div>
                                <input
                                    type="range"
                                    min="-50"
                                    max="50"
                                    step="5"
                                    value={scenarioParams.loadAdjustment}
                                    onChange={handleLoadChange}
                                    className="w-full h-2 bg-surface-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                                />
                                <div className="flex justify-between mt-2">
                                    <span className="text-caption font-medium text-emerald-600">-50% (Save)</span>
                                    <span className="text-caption font-medium text-surface-400">0%</span>
                                    <span className="text-caption font-medium text-red-500">+50% (Use More)</span>
                                </div>
                            </div>
                        </div>
                    </AnimationWrapper>
                </div>
            )}
        </Card>
    );
}

// Simple internal Card components to avoid circular dependencies or complex imports if not needed
function Card({ children, className = '' }) {
    return <div className={`bg-white rounded-2xl border border-surface-100 shadow-card ${className}`}>{children}</div>;
}
