import React, { useState, useCallback } from 'react';
import { getApiUrl } from '../utils/api';

const TIME_ZONE = 'Asia/Manila';

const formatApplianceName = (name) => {
    const aliases = { aircon: 'Air Conditioner', electric_fan: 'Electric Fan', refrigerator: 'Refrigerator' };
    return aliases[name] || name;
};

export default function ForecastGeneratorCard({ currentDate }) {
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const safeDate = currentDate instanceof Date ? currentDate : new Date(currentDate);
    const dateStr = new Intl.DateTimeFormat('en-CA', { timeZone: TIME_ZONE }).format(safeDate);
    // Compute next day using the Manila date string to avoid timezone issues
    const nextDayDate = new Date(`${dateStr}T12:00:00+08:00`);
    nextDayDate.setDate(nextDayDate.getDate() + 1);
    const nextDayStr = new Intl.DateTimeFormat('en-CA', { timeZone: TIME_ZONE }).format(nextDayDate);
    const nextDayLabel = new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', year: 'numeric', timeZone: TIME_ZONE }).format(nextDayDate);

    const handleGenerate = useCallback(async () => {
        setLoading(true);
        setError(null);
        setResult(null);

        try {
            // Step 1: Run the pipeline
            const genRes = await fetch(getApiUrl('/api/forecast/generate'), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ date: nextDayStr }),
            });
            const genData = await genRes.json();

            if (!genRes.ok || genData.status !== 'success') {
                throw new Error(genData.message || 'Pipeline failed');
            }

            // Step 2: Fetch the generated forecast + schedule
            const forecastRes = await fetch(getApiUrl(`/api/forecast/daily?date=${nextDayStr}`));
            const forecastData = await forecastRes.json();

            setResult(forecastData);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, [nextDayStr]);

    const schedule = result?.schedule;
    const hasOptimization = schedule && schedule.status !== 'fallback' && schedule.appliances?.length > 0;

    return (
        <div className="bg-white rounded-2xl border border-surface-100 shadow-card overflow-hidden">
            {/* Header */}
            <div className="p-5 bg-gradient-to-br from-indigo-50/50 to-white border-b border-surface-100">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                    <div className="flex items-start gap-3">
                        <div className="p-2.5 rounded-xl bg-indigo-100 text-indigo-600">
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                            </svg>
                        </div>
                        <div>
                            <h3 className="text-sm font-bold text-surface-900">SARIMAX Forecast + MILP Optimizer</h3>
                            <p className="text-xs text-surface-500 mt-0.5">
                                Viewing <span className="font-semibold">{dateStr}</span> — forecast the next 24 hours (<span className="font-semibold">{nextDayLabel}</span>)
                            </p>
                        </div>
                    </div>

                    <button
                        onClick={handleGenerate}
                        disabled={loading}
                        className={`w-full sm:w-auto px-5 py-2.5 rounded-xl text-sm font-semibold transition-all flex items-center justify-center gap-2 ${
                            loading
                                ? 'bg-indigo-300 text-white cursor-wait'
                                : 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm hover:shadow-md'
                        }`}
                    >
                        {loading ? (
                            <>
                                <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                                </svg>
                                Running Pipeline...
                            </>
                        ) : (
                            <>
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                                </svg>
                                Forecast Next 24 Hours
                            </>
                        )}
                    </button>
                </div>
            </div>

            {/* Error */}
            {error && (
                <div className="p-4 bg-red-50 border-b border-red-100">
                    <p className="text-xs font-semibold text-red-700">Pipeline Error: {error}</p>
                </div>
            )}

            {/* Results */}
            {result && (
                <div className="p-5 space-y-5">
                    {/* Forecast Summary */}
                    {result.appliances?.length > 0 && (
                        <div>
                            <p className="text-[10px] font-bold uppercase tracking-widest text-surface-400 mb-3">Forecast Results — {nextDayLabel}</p>
                            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                                {result.appliances.map((app) => (
                                    <div key={app.appliance} className="rounded-xl border border-surface-100 bg-surface-50 p-3">
                                        <p className="text-[10px] uppercase tracking-wide text-surface-400">{formatApplianceName(app.appliance)}</p>
                                        <p className="text-lg font-bold text-surface-900 tabular-nums">{app.total_predicted_kwh?.toFixed(2)} kWh</p>
                                        <p className="text-[10px] text-surface-400">₱{app.total_predicted_cost_php?.toFixed(2)}</p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Optimization Results */}
                    {hasOptimization && (
                        <div>
                            <p className="text-[10px] font-bold uppercase tracking-widest text-indigo-500 mb-3">MILP Optimization</p>

                            {/* Savings banner */}
                            <div className="rounded-2xl bg-indigo-950 text-white p-5 mb-4">
                                <div className="grid grid-cols-3 gap-4 text-center">
                                    <div>
                                        <p className="text-[10px] uppercase tracking-wide text-indigo-300">Before Cost</p>
                                        <p className="text-xl font-black tabular-nums">₱{Number(schedule.baseline_total_cost_php).toFixed(2)}</p>
                                    </div>
                                    <div>
                                        <p className="text-[10px] uppercase tracking-wide text-emerald-300">After Scheduling</p>
                                        <p className="text-xl font-black tabular-nums text-emerald-400">₱{Number(schedule.optimized_total_cost_php).toFixed(2)}</p>
                                    </div>
                                    <div>
                                        <p className="text-[10px] uppercase tracking-wide text-indigo-300">Peak Reduction</p>
                                        <p className="text-xl font-black tabular-nums">{Number(schedule.peak_reduction_kwh).toFixed(3)} kWh</p>
                                    </div>
                                </div>
                                <div className="mt-3 pt-3 border-t border-indigo-800 text-center">
                                    <p className="text-sm text-indigo-200">
                                        Estimated savings: <span className="font-black text-emerald-400">₱{Number(schedule.estimated_savings_php).toFixed(2)}</span>
                                        {' '}({Number(schedule.estimated_savings_pct).toFixed(1)}% reduction)
                                    </p>
                                </div>
                            </div>

                            {/* Appliance Schedule */}
                            {schedule.time_block_summary && (
                                <div className="space-y-2">
                                    <p className="text-xs font-semibold text-surface-700">Appliance Schedule</p>
                                    {Object.entries(schedule.time_block_summary).map(([app, blocks]) => (
                                        <div key={app} className="flex items-center gap-3 rounded-xl border border-surface-100 bg-surface-50 p-3">
                                            <div className={`w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold ${
                                                app === 'aircon' ? 'bg-blue-100 text-blue-700' :
                                                app === 'electric_fan' ? 'bg-teal-100 text-teal-700' :
                                                'bg-amber-100 text-amber-700'
                                            }`}>
                                                {app === 'aircon' ? 'AC' : app === 'electric_fan' ? 'EF' : 'RF'}
                                            </div>
                                            <div>
                                                <p className="text-xs font-semibold text-surface-800">{formatApplianceName(app)}</p>
                                                <p className="text-[11px] text-surface-500">{blocks}</p>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}

                            {/* Top Actions */}
                            {schedule.optimization_summary?.top_actions?.length > 0 && (
                                <div className="mt-4 rounded-xl border border-emerald-100 bg-emerald-50 p-4">
                                    <p className="text-[10px] font-bold uppercase tracking-widest text-emerald-700 mb-2">Recommendations</p>
                                    <ul className="space-y-1.5">
                                        {schedule.optimization_summary.top_actions.map((action, i) => (
                                            <li key={i} className="text-xs text-emerald-800 flex items-start gap-2">
                                                <span className="mt-0.5 w-1.5 h-1.5 rounded-full bg-emerald-500 shrink-0" />
                                                {action}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    )}

                    {/* No optimization fallback */}
                    {result.appliances?.length > 0 && !hasOptimization && (
                        <div className="rounded-xl border border-amber-100 bg-amber-50 p-4">
                            <p className="text-xs text-amber-700 font-medium">
                                Forecast generated but MILP optimization was not available. Check if <code className="bg-amber-100 px-1 rounded">pulp</code> is installed.
                            </p>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
