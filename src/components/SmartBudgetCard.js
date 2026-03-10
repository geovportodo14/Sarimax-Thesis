import React, { useState } from 'react';
import { Info } from 'lucide-react';

/**
 * SmartBudgetCard
 * ───────────────
 * Displays a data-driven recommended daily budget range based on the
 * 24-hour SARIMAX energy forecast and model evaluation MAE.
 *
 * Formula (from thesis Section 3.6):
 *   estimatedCost = forecastKwh × tariff
 *   lowerBudget   = estimatedCost × (1 − errorPercent)
 *   upperBudget   = estimatedCost × (1 + errorPercent)
 *
 *   errorPercent  = weighted average of per-appliance (MAE_day / mean_day)
 *                   weighted by each appliance's share of total mean daily kWh
 *                   (only well-performing models included: aircon + electricfan)
 */

// ── Model evaluation constants ───────────────────────────────────────────────
// Source: rolling-origin validation, horizon = 24 h
// Appliances with R² < 0 are excluded from the weighting.
const APPLIANCE_METRICS = {
    aircon: { maePct: 0.151, meanDailyKwh: 2.6314, r2: 0.814 },
    electricfan: { maePct: 0.082, meanDailyKwh: 0.8826, r2: 0.837 },
    // Refrigerator excluded (R² = −11.9, MAE% > 200%)
};

/**
 * Compute the weighted MAE% from well-performing appliances.
 * Weight = appliance mean daily kWh / sum of included mean daily kWh.
 */
function computeWeightedMaePct() {
    const included = Object.values(APPLIANCE_METRICS).filter(m => m.r2 > 0);
    const totalMeanKwh = included.reduce((s, m) => s + m.meanDailyKwh, 0);
    return included.reduce(
        (s, m) => s + m.maePct * (m.meanDailyKwh / totalMeanKwh),
        0
    );
}

const WEIGHTED_MAE_PCT = computeWeightedMaePct(); // ≈ 0.131 (13.1 %)

