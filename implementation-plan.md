
# Implementation Plan: Meralco Billing Cycle Tracker (Landing Page Widget)

**Prepared:** 2026-04-18  
**Target:** New `BillingCycleCard` component embedded in `LandingPage.js`

---

## 1. Data Model

Billing cycles are stored as a plain JS constant array in a new utility file:
`src/utils/billingCycle.js`

```js
// Each cycle object
{
  start: 'YYYY-MM-DD',        // Period start (inclusive)
  end: 'YYYY-MM-DD',          // Period end / meter reading date (inclusive)
  billDate: 'YYYY-MM-DD',     // Same as end for Meralco
  dueDate: 'YYYY-MM-DD',      // billDate + 10–12 days (exact from invoice)
  kwh: Number | null,         // null = not yet available
  confirmed: boolean           // true = from actual posted invoice; false = estimated
}
```

**Seeded confirmed history (last 7 cycles):**

| start | end | billDate | dueDate | kwh | confirmed |
|---|---|---|---|---|---|
| 2025-08-20 | 2025-09-19 | 2025-09-19 | 2025-10-01 | 315 | true |
| 2025-09-20 | 2025-10-19 | 2025-10-19 | 2025-10-31 | 319 | true |
| 2025-10-20 | 2025-11-19 | 2025-11-19 | 2025-11-30 | 353 | true |
| 2025-11-20 | 2025-12-19 | 2025-12-19 | 2025-12-30 | 308 | true |
| 2025-12-20 | 2026-01-19 | 2026-01-19 | 2026-01-30 | 332 | true |
| 2026-01-20 | 2026-02-18 | 2026-02-18 | 2026-03-01 | 294 | true |
| 2026-02-19 | 2026-03-19 | 2026-03-19 | 2026-03-30 | 282 | true |

**Current user-confirmed cycle (user-stated, not invoice-confirmed):**

| start | end | billDate | dueDate | kwh | confirmed |
|---|---|---|---|---|---|
| 2026-03-20 | 2026-04-19 | 2026-04-19 | 2026-04-30 | null | false |

---

## 2. Cycle Projection Logic (`src/utils/billingCycle.js`)

```
getActiveCycle(referenceDate):
  1. Find the cycle where start ≤ referenceDate ≤ end → return it
  2. If none found and referenceDate > last cycle's end:
     a. Project from last cycle's end + 1 day as new start
     b. Estimate end = start + 30 days (default; adjust for Feb)
     c. billDate = end
     d. dueDate = end + 11 days
     e. confirmed = false
  3. Return cycle with a toleranceDays: 2 flag on estimated entries

getNextCycle(activeCycle):
  - Start = activeCycle.end + 1 day
  - Apply same projection rules as step 2 above
```

**Leap year / short-month handling:**
- If projected end falls on Feb 28/29, cap at last day of Feb
- Flag with `toleranceDays: 2`

---

## 3. Status Computation

Given `activeCycle` and `today` (Manila date):

```
daysElapsed  = today - activeCycle.start + 1   (1-indexed, inclusive)
totalDays    = activeCycle.end - activeCycle.start + 1
daysRemaining = totalDays - daysElapsed

if today < activeCycle.end:
  status = `Day ${daysElapsed} of ${totalDays} — ${daysRemaining} day(s) remaining`

if today === activeCycle.end:
  status = `Meter reading today — bill expected`

if today > activeCycle.end && today < activeCycle.dueDate:
  daysSinceBill = today - activeCycle.billDate
  daysUntilDue  = activeCycle.dueDate - today
  status = `Bill posted ${daysSinceBill}d ago — due in ${daysUntilDue} day(s)`

if today === activeCycle.dueDate:
  status = `Due TODAY`

if today > activeCycle.dueDate:
  overdueDays = today - activeCycle.dueDate
  status = `OVERDUE by ${overdueDays} day(s)`
```

---

## 4. Confirmed-Bill Ingestion

A `confirmCycle(cycleData)` helper accepts an object with at minimum
`{ start, end, billDate, dueDate, kwh }` and:

