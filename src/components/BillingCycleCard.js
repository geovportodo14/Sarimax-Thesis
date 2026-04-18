import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import { Calendar, Clock, FileText, AlertCircle, CheckCircle2 } from 'lucide-react';
import { computeCycleStatus } from '../utils/billingCycle';

const STATUS_CONFIG = {
    active:       { color: 'text-sky-700',     bg: 'bg-sky-50',     border: 'border-sky-100',     dot: 'bg-sky-500',    pulse: false },
    'meter-day':  { color: 'text-primary-700', bg: 'bg-primary-50', border: 'border-primary-100', dot: 'bg-primary-500', pulse: true  },
    'bill-posted':{ color: 'text-amber-700',   bg: 'bg-amber-50',   border: 'border-amber-100',   dot: 'bg-amber-500',  pulse: false },
    'due-today':  { color: 'text-red-700',     bg: 'bg-red-50',     border: 'border-red-100',     dot: 'bg-red-500',    pulse: true  },
    overdue:      { color: 'text-red-700',     bg: 'bg-red-50',     border: 'border-red-100',     dot: 'bg-red-500',    pulse: true  },
};

function ConfirmedBadge({ confirmed, tolerance }) {
    if (confirmed) {
        return (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-100 text-[10px] font-bold uppercase tracking-wider">
                <CheckCircle2 size={9} /> confirmed
            </span>
        );
    }
    return (
        <span
            className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-50 text-amber-700 border border-amber-100 text-[10px] font-bold uppercase tracking-wider"
            title={`±${tolerance} day tolerance`}
        >
            <AlertCircle size={9} /> est. ±{tolerance}d
        </span>
    );
}

function DateRow({ icon: Icon, label, date, confirmed, tolerance }) {
    return (
        <div className="flex items-center justify-between py-2.5 border-b border-surface-100 last:border-0">
            <div className="flex items-center gap-2 text-surface-500 text-sm">
                <Icon size={13} className="text-surface-400 shrink-0" />
                <span>{label}</span>
            </div>
            <div className="flex items-center gap-2 flex-wrap justify-end">
                <span className="text-sm font-bold text-surface-800 font-mono">{date}</span>
                <ConfirmedBadge confirmed={confirmed} tolerance={tolerance} />
            </div>
        </div>
    );
}

export default function BillingCycleCard() {
    const cycle = useMemo(() => computeCycleStatus(), []);

    if (cycle.outsideConfirmedRange) return null;

    const {
        period, meterReadingDate, billDate, dueDate,
        status, daysElapsed, totalDays, daysRemaining, tolerance, disclaimer,
    } = cycle;

    const progressPercent = Math.min((daysElapsed / totalDays) * 100, 100);
    const cfg = STATUS_CONFIG[status.type] ?? STATUS_CONFIG.active;

    return (
        <section className="container mx-auto px-6 pb-12 max-w-4xl">
            <motion.div
                initial={{ y: 24, opacity: 0 }}
                whileInView={{ y: 0, opacity: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6 }}
                className="relative bg-white/80 border border-white/50 rounded-3xl shadow-[0_24px_48px_-12px_rgba(0,0,0,0.08)] p-6 sm:p-8 overflow-hidden"
                style={{ backdropFilter: 'blur(24px)', WebkitBackdropFilter: 'blur(24px)' }}
            >
                {/* Subtle background glow */}
                <div className="absolute -top-16 -right-16 w-48 h-48 bg-primary-100 rounded-full blur-3xl opacity-30 pointer-events-none" />

                {/* Header row */}
                <div className="flex flex-wrap items-start justify-between gap-3 mb-6">
                    <div>
                        <p className="text-[10px] font-bold uppercase tracking-widest text-surface-400 mb-0.5">Meralco</p>
                        <h3 className="font-bold text-surface-900 text-base tracking-tight">Billing Cycle Tracker</h3>
                        <p className="text-xs text-surface-500 mt-0.5">
                            {period.start} – {period.end}
                            <span className="ml-1.5 text-surface-400">({period.totalDays} days)</span>
                        </p>
                    </div>

                    <div className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full border text-xs font-bold shrink-0 ${cfg.bg} ${cfg.border} ${cfg.color}`}>
                        <span className={`w-1.5 h-1.5 rounded-full ${cfg.dot} ${cfg.pulse ? 'animate-pulse' : ''}`} />
                        {status.label}
                    </div>
                </div>

                <div className="grid sm:grid-cols-2 gap-6 sm:gap-10">
                    {/* Left — progress */}
                    <div className="flex flex-col justify-between gap-4">
                        <div>
                            <div className="flex justify-between text-[11px] text-surface-400 mb-2">
                                <span>Day {daysElapsed} of {totalDays}</span>
                                <span>{daysRemaining} day{daysRemaining !== 1 ? 's' : ''} left</span>
                            </div>
                            <div className="h-3 w-full bg-surface-100 rounded-full overflow-hidden shadow-inner">
                                <motion.div
                                    initial={{ width: 0 }}
                                    animate={{ width: `${progressPercent}%` }}
                                    transition={{ duration: 1, ease: 'easeOut' }}
                                    className="h-full bg-gradient-to-r from-primary-500 to-indigo-500 rounded-full shadow-[0_0_8px_rgba(255,107,0,0.25)]"
                                />
                            </div>
                        </div>

                        {/* Period badge */}
                        <div className={`rounded-2xl px-4 py-3 border ${cfg.bg} ${cfg.border}`}>
                            <p className={`text-xs font-bold ${cfg.color}`}>Current Period</p>
                            <p className="text-sm font-bold text-surface-800 mt-0.5 font-mono">
                                {period.start} – {period.end}
                            </p>
                            <div className="mt-1.5">
                                <ConfirmedBadge confirmed={period.confirmed} tolerance={tolerance} />
                            </div>
                        </div>
                    </div>

                    {/* Right — date rows */}
                    <div className="flex flex-col justify-center">
                        <DateRow
                            icon={Calendar}
                            label="Meter Reading"
                            date={meterReadingDate.date}
                            confirmed={meterReadingDate.confirmed}
                            tolerance={tolerance}
                        />
                        <DateRow
                            icon={FileText}
                            label="Bill Date"
                            date={billDate.date}
                            confirmed={billDate.confirmed}
                            tolerance={tolerance}
                        />
                        <DateRow
                            icon={Clock}
                            label="Due Date"
                            date={dueDate.date}
                            confirmed={dueDate.confirmed}
                            tolerance={tolerance}
                        />
                    </div>
                </div>

                {/* Disclaimer */}
                {!period.confirmed && (
                    <p className="text-[11px] text-surface-400 italic leading-relaxed border-t border-surface-100 pt-4 mt-5">
                        {disclaimer}
                    </p>
                )}
            </motion.div>
        </section>
    );
}
