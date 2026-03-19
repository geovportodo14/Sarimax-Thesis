"""
forecasting/pipeline/scheduler.py
=================================
Post-forecast appliance scheduling using MILP.

Two modes:

binary_mode=True  (default, as described in MILP.md)
    Decision variables are binary: b[appliance, hour] ∈ {0, 1}
        1 → appliance is ON that hour
        0 → appliance is OFF
    Objective: maximise total ON-hours (comfort), subject to:
        - Hard budget constraint: ΣΣ b × energy × tariff ≤ daily_budget
        - Only allowed_hours can be ON (night-only for aircon/fan)
        - Refrigerator: always ON (non-schedulable baseline)

binary_mode=False  (legacy continuous load-shifting)
    Decision variables are continuous shifts; minimises TOU cost + peak + comfort.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, TYPE_CHECKING

import pandas as pd

try:
    import pulp
except Exception:  # pragma: no cover
    pulp = None

if TYPE_CHECKING:
    from forecasting.pipeline.forecaster import ApplianceForecast


# =============================================================================
# Data models
# =============================================================================

@dataclass
class HourlyScheduleRow:
    hour: int
    timestamp: str
    tariff_php_per_kwh: float
    baseline_kwh: float
    optimized_kwh: float
    delta_kwh: float
    action: str
    on_off: bool = True          # True = ON, False = OFF (binary mode only)


@dataclass
class ApplianceSchedule:
    appliance: str
    schedulable: bool
    baseline_total_kwh: float
    optimized_total_kwh: float
    shifted_kwh: float
    hourly: List[HourlyScheduleRow]


@dataclass
class ScheduleResult:
    forecast_date: str
    generated_at: str
    status: str
    solver: str
    objective: float
    baseline_total_cost_php: float
    optimized_total_cost_php: float
    estimated_savings_php: float
    estimated_savings_pct: float
    baseline_peak_kwh: float
    optimized_peak_kwh: float
    peak_reduction_kwh: float
    tariff_by_hour: List[float]
    appliances: List[ApplianceSchedule]
    optimization_summary: Dict[str, Any]
    time_block_summary: Dict[str, str]   # appliance → human-readable time blocks

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["appliances"] = [
            {
                **{
                    k: v
                    for k, v in asdict(app).items()
                    if k != "hourly"
                },
                "hourly": [asdict(row) for row in app.hourly],
            }
            for app in self.appliances
        ]
        return payload

    def to_csv_rows(self) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        for app in self.appliances:
            for row in app.hourly:
                rows.append({
                    "forecast_date": self.forecast_date,
                    "appliance": app.appliance,
                    "schedulable": app.schedulable,
                    "hour": row.hour,
                    "timestamp": row.timestamp,
                    "tariff_php_per_kwh": row.tariff_php_per_kwh,
                    "baseline_kwh": row.baseline_kwh,
                    "optimized_kwh": row.optimized_kwh,
                    "delta_kwh": row.delta_kwh,
                    "on_off": row.on_off,
                    "action": row.action,
                })
        return rows


# =============================================================================
# Helpers
# =============================================================================

def _build_hourly_tariff(base_tariff: float, multipliers: Dict[str, float], horizon: int) -> List[float]:
    """
    Night-aware TOU tariff profile:
        night  18:00-05:59 → multipliers["night"]  (off-peak, when appliances run)
        mid    06:00-12:59 → multipliers["mid"]
        peak   13:00-17:59 → multipliers["peak"]
    Falls back to legacy off_peak key for backwards compatibility.
    """
    night_mult = float(multipliers.get("night", multipliers.get("off_peak", 0.85)))
    mid_mult   = float(multipliers.get("mid",   1.00))
    peak_mult  = float(multipliers.get("peak",  1.25))

    out: List[float] = []
    for hour in range(horizon):
        if 13 <= hour <= 17:
            out.append(round(base_tariff * peak_mult, 4))
        elif 6 <= hour <= 12:
            out.append(round(base_tariff * mid_mult, 4))
        else:
            # 0-5 and 18-23 → night/off-peak
            out.append(round(base_tariff * night_mult, 4))
    return out


def _action_from_on_off(on: bool, baseline_kwh: float) -> str:
    if baseline_kwh <= 0:
        return "OFF (no baseline usage)"
    return "ON — keep running" if on else "OFF — budget constraint"


def _action_from_delta(delta: float) -> str:
    if delta <= -0.02:
        return "Reduce usage in this hour"
    if delta >= 0.02:
        return "Shift usage into this hour"
    return "Keep baseline usage"


def _baseline_from_forecasts(
    appliance_forecasts: Dict[str, "ApplianceForecast"],
    horizon: int,
) -> tuple[Dict[str, List[float]], List[str]]:
    baseline: Dict[str, List[float]] = {}
    timestamps: Optional[List[str]] = None
    for appliance, fc in appliance_forecasts.items():
        vals = [max(0.0, float(v)) for v in fc.predicted_energy[:horizon]]
        if len(vals) < horizon:
            vals.extend([0.0] * (horizon - len(vals)))
        baseline[appliance] = vals

        if timestamps is None:
            ts = list(fc.timestamps[:horizon])
            if len(ts) < horizon:
                if ts:
                    start = pd.to_datetime(ts[0])
                else:
                    start = pd.Timestamp(fc.forecast_date)
                ts_idx = pd.date_range(start=start, periods=horizon, freq="h")
                ts = [t.isoformat() for t in ts_idx]
            timestamps = ts

    if timestamps is None:
        timestamps = [pd.Timestamp.now().isoformat()] * horizon

    return baseline, timestamps


def build_time_block_summary(
    appliances: List[ApplianceSchedule],
) -> Dict[str, str]:
    """
    Convert per-hour ON/OFF schedule into human-readable time-block strings.

    Example output:
        {
            "aircon":       "9 PM – 11 PM",
            "electric_fan": "8 PM – 11 PM",
            "refrigerator": "Continuous operation",
        }
    """

    def _fmt_hour(h: int) -> str:
        if h == 0:
            return "12 AM"
        if h == 12:
            return "12 PM"
        if h < 12:
            return f"{h} AM"
        return f"{h - 12} PM"

    summary: Dict[str, str] = {}

    for app in appliances:
        if not app.schedulable:
            summary[app.appliance] = "Continuous operation"
            continue

        on_hours = sorted([row.hour for row in app.hourly if row.on_off])
        if not on_hours:
            summary[app.appliance] = "OFF (entire day)"
            continue

        # Build consecutive blocks
        blocks: List[tuple[int, int]] = []
        start = on_hours[0]
        prev  = on_hours[0]
        for h in on_hours[1:]:
            if h == prev + 1:
                prev = h
            else:
                blocks.append((start, prev))
                start = prev = h
        blocks.append((start, prev))

        block_strs = [
            f"{_fmt_hour(s)} – {_fmt_hour(e + 1)}" if e + 1 <= 23 else f"{_fmt_hour(s)} – midnight"
            for s, e in blocks
        ]
        summary[app.appliance] = ", ".join(block_strs)

    return summary


def _build_fallback_result(
    forecast_date: str,
    generated_at: str,
    baseline: Dict[str, List[float]],
    timestamps: List[str],
    hourly_tariff: List[float],
    reason: str,
) -> ScheduleResult:
    appliances: List[ApplianceSchedule] = []
    baseline_total_cost = 0.0
    baseline_peak = 0.0

    for hour in range(len(hourly_tariff)):
        total_h = sum(baseline.get(a, [0.0] * len(hourly_tariff))[hour] for a in baseline)
        baseline_peak = max(baseline_peak, total_h)
        baseline_total_cost += total_h * hourly_tariff[hour]

    for appliance, vals in baseline.items():
        rows = [
            HourlyScheduleRow(
                hour=h,
                timestamp=timestamps[h],
                tariff_php_per_kwh=hourly_tariff[h],
                baseline_kwh=round(vals[h], 6),
                optimized_kwh=round(vals[h], 6),
                delta_kwh=0.0,
                action="Keep baseline usage",
                on_off=True,
            )
            for h in range(len(vals))
        ]
        appliances.append(
            ApplianceSchedule(
                appliance=appliance,
                schedulable=False,
                baseline_total_kwh=round(sum(vals), 6),
                optimized_total_kwh=round(sum(vals), 6),
                shifted_kwh=0.0,
                hourly=rows,
            )
        )

    baseline_total_cost = round(baseline_total_cost, 4)
    summary = {
        "status": "fallback",
        "reason": reason,
        "solver_status": "fallback",
        "estimated_savings_php": 0.0,
        "peak_reduction_kwh": 0.0,
        "top_actions": [],
    }

    tbs = build_time_block_summary(appliances)

    return ScheduleResult(
        forecast_date=forecast_date,
        generated_at=generated_at,
        status="fallback",
        solver="none",
        objective=baseline_total_cost,
        baseline_total_cost_php=baseline_total_cost,
        optimized_total_cost_php=baseline_total_cost,
        estimated_savings_php=0.0,
        estimated_savings_pct=0.0,
        baseline_peak_kwh=round(baseline_peak, 6),
        optimized_peak_kwh=round(baseline_peak, 6),
        peak_reduction_kwh=0.0,
        tariff_by_hour=hourly_tariff,
        appliances=appliances,
        optimization_summary=summary,
        time_block_summary=tbs,
    )


# =============================================================================
# Binary ON/OFF MILP (MILP.md design)
# =============================================================================

def _solve_binary(
    baseline: Dict[str, List[float]],
    timestamps: List[str],
    hourly_tariff: List[float],
    forecast_date: str,
    generated_at: str,
    appliance_rules: Dict[str, Dict[str, Any]],
    budget_constraint_php: Optional[float],
    horizon: int,
) -> ScheduleResult:
    """
    Binary ON/OFF MILP as described in MILP.md.

    Decision: b[appliance, hour] ∈ {0, 1}
        b = 1 → appliance ON that hour  (uses forecast_energy kWh)
        b = 0 → appliance OFF            (0 kWh)

    Objective: maximise Σ b  (keep appliances ON as much as possible)

    Constraints:
        1. Budget: Σ_h Σ_app  b[app,h] × energy[app,h] × tariff[h] ≤ budget
        2. Only allowed_hours can be ON: b[app,h] = 0 for h ∉ allowed_hours
        3. Refrigerator: not a decision variable, always ON
    """
    problem = pulp.LpProblem("binary_appliance_scheduling", pulp.LpMaximize)

    schedulable: List[str] = []
    b_vars: Dict[tuple[str, int], pulp.LpVariable] = {}

    for appliance, rule in appliance_rules.items():
        if appliance not in baseline:
            continue
        if not bool(rule.get("schedulable", True)):
            continue

        schedulable.append(appliance)
        allowed = set(int(h) for h in rule.get("allowed_hours", list(range(horizon))))
        base_vals = baseline[appliance]

        for h in range(horizon):
            if h in allowed and base_vals[h] > 0:
                b_vars[(appliance, h)] = pulp.LpVariable(
                    f"b_{appliance}_{h}", cat=pulp.const.LpBinary
                )

    # Objective: maximise total ON-hours (comfort)
    on_terms = [b for b in b_vars.values()]
    problem += pulp.lpSum(on_terms) if on_terms else 0

    # Hard budget constraint — applies only to schedulable appliances
    # (refrigerator is a sunk cost the user cannot reduce)
    if budget_constraint_php is not None and budget_constraint_php > 0:
        ref_cost = sum(
            baseline[a][h] * hourly_tariff[h]
            for a in baseline
            if a not in schedulable
            for h in range(horizon)
        )
        remaining_budget = max(0.0, budget_constraint_php - ref_cost)
        controllable_cost_terms = [
            b_vars[(app, h)] * baseline[app][h] * hourly_tariff[h]
            for (app, h) in b_vars
        ]
        if controllable_cost_terms:
            problem += (
                pulp.lpSum(controllable_cost_terms) <= remaining_budget,
                "hard_schedulable_budget",
            )

    try:
        solver = pulp.PULP_CBC_CMD(msg=False)
        problem.solve(solver)
    except Exception as exc:
        return _build_fallback_result(
            forecast_date=forecast_date,
            generated_at=generated_at,
            baseline=baseline,
            timestamps=timestamps,
            hourly_tariff=hourly_tariff,
            reason=f"Solver failed: {exc}",
        )

    status = pulp.LpStatus.get(problem.status, "Unknown")
    if status not in {"Optimal", "Feasible"}:
        return _build_fallback_result(
            forecast_date=forecast_date,
            generated_at=generated_at,
            baseline=baseline,
            timestamps=timestamps,
            hourly_tariff=hourly_tariff,
            reason=f"Solver status: {status}",
        )

    # ── Build result ──────────────────────────────────────────────────────────
    optimized: Dict[str, List[float]] = {}
    on_off_map: Dict[str, List[bool]] = {}

    for appliance, base_vals in baseline.items():
        if appliance in schedulable:
            opt_vals = []
            oo = []
            for h in range(horizon):
                bvar = b_vars.get((appliance, h))
                if bvar is not None:
                    is_on = bool(round(pulp.value(bvar) or 0))
                else:
                    is_on = False   # outside allowed hours OR zero baseline
                opt_vals.append(base_vals[h] if is_on else 0.0)
                oo.append(is_on)
            optimized[appliance] = opt_vals
            on_off_map[appliance] = oo
        else:
            optimized[appliance] = list(base_vals)
            on_off_map[appliance] = [True] * horizon

    baseline_total_cost = 0.0
    optimized_total_cost = 0.0
    baseline_peak = 0.0
    optimized_peak = 0.0
    for h in range(horizon):
        bt = sum(baseline[a][h] for a in baseline)
        ot = sum(optimized[a][h] for a in optimized)
        baseline_total_cost  += bt * hourly_tariff[h]
        optimized_total_cost += ot * hourly_tariff[h]
        baseline_peak  = max(baseline_peak,  bt)
        optimized_peak = max(optimized_peak, ot)

    savings    = baseline_total_cost - optimized_total_cost
    savings_pct = (savings / baseline_total_cost * 100.0) if baseline_total_cost > 0 else 0.0

    appliance_payload: List[ApplianceSchedule] = []
    candidate_actions: List[Dict[str, Any]] = []

    for appliance, base_vals in baseline.items():
        opt_vals = optimized[appliance]
        oo       = on_off_map[appliance]
        shifted  = 0.5 * sum(abs(opt_vals[h] - base_vals[h]) for h in range(horizon))

        rows: List[HourlyScheduleRow] = []
        for h in range(horizon):
            delta  = opt_vals[h] - base_vals[h]
            is_sched = appliance in schedulable
            action = _action_from_on_off(oo[h], base_vals[h]) if is_sched else "Continuous operation"
            rows.append(
                HourlyScheduleRow(
                    hour=h,
                    timestamp=timestamps[h],
                    tariff_php_per_kwh=hourly_tariff[h],
                    baseline_kwh=round(base_vals[h], 6),
                    optimized_kwh=round(opt_vals[h], 6),
                    delta_kwh=round(delta, 6),
                    action=action,
                    on_off=oo[h],
                )
            )
            if is_sched and not oo[h] and base_vals[h] > 0:
                candidate_actions.append({
                    "appliance": appliance,
                    "hour": h,
                    "kwh_saved": base_vals[h],
                    "cost_saved": base_vals[h] * hourly_tariff[h],
                    "message": (
                        f"Turn off {appliance.replace('_', ' ')} at {h:02d}:00 "
                        f"to stay within budget (saves ₱{base_vals[h] * hourly_tariff[h]:.2f})."
                    ),
                })

        appliance_payload.append(
            ApplianceSchedule(
                appliance=appliance,
                schedulable=appliance in schedulable,
                baseline_total_kwh=round(sum(base_vals), 6),
                optimized_total_kwh=round(sum(opt_vals), 6),
                shifted_kwh=round(shifted, 6),
                hourly=rows,
            )
        )

    candidate_actions.sort(key=lambda x: x["cost_saved"], reverse=True)
    top_actions = [c["message"] for c in candidate_actions[:5]]

    tbs = build_time_block_summary(appliance_payload)

    summary = {
        "status": "ok",
        "mode": "binary",
        "solver_status": status,
        "estimated_savings_php": round(savings, 4),
        "estimated_savings_pct": round(savings_pct, 2),
        "peak_reduction_kwh": round(baseline_peak - optimized_peak, 6),
        "top_actions": top_actions,
        "time_block_summary": tbs,
    }

    return ScheduleResult(
        forecast_date=forecast_date,
        generated_at=generated_at,
        status="ok",
        solver="cbc-binary",
        objective=round(float(pulp.value(problem.objective) or 0.0), 6),
        baseline_total_cost_php=round(baseline_total_cost, 4),
        optimized_total_cost_php=round(optimized_total_cost, 4),
        estimated_savings_php=round(savings, 4),
        estimated_savings_pct=round(savings_pct, 2),
        baseline_peak_kwh=round(baseline_peak, 6),
        optimized_peak_kwh=round(optimized_peak, 6),
        peak_reduction_kwh=round(baseline_peak - optimized_peak, 6),
        tariff_by_hour=hourly_tariff,
        appliances=appliance_payload,
        optimization_summary=summary,
        time_block_summary=tbs,
    )


# =============================================================================
# Legacy continuous load-shifting MILP
# =============================================================================

def _solve_continuous(
    baseline: Dict[str, List[float]],
    timestamps: List[str],
    hourly_tariff: List[float],
    forecast_date: str,
    generated_at: str,
    appliance_rules: Dict[str, Dict[str, Any]],
    comfort_penalty: Dict[str, float],
    max_shift_default: int,
    peak_penalty: float,
    horizon: int,
) -> ScheduleResult:
    """Legacy continuous load-shifting solver (pre-MILP.md behaviour)."""
    problem = pulp.LpProblem("appliance_scheduling_continuous", pulp.LpMinimize)
    peak_var = pulp.LpVariable("peak_total_kwh", lowBound=0)

    schedulable_appliances: List[str] = []
    x_vars: Dict[tuple[str, int], pulp.LpVariable] = {}
    y_vars: Dict[tuple[str, int, int], pulp.LpVariable] = {}
    dev_pos_vars: Dict[tuple[str, int], pulp.LpVariable] = {}
    dev_neg_vars: Dict[tuple[str, int], pulp.LpVariable] = {}

    for appliance, base_vals in baseline.items():
        rule = appliance_rules.get(appliance, {})
        schedulable = bool(rule.get("schedulable", appliance != "refrigerator"))
        if not schedulable:
            continue

        schedulable_appliances.append(appliance)
        allowed_hours = set(int(h) for h in rule.get("allowed_hours", list(range(horizon))))
        for hour, val in enumerate(base_vals):
            if val > 0:
                allowed_hours.add(hour)

        max_shift = int(rule.get("max_shift_hours", max_shift_default))

        for h in range(horizon):
            x_vars[(appliance, h)] = pulp.LpVariable(f"x_{appliance}_{h}", lowBound=0)
            dev_pos_vars[(appliance, h)] = pulp.LpVariable(f"dev_pos_{appliance}_{h}", lowBound=0)
            dev_neg_vars[(appliance, h)] = pulp.LpVariable(f"dev_neg_{appliance}_{h}", lowBound=0)

        for source_h in range(horizon):
            for target_h in range(horizon):
                if target_h not in allowed_hours:
                    continue
                if abs(target_h - source_h) > max_shift:
                    continue
                y_vars[(appliance, source_h, target_h)] = pulp.LpVariable(
                    f"y_{appliance}_{source_h}_{target_h}", lowBound=0
                )

        for source_h in range(horizon):
            outgoing = [
                y_vars[(appliance, source_h, target_h)]
                for target_h in range(horizon)
                if (appliance, source_h, target_h) in y_vars
            ]
            if outgoing:
                problem += pulp.lpSum(outgoing) == base_vals[source_h], f"source_balance_{appliance}_{source_h}"
            else:
                problem += base_vals[source_h] == 0, f"source_empty_{appliance}_{source_h}"

        for target_h in range(horizon):
            incoming = [
                y_vars[(appliance, source_h, target_h)]
                for source_h in range(horizon)
                if (appliance, source_h, target_h) in y_vars
            ]
            if incoming:
                problem += x_vars[(appliance, target_h)] == pulp.lpSum(incoming), f"target_balance_{appliance}_{target_h}"
            else:
                problem += x_vars[(appliance, target_h)] == 0, f"target_zero_{appliance}_{target_h}"

            problem += (
                x_vars[(appliance, target_h)] - base_vals[target_h]
                == dev_pos_vars[(appliance, target_h)] - dev_neg_vars[(appliance, target_h)]
            ), f"dev_balance_{appliance}_{target_h}"

    total_cost_terms = []
    comfort_terms = []

    for h in range(horizon):
        base_non_sched = sum(
            baseline[a][h] for a in baseline if a not in schedulable_appliances
        )
        controlled_load = pulp.lpSum(
            x_vars[(a, h)] for a in schedulable_appliances
        ) if schedulable_appliances else 0
        total_load_h = base_non_sched + controlled_load
        problem += peak_var >= total_load_h, f"peak_cap_{h}"
        total_cost_terms.append(hourly_tariff[h] * total_load_h)

    for appliance in schedulable_appliances:
        penalty = float(comfort_penalty.get(appliance, 0.0))
        for h in range(horizon):
            comfort_terms.append(penalty * (dev_pos_vars[(appliance, h)] + dev_neg_vars[(appliance, h)]))

    problem += pulp.lpSum(total_cost_terms) + (peak_penalty * peak_var) + pulp.lpSum(comfort_terms)

    try:
        solver = pulp.PULP_CBC_CMD(msg=False)
        problem.solve(solver)
    except Exception as exc:
        return _build_fallback_result(
            forecast_date=forecast_date,
            generated_at=generated_at,
            baseline=baseline,
            timestamps=timestamps,
            hourly_tariff=hourly_tariff,
            reason=f"Solver failed: {exc}",
        )

    status = pulp.LpStatus.get(problem.status, "Unknown")
    if status not in {"Optimal", "Feasible"}:
        return _build_fallback_result(
            forecast_date=forecast_date,
            generated_at=generated_at,
            baseline=baseline,
            timestamps=timestamps,
            hourly_tariff=hourly_tariff,
            reason=f"Solver status: {status}",
        )

    optimized: Dict[str, List[float]] = {}
    for appliance, base_vals in baseline.items():
        if appliance in schedulable_appliances:
            optimized[appliance] = [
                max(0.0, float(pulp.value(x_vars[(appliance, h)]) or 0.0))
                for h in range(horizon)
            ]
        else:
            optimized[appliance] = list(base_vals)

    on_off_map: Dict[str, List[bool]] = {
        a: [True] * horizon for a in optimized
    }

    baseline_total_cost = 0.0
    optimized_total_cost = 0.0
    baseline_peak = 0.0
    optimized_peak = 0.0
    for h in range(horizon):
        base_total_h = sum(baseline[a][h] for a in baseline)
        opt_total_h  = sum(optimized[a][h] for a in optimized)
        baseline_total_cost  += base_total_h * hourly_tariff[h]
        optimized_total_cost += opt_total_h  * hourly_tariff[h]
        baseline_peak  = max(baseline_peak,  base_total_h)
        optimized_peak = max(optimized_peak, opt_total_h)

    savings     = baseline_total_cost - optimized_total_cost
    savings_pct = (savings / baseline_total_cost * 100.0) if baseline_total_cost > 0 else 0.0

    appliance_payload: List[ApplianceSchedule] = []
    candidate_actions: List[Dict[str, Any]] = []
    for appliance, base_vals in baseline.items():
        opt_vals = optimized[appliance]
        shifted  = 0.5 * sum(abs(opt_vals[h] - base_vals[h]) for h in range(horizon))
        rows: List[HourlyScheduleRow] = []
        for h in range(horizon):
            delta = opt_vals[h] - base_vals[h]
            rows.append(
                HourlyScheduleRow(
                    hour=h,
                    timestamp=timestamps[h],
                    tariff_php_per_kwh=hourly_tariff[h],
                    baseline_kwh=round(base_vals[h], 6),
                    optimized_kwh=round(opt_vals[h], 6),
                    delta_kwh=round(delta, 6),
                    action=_action_from_delta(delta),
                    on_off=on_off_map[appliance][h],
                )
            )
            if delta <= -0.03:
                candidate_actions.append({
                    "appliance": appliance,
                    "hour": h,
                    "kwh_reduction": abs(delta),
                    "tariff": hourly_tariff[h],
                    "message": f"Reduce {appliance.replace('_', ' ')} around {h:02d}:00 (high-cost slot).",
                })

        appliance_payload.append(
            ApplianceSchedule(
                appliance=appliance,
                schedulable=appliance in schedulable_appliances,
                baseline_total_kwh=round(sum(base_vals), 6),
                optimized_total_kwh=round(sum(opt_vals), 6),
                shifted_kwh=round(shifted, 6),
                hourly=rows,
            )
        )

    candidate_actions.sort(key=lambda x: (x["tariff"], x["kwh_reduction"]), reverse=True)
    top_actions = [c["message"] for c in candidate_actions[:5]]

    tbs = build_time_block_summary(appliance_payload)

    summary = {
        "status": "ok",
        "mode": "continuous",
        "solver_status": status,
        "estimated_savings_php": round(savings, 4),
        "estimated_savings_pct": round(savings_pct, 2),
        "peak_reduction_kwh": round(baseline_peak - optimized_peak, 6),
        "top_actions": top_actions,
        "time_block_summary": tbs,
    }

    return ScheduleResult(
        forecast_date=forecast_date,
        generated_at=generated_at,
        status="ok",
        solver="cbc",
        objective=round(float(pulp.value(problem.objective) or 0.0), 6),
        baseline_total_cost_php=round(baseline_total_cost, 4),
        optimized_total_cost_php=round(optimized_total_cost, 4),
        estimated_savings_php=round(savings, 4),
        estimated_savings_pct=round(savings_pct, 2),
        baseline_peak_kwh=round(baseline_peak, 6),
        optimized_peak_kwh=round(optimized_peak, 6),
        peak_reduction_kwh=round(baseline_peak - optimized_peak, 6),
        tariff_by_hour=hourly_tariff,
        appliances=appliance_payload,
        optimization_summary=summary,
        time_block_summary=tbs,
    )


# =============================================================================
# Public entry point
# =============================================================================

def optimize_schedule(
    appliance_forecasts: Dict[str, "ApplianceForecast"],
    forecast_date: str,
    generated_at: str,
    base_tariff: float,
    appliance_rules: Dict[str, Dict[str, Any]],
    comfort_penalty: Dict[str, float],
    tariff_multipliers: Dict[str, float],
    max_shift_default: int = 3,
    peak_penalty: float = 1.0,
    horizon: int = 24,
    budget_constraint_php: Optional[float] = None,
    binary_mode: bool = True,
) -> ScheduleResult:
    """
    Solve an MILP schedule from per-appliance 24-hour forecast energy.

    Parameters
    ----------
    budget_constraint_php : float, optional
        Hard daily budget cap (PHP). When set in binary_mode, the solver will
        choose which hours to keep ON/OFF so total cost stays ≤ this limit.
    binary_mode : bool
        True  → binary ON/OFF per MILP.md (default)
        False → legacy continuous load-shifting
    """
    baseline, timestamps = _baseline_from_forecasts(appliance_forecasts, horizon)
    hourly_tariff = _build_hourly_tariff(base_tariff, tariff_multipliers, horizon)

    if not baseline:
        return _build_fallback_result(
            forecast_date=forecast_date,
            generated_at=generated_at,
            baseline={},
            timestamps=timestamps,
            hourly_tariff=hourly_tariff,
            reason="No baseline forecasts available.",
        )

    if pulp is None:
        return _build_fallback_result(
            forecast_date=forecast_date,
            generated_at=generated_at,
            baseline=baseline,
            timestamps=timestamps,
            hourly_tariff=hourly_tariff,
            reason="pulp is not installed.",
        )

    if binary_mode:
        return _solve_binary(
            baseline=baseline,
            timestamps=timestamps,
            hourly_tariff=hourly_tariff,
            forecast_date=forecast_date,
            generated_at=generated_at,
            appliance_rules=appliance_rules,
            budget_constraint_php=budget_constraint_php,
            horizon=horizon,
        )
    else:
        return _solve_continuous(
            baseline=baseline,
            timestamps=timestamps,
            hourly_tariff=hourly_tariff,
            forecast_date=forecast_date,
            generated_at=generated_at,
            appliance_rules=appliance_rules,
            comfort_penalty=comfort_penalty,
            max_shift_default=max_shift_default,
            peak_penalty=peak_penalty,
            horizon=horizon,
        )