1. Finds the matching estimated cycle in the array (by overlapping start/end)
2. Merges fields and sets `confirmed: true`
3. Removes the `toleranceDays` flag

In practice for this React app, confirmed bills are hardcoded in the seeded array.
Future: a small form in the UI to paste bill details → updates local state via `useState`.

---

## 5. Edge Cases

| Case | Handling |
|---|---|
| Today before 2025-08-20 | Return null; show "No reference data available" |
| Today exactly on end date | status = "Meter reading today" |
| Gap between cycles (cycle shifted > 2 days) | Log warning; project from last confirmed end + 1 |
| Leap year Feb end | Cap at Feb 29 (leap) or Feb 28 (non-leap); flag toleranceDays: 2 |
| Missing kwh on confirmed cycle | Render "— kWh" placeholder; never invent a value |
| referenceDate in between two non-overlapping cycles | Project a synthetic cycle bridging the gap |

---

## 6. Timezone Handling

- **All date math is done in Asia/Manila (UTC+8)**
- Use `Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Manila' })` to get `YYYY-MM-DD` string for "today" — same pattern already used in `LandingPage.js` via `getManilaDateString()`
- No `new Date()` arithmetic on raw timestamps — always convert to Manila date string first, then parse as `YYYY-MM-DD` integers for day-diff math
- Reuse the existing `getManilaDateString()` helper from `LandingPage.js` (move to utils if needed)

---

## 7. Output Contract — `BillingCycleCard` Props / Return Shape

The utility returns:

```js
{
  period: {
    start: 'DD Mon YYYY',
    end: 'DD Mon YYYY',
    totalDays: Number,
    confirmed: boolean
  },
  meterReadingDate: { date: 'DD Mon YYYY', confirmed: boolean },
  billDate:         { date: 'DD Mon YYYY', confirmed: boolean },
  dueDate:          { date: 'DD Mon YYYY', confirmed: boolean },
  status: {
    label: String,          // human-readable status string
    type: 'active' | 'meter-day' | 'bill-posted' | 'due-today' | 'overdue'
  },
  daysElapsed: Number,
  daysRemaining: Number,
  totalDays: Number,
  outsideConfirmedRange: boolean,
  disclaimer: String
}
```

---

## 8. UI Placement — Landing Page

**Position:** Between the Budget Simulator card and the "How SARIMAX Works" section.

**Component:** `src/components/BillingCycleCard.js`

**Design spec:**
- Same glassmorphism card style as existing landing page cards
- Two-column layout (desktop) / stacked (mobile)
- Left column: period label + progress bar (days elapsed / total)
- Right column: meter date, bill date, due date — each with a confirmed/estimated badge
- Status badge at bottom: color-coded
  - `active` → sky/blue
  - `meter-day` → orange (primary)
  - `bill-posted` → yellow
  - `due-today` → red
  - `overdue` → red + pulse animation
- "Estimated" entries show `±1–2 days` tooltip on hover
- Disclaimer text in `text-surface-400 text-xs` at bottom

---

## 9. Open Questions / Assumptions

| # | Question | Current Assumption |
|---|---|---|
| 1 | Should confirmed-bill ingestion be user-editable via a form in the UI? | No for MVP — hardcoded seed data only |
| 2 | Should the next projected cycle also be shown? | No — show active cycle only |
| 3 | Should kWh from billing history display in the card? | No — dates only per the rules |
| 4 | Where does `dueDate + 11 days` default come from? | Median of observed historical due offsets (10–12 days) |
| 5 | Should overdue state trigger a visual alert banner? | Yes — red pulse badge, no separate banner |
| 6 | Is the user-confirmed "20 Mar – 19 Apr" treated as confirmed or estimated? | `confirmed: false` — user-stated, not invoice-confirmed |

---

## Implementation Steps (after approval)

1. Create `src/utils/billingCycle.js` — data + projection + status logic
2. Create `src/components/BillingCycleCard.js` — UI component
3. Import and place `<BillingCycleCard />` in `LandingPage.js` between Budget Simulator and "How SARIMAX Works" sections
4. Smoke test: verify Manila timezone correctness, status transitions at boundary dates
