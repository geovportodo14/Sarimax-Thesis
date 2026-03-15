"""
forecasting/api_adapter.py
===========================
Thin adapter exposing the forecasting pipeline as callable functions
for integration into the Node.js / Express API backend.

Usage from Node via child_process:
    python forecasting/api_adapter.py --appliance aircon --budget 200 --date 2026-03-15

Or call run_forecast() directly from another Python service.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Optional

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))

from forecasting.config import PipelineConfig
from forecasting.run_pipeline import run_pipeline          # noqa: E402


def run_forecast(
    appliance: Optional[str]  = None,
    date:      Optional[str]  = None,
    budget:    Optional[float] = None,
    dry_run:   bool            = False,
) -> dict:
    """
    Callable entry point for in-process API calls.

    Returns a dict compatible with JSON serialisation.
    """
    cfg = PipelineConfig()
    cfg.dry_run   = dry_run
    if budget is not None:
        cfg.daily_budget = budget
    if appliance:
        cfg.appliances = [appliance]

    # run_pipeline exits with code 1 on failure; catch and re-raise cleanly
    try:
        run_pipeline(cfg, force_date=date)
        return {"status": "ok", "forecast_date": date}
    except SystemExit as exc:
        return {"status": "error", "code": exc.code}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--appliance", default=None)
    parser.add_argument("--date",      default=None)
    parser.add_argument("--budget",    type=float, default=None)
    parser.add_argument("--dry-run",   action="store_true")
    args = parser.parse_args()

    result = run_forecast(
        appliance = args.appliance,
        date      = args.date,
        budget    = args.budget,
        dry_run   = args.dry_run,
    )
    print(json.dumps(result, indent=2))
