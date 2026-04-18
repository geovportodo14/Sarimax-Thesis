const TIME_ZONE = 'Asia/Manila';

const BILLING_CYCLES = [
    { start: '2025-08-20', end: '2025-09-19', billDate: '2025-09-19', dueDate: '2025-10-01', kwh: 315,  confirmed: true  },
    { start: '2025-09-20', end: '2025-10-19', billDate: '2025-10-19', dueDate: '2025-10-31', kwh: 319,  confirmed: true  },
    { start: '2025-10-20', end: '2025-11-19', billDate: '2025-11-19', dueDate: '2025-11-30', kwh: 353,  confirmed: true  },
    { start: '2025-11-20', end: '2025-12-19', billDate: '2025-12-19', dueDate: '2025-12-30', kwh: 308,  confirmed: true  },
    { start: '2025-12-20', end: '2026-01-19', billDate: '2026-01-19', dueDate: '2026-01-30', kwh: 332,  confirmed: true  },
    { start: '2026-01-20', end: '2026-02-18', billDate: '2026-02-18', dueDate: '2026-03-01', kwh: 294,  confirmed: true  },
    { start: '2026-02-19', end: '2026-03-19', billDate: '2026-03-19', dueDate: '2026-03-30', kwh: 282,  confirmed: true  },
    // User-confirmed (not invoice-confirmed — no PDF available)
    { start: '2026-03-20', end: '2026-04-19', billDate: '2026-04-19', dueDate: '2026-04-30', kwh: null, confirmed: false },
];

const EARLIEST_DATE = BILLING_CYCLES[0].start;

// Treat stored YYYY-MM-DD as UTC midnight for day-level arithmetic (no hour-level Manila drift)
const parseDate  = (s) => new Date(s + 'T00:00:00Z');
const toDateStr  = (d) => d.toISOString().slice(0, 10);
const addDays    = (s, n) => { const d = parseDate(s); d.setUTCDate(d.getUTCDate() + n); return toDateStr(d); };
const dayDiff    = (a, b) => Math.round((parseDate(b) - parseDate(a)) / 86400000);

const formatDisplay = (s) =>
    new Intl.DateTimeFormat('en-GB', {
        day: '2-digit', month: 'short', year: 'numeric', timeZone: TIME_ZONE,
    }).format(parseDate(s)); // en-GB → "19 Apr 2026"

const getManilaToday = () =>
    new Intl.DateTimeFormat('en-CA', { timeZone: TIME_ZONE }).format(new Date());

// Project one cycle forward from the last known cycle.
// End = 19th of the month following the new start's month.
const projectCycle = (last) => {
    const start = addDays(last.end, 1);
    const [sy, sm] = start.split('-').map(Number);
    let ey = sy, em = sm + 1;
    if (em > 12) { em = 1; ey++; }
    const end      = `${ey}-${String(em).padStart(2, '0')}-19`;
    const billDate = end;
    const dueDate  = addDays(end, 11);
    return { start, end, billDate, dueDate, kwh: null, confirmed: false, toleranceDays: 2 };
};

export const computeCycleStatus = (referenceDateStr) => {
    const today = referenceDateStr || getManilaToday();

    if (today < EARLIEST_DATE) {
        return { outsideConfirmedRange: true, today };
    }

    let activeCycle = BILLING_CYCLES.find(c => today >= c.start && today <= c.end);

    if (!activeCycle) {
        // Outside seeded range — project forward (max 6 months)
        let last = BILLING_CYCLES[BILLING_CYCLES.length - 1];
        let projected = projectCycle(last);
        let safety = 0;
        while (today > projected.end && safety < 6) {
            projected = projectCycle(projected);
            safety++;
        }
        activeCycle = projected;
    }

    const totalDays    = dayDiff(activeCycle.start, activeCycle.end) + 1;
    const daysElapsed  = Math.min(dayDiff(activeCycle.start, today) + 1, totalDays);
    const daysRemaining = Math.max(totalDays - daysElapsed, 0);
    const tolerance    = activeCycle.toleranceDays ?? (activeCycle.confirmed ? 0 : 2);

    let statusLabel, statusType;
    if (today < activeCycle.end) {
        statusLabel = `Day ${daysElapsed} of ${totalDays} — ${daysRemaining} day${daysRemaining !== 1 ? 's' : ''} remaining`;
        statusType  = 'active';
    } else if (today === activeCycle.end) {
        statusLabel = 'Meter reading today — bill expected';
        statusType  = 'meter-day';
    } else if (today > activeCycle.end && today < activeCycle.dueDate) {
        const daysUntilDue = dayDiff(today, activeCycle.dueDate);
        statusLabel = `Bill posted — due in ${daysUntilDue} day${daysUntilDue !== 1 ? 's' : ''}`;
        statusType  = 'bill-posted';
    } else if (today === activeCycle.dueDate) {
        statusLabel = 'Due TODAY';
        statusType  = 'due-today';
    } else {
        const overdueDays = dayDiff(activeCycle.dueDate, today);
        statusLabel = `OVERDUE by ${overdueDays} day${overdueDays !== 1 ? 's' : ''}`;
        statusType  = 'overdue';
    }

    return {
        period: {
            start:     formatDisplay(activeCycle.start),
            end:       formatDisplay(activeCycle.end),
            totalDays,
            confirmed: activeCycle.confirmed,
        },
        meterReadingDate: { date: formatDisplay(activeCycle.end),      confirmed: activeCycle.confirmed },
        billDate:         { date: formatDisplay(activeCycle.billDate),  confirmed: activeCycle.confirmed },
        dueDate:          { date: formatDisplay(activeCycle.dueDate),   confirmed: activeCycle.confirmed },
        status:           { label: statusLabel, type: statusType },
        daysElapsed,
        daysRemaining,
        totalDays,
        tolerance,
        outsideConfirmedRange: false,
        disclaimer: 'Projected dates may shift ±1–2 days. Confirm against the actual Billing Invoice once posted.',
    };
};
