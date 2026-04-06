#!/usr/bin/env python3
"""
forecasting/eval_batch_runner.py
==================================
Offline batch scheduling runner for thesis evaluation.

Loops over every date in the test period (2026-02-25 → 2026-03-10),
runs the full SARIMAX + MILP pipeline for each date, and saves outputs
to outputs/YYYY-MM-DD/ exactly as production would.

History is loaded from MongoDB with a strict $lt:target_date filter,
so no future data leaks into any forecast or scheduling decision.

Usage:
    python eval_batch_runner.py
    python eval_batch_runner.py --start 2026-02-25 --end 2026-03-10
    python eval_batch_runner.py --force          # re-run even if output exists
    python eval_batch_runner.py --dry-run        # skip file/DB writes
"""

from __future__ import annotations

import argparse
import sys
import traceback
from pathlib import Path

import pandas as pd

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))

from forecasting.config import OUTPUTS_DIR, PipelineConfig
from forecasting.pipeline.logger import get_logger
from forecasting.run_pipeline import run_pipeline

log = get_logger("eval_batch_runner", _HERE / "logs")

# ---------------------------------------------------------------------------
# Default test-period dates (Feb 25 – Mar 10, 2026 inclusive)
# ---------------------------------------------------------------------------
DEFAULT_START = "2026-02-25"
DEFAULT_END   = "2026-03-10"


def _output_exists(outputs_dir: Path, date_str: str) -> bool:
    """Return True if this date already has a completed schedule output."""
    schedule_path = outputs_dir / date_str / "_schedule.json"
    manifest_path = outputs_dir / date_str / "_run_manifest.json"
    return schedule_path.exists() and manifest_path.exists()


def run_batch(
    start: str,
    end: str,
    force: bool = False,
    dry_run: bool = False,
    budget: float | None = None,
) -> None:
    date_range = pd.date_range(start=start, end=end, freq="D")
    total      = len(date_range)

    log.info("=" * 60)
    log.info("Offline Batch Scheduling Runner")
    log.info("Test period : %s → %s (%d days)", start, end, total)
    log.info("Force re-run: %s", force)
    log.info("Dry run     : %s", dry_run)
    log.info("=" * 60)

    cfg = PipelineConfig()
    cfg.dry_run    = dry_run
    cfg.save_mongo = True    # write test-period forecasts to daily_forecasts collection
    cfg.save_csv   = True

    if budget is not None:
        cfg.daily_budget = budget

    ok_count      = 0
    skipped_count = 0
    failed_count  = 0
    failed_dates: list[str] = []

    for i, ts in enumerate(date_range, start=1):
        date_str = ts.strftime("%Y-%m-%d")
        log.info("[%d/%d] ─── %s ───────────────────────", i, total, date_str)

        if not force and _output_exists(cfg.outputs_dir, date_str):
            log.info("  Output already exists — skipping. (use --force to re-run)")
            skipped_count += 1
            continue

        try:
            run_pipeline(cfg, force_date=date_str)
            ok_count += 1
            log.info("  [%s] DONE", date_str)
        except SystemExit:
            # run_pipeline calls sys.exit(1) on partial failures — treat as warning
            ok_count += 1
            log.warning("  [%s] Completed with partial appliance failure (check manifest).", date_str)
        except Exception as exc:
            tb = traceback.format_exc()
            log.error("  [%s] FAILED: %s\n%s", date_str, exc, tb)
            failed_count += 1
            failed_dates.append(date_str)

    log.info("=" * 60)
    log.info("Batch complete | OK=%d | SKIPPED=%d | FAILED=%d",
             ok_count, skipped_count, failed_count)
    if failed_dates:
        log.warning("Failed dates: %s", failed_dates)
    log.info("=" * 60)


def _cli() -> None:
    parser = argparse.ArgumentParser(
        description="Offline batch scheduling runner for thesis evaluation."
    )
    parser.add_argument("--start",   default=DEFAULT_START, help="Start date YYYY-MM-DD")
    parser.add_argument("--end",     default=DEFAULT_END,   help="End date YYYY-MM-DD (inclusive)")
    parser.add_argument("--force",   action="store_true",   help="Re-run even if output exists")
    parser.add_argument("--dry-run", action="store_true",   help="Skip file writes")
    parser.add_argument("--budget",  type=float, default=None, help="Override daily budget in PHP")
    args = parser.parse_args()

    run_batch(
        start=args.start,
        end=args.end,
        force=args.force,
        dry_run=args.dry_run,
        budget=args.budget,
    )


if __name__ == "__main__":
    _cli()
