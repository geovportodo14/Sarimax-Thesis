"""
forecasting/pipeline/scheduler.py
=================================
Post-forecast appliance scheduling using MILP.

This module runs AFTER SARIMAX forecasting. It takes hourly predicted energy
for each appliance and computes an optimized schedule that minimizes:
  - energy cost (using a simple TOU tariff profile)
  - peak hourly demand
  - comfort deviation from the forecast baseline
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, TYPE_CHECKING

import pandas as pd

try:
    import pulp
except Exception:  # pragma: no cover - handled gracefully at runtime
    pulp = None

if TYPE_CHECKING:
    from forecasting.pipeline.forecaster import ApplianceForecast


@dataclass
class HourlyScheduleRow:
    hour: int
    timestamp: str
    tariff_php_per_kwh: float
    baseline_kwh: float
    optimized_kwh: float
    delta_kwh: float
    action: str


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
                    "action": row.action,
                })
        return rows


def _build_hourly_tariff(base_tariff: float, multipliers: Dict[str, float], horizon: int) -> List[float]:
    off_peak_mult = float(multipliers.get("off_peak", 0.85))
    mid_mult = float(multipliers.get("mid", 1.0))
    peak_mult = float(multipliers.get("peak", 1.25))

    out: List[float] = []
    for hour in range(horizon):
        if 13 <= hour <= 17:
            out.append(round(base_tariff * peak_mult, 4))
        elif hour <= 5 or hour >= 22:
            out.append(round(base_tariff * off_peak_mult, 4))
        else:
            out.append(round(base_tariff * mid_mult, 4))
    return out


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
    )


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
) -> ScheduleResult:
    """
    Solve an MILP schedule from per-appliance 24-hour forecast energy.
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

    problem = pulp.LpProblem("appliance_scheduling", pulp.LpMinimize)
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
                    f"y_{appliance}_{source_h}_{target_h}",
                    lowBound=0,
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
            baseline[a][h]
            for a in baseline
            if a not in schedulable_appliances
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

    baseline_total_cost = 0.0
    optimized_total_cost = 0.0
    baseline_peak = 0.0
    optimized_peak = 0.0
    for h in range(horizon):
        base_total_h = sum(baseline[a][h] for a in baseline)
        opt_total_h = sum(optimized[a][h] for a in optimized)
        baseline_total_cost += base_total_h * hourly_tariff[h]
        optimized_total_cost += opt_total_h * hourly_tariff[h]
        baseline_peak = max(baseline_peak, base_total_h)
        optimized_peak = max(optimized_peak, opt_total_h)

    savings = baseline_total_cost - optimized_total_cost
    savings_pct = (savings / baseline_total_cost * 100.0) if baseline_total_cost > 0 else 0.0

    appliance_payload: List[ApplianceSchedule] = []
    candidate_actions: List[Dict[str, Any]] = []
    for appliance, base_vals in baseline.items():
        opt_vals = optimized[appliance]
        shifted = 0.5 * sum(abs(opt_vals[h] - base_vals[h]) for h in range(horizon))
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

    summary = {
        "status": "ok",
        "solver_status": status,
        "estimated_savings_php": round(savings, 4),
        "estimated_savings_pct": round(savings_pct, 2),
        "peak_reduction_kwh": round(baseline_peak - optimized_peak, 6),
        "top_actions": top_actions,
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
    )
