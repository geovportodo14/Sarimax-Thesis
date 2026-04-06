#!/usr/bin/env python3
"""
forecasting/eval_budget_stress.py
===================================
Budget stress-test for the MILP scheduling optimizer.

For each day in the test period (Feb 25 – Mar 10, 2026):
  1. Load the SARIMAX baseline forecast from the existing _schedule.json
     (baseline_kwh per appliance per hour + tariff_by_hour)
  2. Compute baseline_cost  = Σ energy × tariff  (this is the 100% reference)
  3. For each budget level  [100%, 75%, 50%, 25%, 10%]  (and optionally lower):
       budget_php = baseline_cost × (pct / 100)
       Run MILP optimizer with that budget
       Record status, savings, ON-hours retained, peak reduction
  4. Find the "breaking point" per day = lowest budget_pct where solver still
     returns Optimal / Feasible (not fallback)

The SARIMAX forecasts are treated as fixed inputs — only the budget changes.
No pipeline re-runs needed; reconstruction is done entirely from _schedule.json.

Outputs:
    outputs/eval_budget_stress_raw.csv       — one row per (date, budget_pct)
    outputs/eval_budget_stress_summary.json  — aggregate stats per budget_pct

Usage:
    python eval_budget_stress.py
    python eval_budget_stress.py --start 2026-02-25 --end 2026-03-10
    python eval_budget_stress.py --levels 100,75,50,25,10,5
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))

from forecasting.config import OUTPUTS_DIR, SCHEDULER_APPLIANCE_RULES, PipelineConfig
from forecasting.pipeline.scheduler import _solve_binary  # type: ignore[attr-defined]

DEFAULT_START  = "2026-02-25"
DEFAULT_END    = "2026-03-10"

# Budget levels as percentages of the forecasted baseline cost
DEFAULT_LEVELS = [100, 75, 50, 25, 10]


# ---------------------------------------------------------------------------
# Reconstruction from _schedule.json
# ---------------------------------------------------------------------------

def load_schedule_json(date_str: str, outputs_dir: Path) -> Optional[Dict[str, Any]]:
    path = outputs_dir / date_str / "_schedule.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def extract_baseline(schedule: Dict[str, Any]) -> Tuple[
    Dict[str, List[float]],   # baseline energy per appliance
    List[str],                 # timestamps
    List[float],               # hourly tariff
    float,                     # pre-computed baseline cost (cross-check)
]:
    """Reconstruct MILP inputs from _schedule.json baseline hourly data."""
    baseline: Dict[str, List[float]] = {}
    timestamps: List[str] = []

    for app in schedule.get("appliances", []):
        name   = app["appliance"]
        hourly = app["hourly"]
        baseline[name] = [row["baseline_kwh"] for row in hourly]

        if not timestamps:
            timestamps = [row["timestamp"] for row in hourly]

    hourly_tariff: List[float] = schedule.get("tariff_by_hour", [])
    baseline_cost: float       = schedule.get("baseline_total_cost_php", 0.0)

    return baseline, timestamps, hourly_tariff, baseline_cost


# ---------------------------------------------------------------------------
# ON-hours retention helper (mirrors eval_schedule_results.py)
# ---------------------------------------------------------------------------

def _on_hours_pct(result_appliances: List[Any], baseline: Dict[str, List[float]]) -> Optional[float]:
    eligible = 0
    retained = 0
    for app in result_appliances:
        if not app.schedulable:
            continue
        for row in app.hourly:
            if baseline.get(app.appliance, [0.0] * 24)[row.hour] > 0:
                eligible += 1
                if row.on_off:
                    retained += 1
    if eligible == 0:
        return None
    return round(retained / eligible * 100.0, 2)


# ---------------------------------------------------------------------------
# Single-day, single-budget run
# ---------------------------------------------------------------------------

def run_single(
    date_str: str,
    budget_pct: float,
    baseline: Dict[str, List[float]],
    timestamps: List[str],
    hourly_tariff: List[float],
    baseline_cost: float,
    appliance_rules: Dict[str, Any],
) -> Dict[str, Any]:
    budget_php = round(baseline_cost * (budget_pct / 100.0), 4)

    result = _solve_binary(
        baseline=baseline,
        timestamps=timestamps,
        hourly_tariff=hourly_tariff,
        forecast_date=date_str,
        generated_at="eval_budget_stress",
        appliance_rules=appliance_rules,
        budget_constraint_php=budget_php,
        horizon=len(hourly_tariff),
    )

    on_pct = _on_hours_pct(result.appliances, baseline)

    return {
        "date":                  date_str,
        "budget_pct":            budget_pct,
        "budget_php":            budget_php,
        "baseline_cost_php":     round(baseline_cost, 4),
        "optimized_cost_php":    round(result.optimized_total_cost_php, 4),
        "savings_php":           round(result.estimated_savings_php, 4),
        "savings_pct":           round(result.estimated_savings_pct, 2),
        "peak_reduction_kwh":    round(result.peak_reduction_kwh, 6),
        "on_hours_retained_pct": on_pct,
        "solver_status":         result.status,   # "ok" or "fallback"
        "solver":                result.solver,
        "budget_met":            bool(result.optimized_total_cost_php <= budget_php),
    }


# ---------------------------------------------------------------------------
# Per-date stress test
# ---------------------------------------------------------------------------

def stress_test_date(
    date_str: str,
    budget_levels: List[float],
    outputs_dir: Path,
    appliance_rules: Dict[str, Any],
) -> List[Dict[str, Any]]:
    schedule = load_schedule_json(date_str, outputs_dir)
    if schedule is None:
        return [{"date": date_str, "budget_pct": lvl, "error": "missing _schedule.json"} for lvl in budget_levels]

    if schedule.get("status") == "fallback":
        return [{"date": date_str, "budget_pct": lvl, "error": "original schedule was fallback"} for lvl in budget_levels]

    baseline, timestamps, hourly_tariff, baseline_cost = extract_baseline(schedule)

    if baseline_cost <= 0:
        return [{"date": date_str, "budget_pct": lvl, "error": "zero baseline cost"} for lvl in budget_levels]

    rows: List[Dict[str, Any]] = []
    for pct in budget_levels:
        row = run_single(
            date_str=date_str,
            budget_pct=pct,
            baseline=baseline,
            timestamps=timestamps,
            hourly_tariff=hourly_tariff,
            baseline_cost=baseline_cost,
            appliance_rules=appliance_rules,
        )
        rows.append(row)

    return rows


# ---------------------------------------------------------------------------
# Breaking point analysis
# ---------------------------------------------------------------------------

def find_breaking_point(day_rows: List[Dict[str, Any]]) -> Optional[float]:
    """
    Lowest budget_pct level where the solver still returned 'ok'.
    Returns None if no level succeeded, or if all levels succeeded.
    """
    ok_levels    = [r["budget_pct"] for r in day_rows if r.get("solver_status") == "ok"]
    fail_levels  = [r["budget_pct"] for r in day_rows if r.get("solver_status") == "fallback"]
    if not ok_levels or not fail_levels:
        return None
    return min(ok_levels)


# ---------------------------------------------------------------------------
# Aggregate per budget level
# ---------------------------------------------------------------------------

def aggregate_by_level(all_rows: List[Dict[str, Any]], budget_levels: List[float]) -> List[Dict[str, Any]]:
    agg_rows: List[Dict[str, Any]] = []

    for pct in budget_levels:
        level_rows = [r for r in all_rows if r.get("budget_pct") == pct and "error" not in r]
        ok_rows    = [r for r in level_rows if r.get("solver_status") == "ok"]
        n_total    = len(level_rows)
        n_ok       = len(ok_rows)

        if n_total == 0:
            continue

        def _stat(key: str) -> Dict[str, float]:
            vals = [r[key] for r in ok_rows if r.get(key) is not None]
            if not vals:
                return {"mean": float("nan"), "std": float("nan")}
            arr = np.array(vals, dtype=float)
            return {"mean": round(float(np.mean(arr)), 4), "std": round(float(np.std(arr)), 4)}

        on_hrs_vals = [r["on_hours_retained_pct"] for r in ok_rows if r.get("on_hours_retained_pct") is not None]

        agg_rows.append({
            "budget_pct":             pct,
            "n_days_total":           n_total,
            "n_days_solver_ok":       n_ok,
            "n_days_fallback":        n_total - n_ok,
            "solver_success_rate_pct": round(n_ok / n_total * 100.0, 1),
            "savings_php":            _stat("savings_php"),
            "savings_pct":            _stat("savings_pct"),
            "peak_reduction_kwh":     _stat("peak_reduction_kwh"),
            "on_hours_retained_pct": {
                "mean": round(float(np.mean(on_hrs_vals)), 2) if on_hrs_vals else float("nan"),
                "std":  round(float(np.std(on_hrs_vals)),  2) if on_hrs_vals else float("nan"),
            },
        })

    return agg_rows


# ---------------------------------------------------------------------------
# Report printer
# ---------------------------------------------------------------------------

def print_report(agg_by_level: List[Dict[str, Any]], all_rows: List[Dict[str, Any]], date_range: pd.DatetimeIndex) -> None:
    print()
    print("=" * 80)
    print("  BUDGET STRESS-TEST — MILP OPTIMIZER EVALUATION")
    print("=" * 80)
    print(f"  Test period : {date_range[0].date()} → {date_range[-1].date()} ({len(date_range)} days)")
    print()

    # Summary table by budget level
    print(f"  {'BUDGET%':>8}  {'SUCCESS':>8}  {'SAVINGS(mean)':>14}  {'SAVINGS%(mean)':>15}  {'ON-HRS%(mean)':>14}  {'PEAK-RED(mean)':>14}")
    print("  " + "-" * 76)

    for row in agg_by_level:
        pct      = row["budget_pct"]
        rate     = row["solver_success_rate_pct"]
        sav_php  = row["savings_php"]["mean"]
        sav_pct  = row["savings_pct"]["mean"]
        on_hrs   = row["on_hours_retained_pct"]["mean"]
        peak_red = row["peak_reduction_kwh"]["mean"]

        ok_str   = f"{row['n_days_solver_ok']}/{row['n_days_total']} ({rate:.0f}%)"
        sav_str  = f"₱{sav_php:.2f}" if not np.isnan(sav_php) else "—"
        sp_str   = f"{sav_pct:.1f}%"   if not np.isnan(sav_pct) else "—"
        oh_str   = f"{on_hrs:.1f}%"    if not np.isnan(on_hrs)  else "—"
        pr_str   = f"{peak_red:.4f}"   if not np.isnan(peak_red) else "—"

        print(f"  {pct:>7.0f}%  {ok_str:>8}  {sav_str:>14}  {sp_str:>15}  {oh_str:>14}  {pr_str:>14}")

    # Breaking point summary across all days
    print()
    print("  BREAKING POINT ANALYSIS (per day)")
    print("  " + "-" * 52)

    dates = [ts.strftime("%Y-%m-%d") for ts in date_range]
    for date_str in dates:
        day_rows = [r for r in all_rows if r.get("date") == date_str and "error" not in r]
        bp = find_breaking_point(day_rows)
        if not day_rows:
            bp_str = "no data"
        elif bp is None:
            ok_all = all(r.get("solver_status") == "ok" for r in day_rows)
            bp_str = "all levels OK" if ok_all else "all levels FAILED"
        else:
            bp_str = f"breaks below {bp:.0f}% budget"
        print(f"  {date_str}  {bp_str}")

    print("=" * 80)
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Budget stress-test for MILP optimizer (thesis evaluation)."
    )
    parser.add_argument("--start",   default=DEFAULT_START,
                        help="Start date YYYY-MM-DD")
    parser.add_argument("--end",     default=DEFAULT_END,
                        help="End date YYYY-MM-DD (inclusive)")
    parser.add_argument("--levels",  default=",".join(str(x) for x in DEFAULT_LEVELS),
                        help=f"Comma-separated budget percentages (default: {DEFAULT_LEVELS})")
    parser.add_argument("--json-out", default="",
                        help="Optional path to save full JSON report.")
    args = parser.parse_args()

    budget_levels = [float(x) for x in args.levels.split(",")]
    budget_levels = sorted(set(budget_levels), reverse=True)  # descending

    date_range = pd.date_range(start=args.start, end=args.end, freq="D")
    cfg        = PipelineConfig()

    all_rows: List[Dict[str, Any]] = []

    print(f"\nRunning budget stress-test over {len(date_range)} days × {len(budget_levels)} budget levels …")

    for ts in date_range:
        date_str = ts.strftime("%Y-%m-%d")
        rows = stress_test_date(
            date_str=date_str,
            budget_levels=budget_levels,
            outputs_dir=OUTPUTS_DIR,
            appliance_rules=cfg.scheduler_appliance_rules,
        )
        all_rows.extend(rows)
        # Quick per-day summary to console
        ok_count = sum(1 for r in rows if r.get("solver_status") == "ok")
        err      = next((r.get("error") for r in rows if "error" in r), None)
        if err:
            print(f"  {date_str}  ERROR: {err}")
        else:
            print(f"  {date_str}  solver_ok={ok_count}/{len(rows)} levels")

    agg_by_level = aggregate_by_level(all_rows, budget_levels)
    print_report(agg_by_level, all_rows, date_range)

    # Save raw CSV (one row per date × budget_pct)
    raw_csv_path = OUTPUTS_DIR / "eval_budget_stress_raw.csv"
    pd.DataFrame(all_rows).to_csv(raw_csv_path, index=False)
    print(f"  Raw CSV saved      : {raw_csv_path}")

    # Save summary JSON
    summary = {
        "start_date":     args.start,
        "end_date":       args.end,
        "budget_levels":  budget_levels,
        "n_days":         len(date_range),
        "aggregate_by_budget_pct": agg_by_level,
        "raw_rows":       all_rows,
    }
    default_json = OUTPUTS_DIR / "eval_budget_stress_summary.json"
    json_out_path = Path(args.json_out) if args.json_out else default_json
    json_out_path.parent.mkdir(parents=True, exist_ok=True)
    json_out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"  Summary JSON saved : {json_out_path}")
    print()


if __name__ == "__main__":
    main()
