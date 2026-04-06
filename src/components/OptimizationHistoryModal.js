import React, { useState, useEffect, useCallback } from 'react';
import { ChevronLeft, ChevronRight, X, Calendar, Zap, TrendingDown, DollarSign } from 'lucide-react';
import { getApiUrl } from '../utils/api';

function OptimizationHistoryModal({ isOpen, onClose }) {
    const [availableDates, setAvailableDates] = useState([]);
    const [selectedDate, setSelectedDate] = useState(null);
    const [schedule, setSchedule] = useState(null);
    const [loadingDates, setLoadingDates] = useState(false);
    const [loadingSchedule, setLoadingSchedule] = useState(false);

    // Load available dates on open
    useEffect(() => {
        if (!isOpen) return;
        setLoadingDates(true);
        fetch(getApiUrl('/api/schedule/dates'))
            .then(r => r.json())
            .then(data => {
                const dates = data.dates || [];
                setAvailableDates(dates);
                if (dates.length > 0 && !selectedDate) {
                    setSelectedDate(dates[dates.length - 1]); // default to latest
                }
            })
            .catch(console.error)
            .finally(() => setLoadingDates(false));
    }, [isOpen]); // eslint-disable-line react-hooks/exhaustive-deps

    // Load schedule when date changes
    useEffect(() => {
        if (!selectedDate) return;
        setLoadingSchedule(true);
        setSchedule(null);
        fetch(getApiUrl(`/api/forecast/daily?date=${selectedDate}`))
            .then(r => r.json())
            .then(data => setSchedule(data.schedule || null))
            .catch(console.error)
            .finally(() => setLoadingSchedule(false));
    }, [selectedDate]);

    const currentIndex = availableDates.indexOf(selectedDate);

    const goToPrev = useCallback(() => {
        if (currentIndex > 0) setSelectedDate(availableDates[currentIndex - 1]);
    }, [availableDates, currentIndex]);

    const goToNext = useCallback(() => {
        if (currentIndex < availableDates.length - 1) setSelectedDate(availableDates[currentIndex + 1]);
    }, [availableDates, currentIndex]);

    // Close on Escape
    useEffect(() => {
        if (!isOpen) return;
        const handler = (e) => { if (e.key === 'Escape') onClose(); };
        window.addEventListener('keydown', handler);
        return () => window.removeEventListener('keydown', handler);
    }, [isOpen, onClose]);

    if (!isOpen) return null;

    const formatDate = (dateStr) => {
        if (!dateStr) return '';
        const d = new Date(dateStr + 'T00:00:00');
        return d.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
    };

    const savings = schedule?.estimated_savings_php ?? null;
    const savingsPct = schedule?.estimated_savings_pct ?? null;
    const baselineCost = schedule?.baseline_total_cost_php ?? null;
    const optimizedCost = schedule?.optimized_total_cost_php ?? null;
    const peakReduction = schedule?.peak_reduction_kwh ?? null;
    const timeBlocks = schedule?.time_block_summary ?? {};
    const topActions = schedule?.optimization_summary?.top_actions ?? [];
    const status = schedule?.status ?? null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/40 backdrop-blur-sm"
                onClick={onClose}
            />

            {/* Modal */}
            <div className="relative bg-white rounded-3xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col overflow-hidden">

                {/* Header */}
                <div className="flex items-center justify-between px-6 py-4 border-b border-surface-100 shrink-0">
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-xl bg-primary-100 flex items-center justify-center">
                            <Calendar size={16} className="text-primary-600" />
                        </div>
                        <div>
                            <h2 className="text-base font-bold text-surface-900">Optimization History</h2>
                            <p className="text-xs text-surface-500">{availableDates.length} days available</p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="w-8 h-8 flex items-center justify-center rounded-xl hover:bg-surface-100 transition-colors"
                    >
                        <X size={16} className="text-surface-500" />
                    </button>
                </div>

                {/* Date navigator */}
                <div className="flex items-center justify-between px-6 py-3 bg-surface-50 border-b border-surface-100 shrink-0">
                    <button
                        onClick={goToPrev}
                        disabled={currentIndex <= 0}
                        className="w-8 h-8 flex items-center justify-center rounded-xl hover:bg-surface-200 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                    >
                        <ChevronLeft size={16} />
                    </button>

                    <div className="flex items-center gap-2">
                        <span className="text-sm font-semibold text-surface-900">
                            {loadingDates ? 'Loading…' : formatDate(selectedDate)}
                        </span>
                        {availableDates.length > 0 && (
                            <span className="text-xs text-surface-400">
                                ({currentIndex + 1} / {availableDates.length})
                            </span>
                        )}
                    </div>

                    <button
                        onClick={goToNext}
                        disabled={currentIndex >= availableDates.length - 1}
                        className="w-8 h-8 flex items-center justify-center rounded-xl hover:bg-surface-200 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                    >
                        <ChevronRight size={16} />
                    </button>
                </div>

                {/* Scrollable body */}
                <div className="flex-1 overflow-y-auto px-6 py-5 space-y-4">

                    {loadingSchedule && (
                        <div className="flex items-center justify-center py-16">
                            <div className="animate-spin rounded-full h-8 w-8 border-2 border-primary-200 border-t-primary-600" />
                        </div>
                    )}

                    {!loadingSchedule && !schedule && (
                        <div className="flex flex-col items-center justify-center py-16 text-center">
                            <div className="w-12 h-12 rounded-2xl bg-surface-100 flex items-center justify-center mb-3">
                                <Calendar size={20} className="text-surface-400" />
                            </div>
                            <p className="text-sm font-medium text-surface-600">No schedule available for this date</p>
                            <p className="text-xs text-surface-400 mt-1">The pipeline may not have run for this day.</p>
                        </div>
                    )}

                    {!loadingSchedule && schedule && (
                        <>
                            {/* Status badge */}
                            <div className="flex items-center gap-2">
                                <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${
                                    status === 'ok'
                                        ? 'bg-emerald-100 text-emerald-700'
                                        : 'bg-amber-100 text-amber-700'
                                }`}>
                                    {status === 'ok' ? 'Optimized' : 'Fallback'}
                                </span>
                                <span className="text-xs text-surface-400">Solver: {schedule.solver}</span>
                            </div>

                            {/* Cost summary cards */}
                            <div className="grid grid-cols-3 gap-3">
                                <div className="rounded-xl border border-surface-200 bg-surface-50 px-3 py-3">
                                    <p className="text-[10px] uppercase tracking-wide text-surface-500 mb-1">Before Cost</p>
                                    <p className="text-lg font-bold text-surface-900">
                                        ₱{baselineCost != null ? Number(baselineCost).toFixed(2) : '—'}
                                    </p>
                                </div>
                                <div className="rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-3">
                                    <p className="text-[10px] uppercase tracking-wide text-emerald-700 mb-1">After Scheduling</p>
                                    <p className="text-lg font-bold text-emerald-800">
                                        ₱{optimizedCost != null ? Number(optimizedCost).toFixed(2) : '—'}
                                    </p>
                                </div>
                                <div className="rounded-xl border border-blue-200 bg-blue-50 px-3 py-3">
                                    <p className="text-[10px] uppercase tracking-wide text-blue-700 mb-1">Peak Reduction</p>
                                    <p className="text-lg font-bold text-blue-800">
                                        {peakReduction != null ? Number(peakReduction).toFixed(3) : '—'} kWh
                                    </p>
                                </div>
                            </div>

                            {/* Savings highlight */}
                            {savings != null && savings > 0 && (
                                <div className="flex items-center gap-3 rounded-xl bg-gradient-to-r from-emerald-50 to-green-50 border border-emerald-200 px-4 py-3">
                                    <DollarSign size={18} className="text-emerald-600 shrink-0" />
                                    <div>
                                        <p className="text-sm font-bold text-emerald-800">
                                            ₱{Number(savings).toFixed(2)} saved
                                            {savingsPct != null && (
                                                <span className="ml-1 text-xs font-semibold text-emerald-600">
                                                    ({Number(savingsPct).toFixed(1)}%)
                                                </span>
                                            )}
                                        </p>
                                        <p className="text-xs text-emerald-700">vs. unscheduled baseline</p>
                                    </div>
                                </div>
                            )}

                            {/* Appliance schedule blocks */}
                            {Object.keys(timeBlocks).length > 0 && (
                                <div>
                                    <p className="text-xs font-bold text-surface-700 mb-2 flex items-center gap-1.5">
                                        <Zap size={12} className="text-amber-500" />
                                        Appliance Schedule
                                    </p>
                                    <div className="space-y-2">
                                        {Object.entries(timeBlocks).map(([appliance, block]) => (
                                            <div
                                                key={appliance}
                                                className="flex items-center justify-between rounded-lg border border-surface-200 bg-surface-50 px-3 py-2"
                                            >
                                                <span className="text-xs font-semibold text-surface-700 capitalize">
                                                    {appliance.replace(/_/g, ' ')}
                                                </span>
                                                <span className="text-xs text-surface-600">{block}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Top actions */}
                            {topActions.length > 0 && (
                                <div>
                                    <p className="text-xs font-bold text-surface-700 mb-2 flex items-center gap-1.5">
                                        <TrendingDown size={12} className="text-blue-500" />
                                        Suggested Actions
                                    </p>
                                    <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 space-y-1">
                                        {topActions.slice(0, 4).map((action, i) => (
                                            <p key={i} className="text-xs text-amber-900">— {action}</p>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </>
                    )}
                </div>

                {/* Date quick-select strip */}
                {availableDates.length > 0 && (
                    <div className="shrink-0 border-t border-surface-100 px-6 py-3">
                        <div className="flex gap-1.5 overflow-x-auto pb-1">
                            {availableDates.map(date => (
                                <button
                                    key={date}
                                    onClick={() => setSelectedDate(date)}
                                    className={`shrink-0 text-[10px] font-semibold px-2 py-1 rounded-lg transition-colors ${
                                        date === selectedDate
                                            ? 'bg-primary-600 text-white'
                                            : 'bg-surface-100 text-surface-600 hover:bg-surface-200'
                                    }`}
                                >
                                    {date.slice(5)} {/* show MM-DD */}
                                </button>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

export default OptimizationHistoryModal;