export default function SmartBudgetCard({ forecastKwh = 0, tariff = 13.47 }) {
    const [showInfo, setShowInfo] = useState(false);

    const isReady = forecastKwh > 0 && tariff > 0;
    const estimatedCost = forecastKwh * tariff;
    const lowerBudget = estimatedCost * (1 - WEIGHTED_MAE_PCT);
    const upperBudget = estimatedCost * (1 + WEIGHTED_MAE_PCT);

    const fmt = (n) => `₱${Math.round(n).toLocaleString()}`;
    const fmtD = (n) => n.toFixed(2);

    return (
        <div className="relative overflow-hidden rounded-2xl border border-emerald-200 bg-gradient-to-br from-emerald-50 via-white to-teal-50 p-6 shadow-sm">
            {/* Decorative blobs */}
            <div className="pointer-events-none absolute -right-10 -top-10 h-40 w-40 rounded-full bg-emerald-100 opacity-40 blur-3xl" />
            <div className="pointer-events-none absolute -bottom-8 -left-8 h-32 w-32 rounded-full bg-teal-100 opacity-30 blur-2xl" />

            {/* Header */}
            <div className="relative flex items-start justify-between mb-5">
                <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl bg-emerald-600 text-white shadow-sm">
                        {/* Wallet icon */}
                        <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                        </svg>
                    </div>
                    <div>
                        <h3 className="text-base font-bold text-gray-900 leading-tight">
                            Recommended Daily Budget
                        </h3>
                        <p className="text-xs text-surface-500 mt-0.5">
                            Based on your 24-hour energy forecast
                        </p>
                    </div>
                </div>

                {/* Info toggle */}
                <button
                    onClick={() => setShowInfo(v => !v)}
                    className="flex-shrink-0 rounded-full p-1.5 text-surface-400 hover:bg-surface-100 hover:text-surface-600 transition-colors"
                    title="How is this calculated?"
                >
                    <Info size={16} />
                </button>
            </div>

            {/* Info panel */}
            {showInfo && (
                <div className="relative mb-5 rounded-xl border border-emerald-100 bg-white/80 p-4 text-xs text-surface-600 leading-relaxed space-y-1.5">
                    <p className="font-semibold text-surface-700 mb-1">How this is calculated</p>
                    <p>
                        <span className="font-medium">Estimated Cost</span> = Forecast kWh × Tariff Rate
                    </p>
                    <p>
                        <span className="font-medium">Budget Range</span> = Estimated Cost × (1 ± Error%)
                    </p>
                    <p>
                        <span className="font-medium">Error%</span> = Weighted MAE% from rolling-origin
                        model evaluation (Aircon: 15.1%, Electricfan: 8.2% → weighted avg ≈{' '}
                        {(WEIGHTED_MAE_PCT * 100).toFixed(1)}%)
                    </p>
                    <p className="text-surface-400 italic text-[10px] pt-1">
                        Refrigerator excluded from error weighting (R² = −11.9, high daily variance).
                    </p>
                </div>
            )}

            {!isReady ? (
                /* Empty state */
                <div className="relative text-center py-6">
                    <p className="text-sm text-surface-400">
                        Set a tariff rate and load forecast data to see your budget recommendation.
                    </p>
                </div>
            ) : (
                <>
                    {/* Budget Range — the hero number */}
                    <div className="relative mb-5 flex flex-col items-center justify-center gap-1 py-4 rounded-2xl bg-white border border-emerald-100 shadow-sm">
                        <p className="text-xs font-semibold uppercase tracking-widest text-emerald-600 mb-1">
                            Recommended Range
                        </p>
                        <div className="flex items-baseline gap-2">
                            <span className="text-3xl font-extrabold text-gray-900 tabular-nums">
                                {fmt(lowerBudget)}
                            </span>
                            <span className="text-xl font-light text-surface-400">–</span>
                            <span className="text-3xl font-extrabold text-gray-900 tabular-nums">
                                {fmt(upperBudget)}
                            </span>
                        </div>
                        <p className="text-xs text-surface-400 mt-1">for the next 24 hours</p>
                    </div>

                    {/* Breakdown row */}
                    <div className="relative grid grid-cols-3 gap-3">
                        <div className="rounded-xl bg-white border border-surface-100 p-3 text-center">
                            <p className="text-[10px] font-semibold uppercase tracking-wide text-surface-400 mb-1">
                                Forecast
                            </p>
                            <p className="text-sm font-bold text-surface-900 tabular-nums">
                                {fmtD(forecastKwh)} kWh
                            </p>
                        </div>
                        <div className="rounded-xl bg-white border border-surface-100 p-3 text-center">
                            <p className="text-[10px] font-semibold uppercase tracking-wide text-surface-400 mb-1">
                                Est. Cost
                            </p>
                            <p className="text-sm font-bold text-surface-900 tabular-nums">
                                {fmt(estimatedCost)}
                            </p>
                        </div>
                        <div className="rounded-xl bg-white border border-surface-100 p-3 text-center">
                            <p className="text-[10px] font-semibold uppercase tracking-wide text-surface-400 mb-1">
                                Error Margin
                            </p>
                            <p className="text-sm font-bold text-emerald-700 tabular-nums">
                                ±{(WEIGHTED_MAE_PCT * 100).toFixed(1)}%
                            </p>
                        </div>
                    </div>

                    {/* Visual range bar */}
                    <div className="relative mt-4">
                        <div className="flex items-center justify-between text-[10px] text-surface-400 mb-1">
                            <span>{fmt(lowerBudget)}</span>
                            <span className="font-medium text-surface-600">Est. {fmt(estimatedCost)}</span>
                            <span>{fmt(upperBudget)}</span>
                        </div>
                        <div className="h-2.5 rounded-full bg-surface-100 overflow-hidden">
                            {/* The "safe zone" spans from lower→upper, centre-aligned */}
                            <div
                                className="h-full rounded-full bg-gradient-to-r from-emerald-400 via-emerald-500 to-teal-500 transition-all duration-500"
                                style={{ width: '100%' }}
                            />
                        </div>
                        {/* Needle for estimated cost */}
                        <div
                            className="absolute top-5 h-4 w-0.5 bg-gray-600 rounded-full"
                            style={{ left: '50%', transform: 'translateX(-50%)' }}
                            title={`Estimated: ${fmt(estimatedCost)}`}
                        />
                    </div>

                    {/* Footer note */}
                    <p className="relative mt-4 text-[11px] text-surface-400 leading-relaxed text-center">
                        Range accounts for model forecasting uncertainty (MAE-derived, 24 h rolling-origin eval).
                    </p>
                </>
            )}
        </div>
    );
}
