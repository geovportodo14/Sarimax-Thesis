import React, { useEffect, useMemo } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { X, Calendar, Zap } from 'lucide-react';
import { ApplianceIcons } from './ui/icons';

function MonthlyApplianceSummaryModal({
    isOpen,
    onClose,
    selectedMonth,
    onMonthChange,
    maxMonth,
    loading = false,
    error = '',
    applianceCards = [],
    totalKwh = 0,
    tariff = 0
}) {
    useEffect(() => {
        if (!isOpen) return undefined;
        const { overflow } = document.body.style;
        document.body.style.overflow = 'hidden';
        return () => {
            document.body.style.overflow = overflow;
        };
    }, [isOpen]);

    useEffect(() => {
        if (!isOpen) return undefined;
        const onEsc = (event) => {
            if (event.key === 'Escape') onClose();
        };
        window.addEventListener('keydown', onEsc);
        return () => window.removeEventListener('keydown', onEsc);
    }, [isOpen, onClose]);

    const totalEstimatedCost = useMemo(() => Number(totalKwh || 0) * Number(tariff || 0), [totalKwh, tariff]);
    const topAppliance = useMemo(() => {
        if (!applianceCards.length) return null;
        return applianceCards.reduce((best, current) => (current.kwh > best.kwh ? current : best), applianceCards[0]);
    }, [applianceCards]);
    const hasData = useMemo(() => applianceCards.some((app) => Number(app.kwh || 0) > 0), [applianceCards]);

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    <motion.div
                        className="fixed inset-0 z-[90] bg-black/50 backdrop-blur-sm"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                    />

                    <motion.div
                        className="fixed inset-0 z-[91] p-4 sm:p-6 flex items-center justify-center"
                        initial={{ opacity: 0, y: 12, scale: 0.98 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: 8, scale: 0.98 }}
                        transition={{ duration: 0.2, ease: 'easeOut' }}
                    >
                        <div className="w-full max-w-4xl max-h-[90vh] overflow-y-auto rounded-3xl border border-primary-100 bg-gradient-to-br from-sky-50 via-white to-cyan-50 shadow-2xl">
                            <div className="sticky top-0 z-10 px-5 py-4 sm:px-6 sm:py-5 border-b border-surface-100 bg-white/90 backdrop-blur">
                                <div className="flex items-start justify-between gap-4">
                                    <div>
                                        <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-primary-50 text-primary-700 text-[10px] font-bold uppercase tracking-widest mb-2">
                                            <Calendar size={12} />
                                            Monthly Breakdown
                                        </div>
                                        <h3 className="text-heading-md text-surface-900 font-bold">Appliance Consumption Summary</h3>
                                        <p className="text-body-sm text-surface-500 mt-1">
                                            Accumulated monthly kWh and estimated cost per appliance.
                                        </p>
                                    </div>
                                    <button
                                        onClick={onClose}
                                        className="w-10 h-10 rounded-xl border border-surface-200 bg-white hover:bg-surface-50 text-surface-500 transition-colors flex items-center justify-center"
                                        aria-label="Close monthly summary"
                                    >
                                        <X size={18} />
                                    </button>
                                </div>
                            </div>

                            <div className="p-5 sm:p-6 space-y-5">
                                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                                    <div className="flex items-center gap-2">
                                        <label htmlFor="monthly-breakdown-month" className="text-caption font-medium text-surface-500">Month</label>
                                        <input
                                            id="monthly-breakdown-month"
                                            type="month"
                                            value={selectedMonth}
                                            max={maxMonth}
                                            onChange={(e) => {
                                                if (e.target.value) onMonthChange(e.target.value);
                                            }}
                                            className="px-3 py-1.5 rounded-lg border border-surface-200 bg-white text-body-sm text-surface-700 focus:outline-none focus:ring-2 focus:ring-primary-200"
                                        />
                                    </div>
                                    <div className="flex flex-wrap items-center gap-2 text-caption">
                                        <span className="px-2.5 py-1 rounded-full bg-sky-50 text-sky-700 border border-sky-100">
                                            Total: {Number(totalKwh || 0).toFixed(2)} kWh
                                        </span>
                                        <span className="px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-100">
                                            Est. Cost: ₱{totalEstimatedCost.toFixed(2)}
                                        </span>
                                    </div>
                                </div>

                                {!!error && !loading && (
                                    <div className="rounded-xl border border-red-200 bg-red-50 px-3 py-2">
                                        <p className="text-caption text-red-700">{error}</p>
                                    </div>
                                )}

                                {topAppliance && hasData && !loading && (
                                    <motion.div
                                        initial={{ opacity: 0, y: 8 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        className="rounded-2xl border border-amber-100 bg-amber-50/80 p-4 flex items-center gap-3"
                                    >
                                        <div className="w-10 h-10 rounded-xl bg-amber-100 text-amber-700 flex items-center justify-center">
                                            <Zap size={18} />
                                        </div>
                                        <div>
                                            <p className="text-caption text-amber-700 font-semibold uppercase tracking-wide">Top Consumer</p>
                                            <p className="text-body-md font-bold text-amber-900">
                                                {topAppliance.label} ({topAppliance.kwh.toFixed(2)} kWh, {topAppliance.share.toFixed(1)}%)
                                            </p>
                                        </div>
                                    </motion.div>
                                )}

                                {loading ? (
                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                        {[1, 2, 3].map((idx) => (
                                            <div key={idx} className="rounded-2xl border border-surface-100 bg-white p-4 space-y-2">
                                                <div className="h-4 w-24 rounded bg-surface-100 animate-pulse" />
                                                <div className="h-8 w-28 rounded bg-surface-100 animate-pulse" />
                                                <div className="h-3 w-20 rounded bg-surface-100 animate-pulse" />
                                                <div className="h-2 w-full rounded bg-surface-100 animate-pulse" />
                                            </div>
                                        ))}
                                    </div>
                                ) : hasData ? (
                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                        {applianceCards.map((app, index) => (
                                            <motion.div
                                                key={app.key}
                                                initial={{ opacity: 0, y: 12 }}
                                                animate={{ opacity: 1, y: 0 }}
                                                transition={{ delay: index * 0.06 }}
                                                className="rounded-2xl border border-surface-100 bg-white p-4 shadow-sm hover:shadow-md transition-shadow"
                                            >
                                                <div className="flex items-center justify-between mb-3">
                                                    <div className="flex items-center gap-2">
                                                        <div className="w-9 h-9 rounded-xl bg-surface-50 text-surface-700 flex items-center justify-center">
                                                            {ApplianceIcons[app.label] || ApplianceIcons.Default}
                                                        </div>
                                                        <p className="text-body-sm font-semibold text-surface-900">{app.label}</p>
                                                    </div>
                                                    <span className="text-[11px] font-bold px-2 py-1 rounded-full bg-primary-50 text-primary-700">
                                                        {app.share.toFixed(1)}%
                                                    </span>
                                                </div>

                                                <p className="text-2xl font-bold text-surface-900 tabular-nums">{app.kwh.toFixed(2)} kWh</p>
                                                <p className="text-caption text-surface-500 mt-1">Est. cost: ₱{app.estCost.toFixed(2)}</p>

                                                <div className="mt-3 h-2 rounded-full bg-surface-100 overflow-hidden">
                                                    <motion.div
                                                        className="h-full bg-gradient-to-r from-primary-500 to-cyan-500 rounded-full"
                                                        initial={{ width: 0 }}
                                                        animate={{ width: `${Math.min(100, Math.max(0, app.share))}%` }}
                                                        transition={{ duration: 0.45, delay: index * 0.05 }}
                                                    />
                                                </div>
                                            </motion.div>
                                        ))}
                                    </div>
                                ) : (
                                    <div className="rounded-2xl border border-dashed border-surface-300 bg-white/80 p-8 text-center">
                                        <p className="text-body-md font-semibold text-surface-700">No monthly readings yet</p>
                                        <p className="text-caption text-surface-500 mt-1">
                                            Try selecting another month or collect more readings for this period.
                                        </p>
                                    </div>
                                )}
                            </div>
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
}

export default MonthlyApplianceSummaryModal;
