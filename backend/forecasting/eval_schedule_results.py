#!/usr/bin/env python3
"""
forecasting/eval_schedule_results.py
======================================
Aggregate scheduling evaluation for thesis.

Reads every _schedule.json + _run_manifest.json in the test-period
output folders and computes:

  Per-day metrics:
    • baseline_cost_php, optimized_cost_php, savings_php, savings_pct
    • budget_met  (optimized cost ≤ daily budget)
    • peak_reduction_kwh
    • on_hours_retained_pct  (schedulable appliances only)
    • solver_status  (Optimal / Feasible / fallback)

  Aggregate metrics (mean ± std over all valid days):
    • All of the above
    • solver_success_rate, fallback_rate, budget_adherence_rate

Outputs:
    outputs/eval_schedule_daily.csv
    outputs/eval_schedule_summary.json

Usage:
    python eval_schedule_results.py
    python eval_schedule_results.py --start 2026-02-25 --end 2026-03-10
    python eval_schedule_results.py --json-out path/to/report.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))

from forecasting.config import DEFAULT_DAILY_BUDGET_PHP, OUTPUTS_DIR

DEFAULT_START = "2026-02-25"
DEFAULT_END   = "2026-03-10"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _compute_on_hours_retention(appliances: List[Dict[str, Any]]) -> Optional[float]:
    """
    ON-hours retention for schedulable appliances.

    = Σ(hours where on_off=True) / Σ(hours where a b_var existed)
    A b_var exists when: hour is in allowed_hours AND baseline_kwh > 0.
    Since the schedule already encodes this (off-budget hours have on_off=False,
    hours outside allowed_hours also have on_off=False and baseline_kwh>0 is
    encoded in the original forecast), we use:

        eligible = hourly rows where schedulable=True and baseline_kwh > 0
        retained = eligible rows where on_off=True
    """
    eligible = 0
    retained = 0

    for app in appliances:
        if not app.get("schedulable", False):
            continue
        for row in app.get("hourly", []):
            if row.get("baseline_kwh", 0.0) > 0:
                eligible += 1
                if row.get("on_off", False):
                    retained += 1

    if eligible == 0:
        return None
    return round(retained / eligible * 100.0, 2)


# ---------------------------------------------------------------------------
# Per-day evaluation
# ---------------------------------------------------------------------------

def evaluate_date(
    date_str: str,
    outputs_dir: Path,
    daily_budget: float,
) -> Optional[Dict[str, Any]]:
    schedule_path = outputs_dir / date_str / "_schedule.json"
    manifest_path = outputs_dir / date_str / "_run_manifest.json"

    if not schedule_path.exists():
        return {"date": date_str, "error": "missing _schedule.json"}
    if not manifest_path.exists():
        return {"date": date_str, "error": "missing _run_manifest.json"}

    sched    = _load_json(schedule_path)
    manifest = _load_json(manifest_path)

    if sched is None:
        return {"date": date_str, "error": "could not parse _schedule.json"}

    status  = sched.get("status", "unknown")
    solver  = sched.get("solver", "unknown")

    baseline_cost  = sched.get("baseline_total_cost_php", 0.0)
    optimized_cost = sched.get("optimized_total_cost_php", 0.0)
    savings_php    = sched.get("estimated_savings_php", 0.0)
    savings_pct    = sched.get("estimated_savings_pct", 0.0)
    peak_base      = sched.get("baseline_peak_kwh", 0.0)
    peak_opt       = sched.get("optimized_peak_kwh", 0.0)
    peak_reduction = sched.get("peak_reduction_kwh", 0.0)

    # Budget adherence
    budget_met = bool(optimized_cost <= daily_budget)

    # ON-hours retention
    on_hours_pct = _compute_on_hours_retention(sched.get("appliances", []))

    # Appliance-level totals
    app_rows: List[Dict[str, Any]] = []
    for app in sched.get("appliances", []):
        app_rows.append({
            "date":                   date_str,
            "appliance":              app.get("appliance"),
            "schedulable":            app.get("schedulable"),
            "baseline_total_kwh":     app.get("baseline_total_kwh"),
            "optimized_total_kwh":    app.get("optimized_total_kwh"),
            "shifted_kwh":            app.get("shifted_kwh"),
        })

    # Forecast ok/failed counts from manifest
    forecast_ok     = manifest.get("ok",     0) if manifest else None
    forecast_failed = manifest.get("failed", 0) if manifest else None

    return {
        "date":               date_str,
        "status":             status,
        "solver":             solver,
        "baseline_cost_php":  round(baseline_cost,  4),
        "optimized_cost_php": round(optimized_cost, 4),
        "savings_php":        round(savings_php,    4),
        "savings_pct":        round(savings_pct,    2),
        "daily_budget_php":   daily_budget,
        "budget_met":         budget_met,
        "baseline_peak_kwh":  round(peak_base,      6),
        "optimized_peak_kwh": round(peak_opt,       6),
        "peak_reduction_kwh": round(peak_reduction, 6),
        "on_hours_retained_pct": on_hours_pct,
        "forecast_ok":        forecast_ok,
        "forecast_failed":    forecast_failed,
        "appliance_detail":   app_rows,
        "error":              None,
    }


# ---------------------------------------------------------------------------
# Aggregate
# ---------------------------------------------------------------------------

def _mean_std(values: List[float]) -> Dict[str, float]:
    arr = np.array([v for v in values if v is not None and np.isfinite(v)])
    if len(arr) == 0:
        return {"mean": float("nan"), "std": float("nan"), "min": float("nan"), "max": float("nan")}
    return {
        "mean": round(float(np.mean(arr)), 4),
        "std":  round(float(np.std(arr)),  4),
        "min":  round(float(np.min(arr)),  4),
        "max":  round(float(np.max(arr)),  4),
    }


def compute_aggregate(daily_rows: List[Dict[str, Any]], daily_budget: float) -> Dict[str, Any]:
    valid = [r for r in daily_rows if r.get("error") is None and r.get("status") in ("ok", "Optimal", "Feasible")]
    n_valid   = len(valid)
    n_total   = len(daily_rows)
    n_errors  = sum(1 for r in daily_rows if r.get("error") is not None)
    n_fallback = sum(1 for r in daily_rows if r.get("status") == "fallback")

    if n_valid == 0:
        return {
            "n_total": n_total, "n_valid": 0, "n_errors": n_errors,
            "n_fallback": n_fallback, "note": "No valid days to aggregate."
        }

    savings_php    = [r["savings_php"]            for r in valid]
    savings_pct    = [r["savings_pct"]            for r in valid]
    budget_met     = [1.0 if r["budget_met"] else 0.0 for r in valid]
    peak_reduction = [r["peak_reduction_kwh"]     for r in valid]
    on_hours       = [r["on_hours_retained_pct"]  for r in valid if r["on_hours_retained_pct"] is not None]
    baseline_costs = [r["baseline_cost_php"]      for r in valid]
    optimized_costs = [r["optimized_cost_php"]    for r in valid]

    total_baseline_cost  = round(sum(baseline_costs), 4)
    total_optimized_cost = round(sum(optimized_costs), 4)
    total_savings        = round(total_baseline_cost - total_optimized_cost, 4)
    overall_savings_pct  = round(total_savings / total_baseline_cost * 100.0, 2) if total_baseline_cost > 0 else 0.0

    return {
        "test_period": {
            "n_total_days":   n_total,
            "n_valid_days":   n_valid,
            "n_error_days":   n_errors,
            "n_fallback_days": n_fallback,
            "solver_success_rate_pct":  round(n_valid / n_total * 100.0, 1),
            "fallback_rate_pct":        round(n_fallback / n_total * 100.0, 1),
        },
        "cost_php": {
            "total_baseline_cost":   total_baseline_cost,
            "total_optimized_cost":  total_optimized_cost,
            "total_savings":         total_savings,
            "overall_savings_pct":   overall_savings_pct,
            "daily_savings_php":     _mean_std(savings_php),
            "daily_savings_pct":     _mean_std(savings_pct),
            "daily_baseline_cost":   _mean_std(baseline_costs),
            "daily_optimized_cost":  _mean_std(optimized_costs),
        },
        "budget_adherence": {
            "daily_budget_php":         daily_budget,
            "budget_adherence_rate_pct": round(float(np.mean(budget_met)) * 100.0, 1),
            "days_within_budget":       int(sum(budget_met)),
            "days_over_budget":         int(n_valid - sum(budget_met)),
        },
        "peak_reduction_kwh": _mean_std(peak_reduction),
        "on_hours_retained_pct": _mean_std(on_hours) if on_hours else {"note": "no schedulable data"},
    }


# ---------------------------------------------------------------------------
# Report printer
# ---------------------------------------------------------------------------

def print_report(daily_rows: List[Dict[str, Any]], agg: Dict[str, Any]) -> None:
    print()
    print("=" * 72)
    print("  OFFLINE SCHEDULING EVALUATION — THESIS REPORT")
    print("=" * 72)

    # Header
    print(f"  {'DATE':<12} {'STATUS':<10} {'BASELINE':>10} {'OPTIMIZED':>10} {'SAVINGS':>8} {'SAVED%':>7} {'BUDGET':>7} {'PEAK-RED':>9} {'ON-HRS%':>8}")
    print("  " + "-" * 70)

    for r in daily_rows:
        if r.get("error"):
            print(f"  {r['date']:<12} ERROR — {r['error']}")
            continue
        budget_flag = "YES" if r["budget_met"] else "NO "
        on_hrs      = f"{r['on_hours_retained_pct']:.1f}" if r["on_hours_retained_pct"] is not None else "N/A"
        print(
            f"  {r['date']:<12} {r['status']:<10} "
            f"{r['baseline_cost_php']:>10.2f} {r['optimized_cost_php']:>10.2f} "
            f"{r['savings_php']:>8.2f} {r['savings_pct']:>6.1f}% "
            f"{budget_flag:>7} {r['peak_reduction_kwh']:>9.4f} {on_hrs:>8}"
        )

    print()
    print("─" * 72)
    print("  AGGREGATE SUMMARY")
    print("─" * 72)

    tp  = agg["test_period"]
    cost = agg["cost_php"]
    ba   = agg["budget_adherence"]
    pr   = agg["peak_reduction_kwh"]
    oh   = agg.get("on_hours_retained_pct", {})

    print(f"  Test days         : {tp['n_total_days']}  (valid={tp['n_valid_days']}, fallback={tp['n_fallback_days']}, error={tp['n_error_days']})")
    print(f"  Solver success    : {tp['solver_success_rate_pct']}%")
    print()
    print(f"  Total baseline cost   : ₱{cost['total_baseline_cost']:.2f}")
    print(f"  Total optimized cost  : ₱{cost['total_optimized_cost']:.2f}")
    print(f"  Total savings         : ₱{cost['total_savings']:.2f}  ({cost['overall_savings_pct']:.1f}%)")
    print(f"  Daily savings (mean)  : ₱{cost['daily_savings_php']['mean']:.2f} ± ₱{cost['daily_savings_php']['std']:.2f}")
    print(f"  Daily savings% (mean) : {cost['daily_savings_pct']['mean']:.1f}% ± {cost['daily_savings_pct']['std']:.1f}%")
    print()
    print(f"  Daily budget          : ₱{ba['daily_budget_php']:.2f}")
    print(f"  Budget adherence rate : {ba['budget_adherence_rate_pct']:.1f}%  ({ba['days_within_budget']}/{tp['n_valid_days']} days)")
    print()
    print(f"  Peak reduction (mean) : {pr['mean']:.4f} kWh ± {pr['std']:.4f}")
    if "mean" in oh:
        print(f"  ON-hours retained     : {oh['mean']:.1f}% ± {oh['std']:.1f}%")
    print("=" * 72)
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Aggregate offline scheduling evaluation for thesis."
    )
    parser.add_argument("--start",    default=DEFAULT_START, help="Start date YYYY-MM-DD")
    parser.add_argument("--end",      default=DEFAULT_END,   help="End date YYYY-MM-DD (inclusive)")
    parser.add_argument("--budget",   type=float, default=DEFAULT_DAILY_BUDGET_PHP,
                        help=f"Daily budget PHP (default: {DEFAULT_DAILY_BUDGET_PHP})")
    parser.add_argument("--json-out", type=str, default="",
                        help="Optional path to save full JSON report.")
    args = parser.parse_args()

    date_range = pd.date_range(start=args.start, end=args.end, freq="D")
    daily_rows: List[Dict[str, Any]] = []
    all_appliance_rows: List[Dict[str, Any]] = []

    for ts in date_range:
        date_str = ts.strftime("%Y-%m-%d")
        row = evaluate_date(date_str, OUTPUTS_DIR, args.budget)
        if row:
            all_appliance_rows.extend(row.pop("appliance_detail", []))
            daily_rows.append(row)

    agg = compute_aggregate(daily_rows, args.budget)
    print_report(daily_rows, agg)

    # Save daily CSV
    daily_csv_path = OUTPUTS_DIR / "eval_schedule_daily.csv"
    pd.DataFrame(daily_rows).to_csv(daily_csv_path, index=False)
    print(f"  Daily CSV saved : {daily_csv_path}")

    # Save appliance-level detail CSV
    detail_csv_path = OUTPUTS_DIR / "eval_schedule_appliance_detail.csv"
    pd.DataFrame(all_appliance_rows).to_csv(detail_csv_path, index=False)
    print(f"  Detail CSV saved: {detail_csv_path}")

    # Save summary JSON
    summary = {
        "start_date":  args.start,
        "end_date":    args.end,
        "daily_budget_php": args.budget,
        "aggregate":   agg,
        "daily":       daily_rows,
    }

    default_json = OUTPUTS_DIR / "eval_schedule_summary.json"
    json_out_path = Path(args.json_out) if args.json_out else default_json
    json_out_path.parent.mkdir(parents=True, exist_ok=True)
    json_out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"  Summary JSON    : {json_out_path}")
    print()


if __name__ == "__main__":
    main()
