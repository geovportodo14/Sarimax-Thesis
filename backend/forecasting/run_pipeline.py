#!/usr/bin/env python3
"""
forecasting/run_pipeline.py
============================
Daily SARIMAX Forecasting Pipeline — Main Orchestrator

Usage (cron / scheduler):
    python run_pipeline.py                         # uses defaults from config.py
    python run_pipeline.py --date 2026-03-15       # override forecast date
    python run_pipeline.py --appliance aircon      # run one appliance only
    python run_pipeline.py --dry-run               # skip saves

This script is the single entry point called by your scheduler (cron, APScheduler,
Azure Function, etc.) every night after 23:00 when actual data is available.

Pipeline steps executed:
    1. Validate / locate historical CSV for each appliance
    2. Determine last actual timestamp → derive forecast window (next 24h)
    3. Fetch weather forecast from Open-Meteo API
    4. Build future_exog (calendar + lag + rolling + weather)
    5. Run SARIMAX get_forecast(steps=24)
    6. Post-process (clip negatives, round)
    7. Compute daily totals & cost
    8. Generate budget-aware recommendations
    9. Save outputs (CSV + optional MongoDB)
   10. Write run manifest JSON
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import traceback
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

# ── Local imports ─────────────────────────────────────────────────────────────
# Resolve paths relative to this file so the script can be run from any cwd.
_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))           # ensure `forecasting` package is importable

from forecasting.config import (
    APPLIANCE_MODEL_DIR,
    APPLIANCES,
    LOGS_DIR,
    OUTPUTS_DIR,
    PipelineConfig,
)
from forecasting.pipeline.features  import build_future_exog
from forecasting.pipeline.forecaster import (
    ApplianceForecast,
    build_forecast_index,
    forecast_appliance,
    load_best_params,
)
from forecasting.pipeline.logger    import get_logger
from forecasting.pipeline.recommender import generate_recommendations
from forecasting.pipeline.storage   import (
    save_forecast_csv,
    save_recommendation_json,
    save_run_manifest,
    save_to_mongo,
)
from forecasting.pipeline.weather   import fallback_weather, fetch_weather_forecast

log = get_logger("sarimax_pipeline", LOGS_DIR)


# =============================================================================
# History loader
# =============================================================================

def load_history(cfg: PipelineConfig, appliance: str, target_date: Optional[str] = None) -> pd.DataFrame:
    """
    Load historical data for *appliance*.
    Tries MongoDB first (if configured), then falls back to CSV.
    """
    if cfg.save_mongo:
        try:
            return load_history_from_mongo(cfg, appliance, target_date)
        except Exception as e:
            log.warning("[%s] MongoDB history load failed: %s. Falling back to CSV.", appliance, e)

    return load_history_from_csv(cfg.history_dir, appliance)


def load_history_from_csv(history_dir: Path, appliance: str) -> pd.DataFrame:
    """Original CSV loader logic."""
    path = history_dir / f"{appliance}_hourly.csv"
    if not path.exists():
        raise FileNotFoundError(f"History file not found: {path}")

    df = pd.read_csv(path)
    if "timestamp" not in df.columns or "energy" not in df.columns:
        raise ValueError(f"{path.name}: must contain 'timestamp' and 'energy' columns.")

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.sort_values("timestamp").drop_duplicates("timestamp").set_index("timestamp")
    return df


def load_history_from_mongo(cfg: PipelineConfig, appliance: str, target_date: Optional[str] = None) -> pd.DataFrame:
    """
    Fetch history from MongoDB `energybuckets` collection.
    If target_date is provided (YYYY-MM-DD), fetches data BEFORE that date.
    """
    from pymongo import MongoClient
    from forecasting.config import APPLIANCE_MAP_MONGO, HISTORY_COLLECTION, MONGO_DB, MONGO_URI

    mongo_app_name = APPLIANCE_MAP_MONGO.get(appliance, appliance)
    client = MongoClient(MONGO_URI)
    col = client[MONGO_DB][HISTORY_COLLECTION]

    # Query criteria
    query: dict[str, Any] = {"appliance_type": mongo_app_name}
    if target_date:
        query["date"] = {"$lt": target_date}

    # Fetch last 10 days to ensure we have enough for lag_168 (7 days)
    cursor = col.find(
        query,
        {"readings": 1, "date": 1}
    ).sort("date", -1).limit(10)

    all_readings = []
    for doc in cursor:
        for r in doc.get("readings", []):
            # Map MongoDB schema to SARIMAX expected feature names
            row = {
                "timestamp":   r["timestamp"],
                "energy":      r["processed_data"]["power_w"] / 1000.0, # kWh proxy
                "power":       r["processed_data"]["power_w"],
                "temperature": r.get("weather", {}).get("temp", 0),
                "humidity":    r.get("weather", {}).get("humidity", 0),
                "rainfall":    r.get("weather", {}).get("rainfall", 0),
            }
            all_readings.append(row)

    client.close()

    if not all_readings:
        raise ValueError(f"No documents found in MongoDB for appliance: {mongo_app_name}")

    df = pd.DataFrame(all_readings)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").drop_duplicates("timestamp").set_index("timestamp")

    log.info("[%s] History loaded from Mongo | rows=%d | last_ts=%s", 
             appliance, len(df), df.index.max())
    return df


# =============================================================================
# Per-appliance runner
# =============================================================================

def run_appliance(
    appliance: str,
    cfg: PipelineConfig,
    weather_df: Optional[pd.DataFrame],
    generated_at: str,
    force_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Run the full pipeline for a single appliance.

    Returns a result dict suitable for the run manifest.
    """
    model_dir_name = APPLIANCE_MODEL_DIR.get(appliance, appliance)
    model_dir      = cfg.models_root / model_dir_name

    if not model_dir.exists():
        raise FileNotFoundError(f"Model directory not found: {model_dir}")

    # ── 1. Load history ───────────────────────────────────────────────────────
    history = load_history(cfg, appliance, target_date=force_date)

    # ── 2. Determine forecast window ──────────────────────────────────────────
    last_actual_ts = history.index.max()

    if force_date:
        # Allow operator override (e.g. backfill runs)
        start_ts = pd.Timestamp(force_date)
        future_idx = pd.date_range(start=start_ts, periods=cfg.horizon, freq="h")
        log.info("[%s] Forced forecast date: %s", appliance, force_date)
    else:
        future_idx = build_forecast_index(last_actual_ts, cfg.horizon)

    forecast_date = future_idx[0].strftime("%Y-%m-%d")

    # ── 3. Load exog_columns from best_params.json ────────────────────────────
    params     = load_best_params(model_dir)
    exog_cols  = params.get("exog_columns", [])

    # ── 4. Build future_exog ──────────────────────────────────────────────────
    weather_for_appliance: Optional[pd.DataFrame] = None
    weather_needed = any(c in exog_cols for c in ("temperature", "humidity", "rainfall"))

    if weather_needed:
        if weather_df is not None and len(weather_df) == 24:
            weather_for_appliance = weather_df
        else:
            # Fallback: forward-fill from history
            w_cols = [c for c in ("temperature", "humidity", "rainfall") if c in history.columns]
            if w_cols:
                weather_for_appliance = fallback_weather(future_idx, history, w_cols)
            else:
                log.warning("[%s] Weather needed but no history cols available; using 0.", appliance)

    future_exog = build_future_exog(
        history      = history,
        future_idx   = future_idx,
        exog_columns = exog_cols,
        weather_df   = weather_for_appliance,
    )

    # ── 5-6. Forecast ─────────────────────────────────────────────────────────
    fc: ApplianceForecast = forecast_appliance(
        appliance    = appliance,
        model_dir    = model_dir,
        future_exog  = future_exog,
        future_idx   = future_idx,
        horizon      = cfg.horizon,
        generated_at = generated_at,
    )

    # ── 7. Post-process & save ────────────────────────────────────────────────
    records = fc.to_records(tariff=cfg.tariff)

    if not cfg.dry_run:
        if cfg.save_csv:
            save_forecast_csv(records, appliance, cfg.outputs_dir, forecast_date)

        if cfg.save_mongo:
            from forecasting.config import FORECAST_COLLECTION, MONGO_DB, MONGO_URI
            save_to_mongo(records, appliance, forecast_date, MONGO_URI, MONGO_DB, FORECAST_COLLECTION)

    return {
        "appliance":      appliance,
        "status":         "ok",
        "last_actual_ts": str(last_actual_ts),
        "forecast_start": str(future_idx[0]),
        "forecast_end":   str(future_idx[-1]),
        "total_kwh":      fc.total_kwh,
        "total_cost_php": round(fc.total_kwh * cfg.tariff, 4),
        "n_rows":         fc.n_rows,
    }, fc


# =============================================================================
# Main orchestrator
# =============================================================================

def run_pipeline(cfg: PipelineConfig, force_date: Optional[str] = None) -> None:
    generated_at  = datetime.now().isoformat()
    forecast_date = force_date or (pd.Timestamp.now() + pd.Timedelta(days=1)).strftime("%Y-%m-%d")

    log.info("=" * 60)
    log.info("SARIMAX Daily Forecasting Pipeline")
    log.info("Generated at : %s", generated_at)
    log.info("Forecast date: %s", forecast_date)
    log.info("Appliances   : %s", cfg.appliances)
    log.info("Horizon      : %d h", cfg.horizon)
    log.info("Tariff       : ₱%.2f/kWh", cfg.tariff)
    log.info("Budget       : ₱%.2f/day", cfg.daily_budget)
    log.info("Dry run      : %s", cfg.dry_run)
    log.info("=" * 60)

    # ── Step 3: Weather (one call, shared across all appliances) ──────────────
    weather_df = fetch_weather_forecast(
        lat         = cfg.lat,
        lon         = cfg.lon,
        target_date = pd.Timestamp(forecast_date).date(),
    )

    # ── Step 4–7: Per-appliance loop ──────────────────────────────────────────
    manifest: Dict[str, Any] = {
        "generated_at":  generated_at,
        "forecast_date": forecast_date,
        "config": {
            "horizon": cfg.horizon,
            "tariff":  cfg.tariff,
            "budget":  cfg.daily_budget,
        },
        "ok":       0,
        "failed":   0,
        "results":  [],
        "failures": [],
    }

    all_forecasts: Dict[str, ApplianceForecast] = {}

    for appliance in cfg.appliances:
        log.info("─── [%s] ───────────────────────────────────────", appliance)
        try:
            result, fc = run_appliance(appliance, cfg, weather_df, generated_at, forecast_date)
            manifest["results"].append(result)
            manifest["ok"] += 1
            all_forecasts[appliance] = fc
        except Exception as exc:
            tb = traceback.format_exc()
            log.error("[%s] FAILED: %s\n%s", appliance, exc, tb)
            manifest["failed"] += 1
            manifest["failures"].append({
                "appliance": appliance,
                "error":     str(exc),
                "traceback": tb,
            })

    # ── Step 8: Budget recommendation ─────────────────────────────────────────
    if all_forecasts:
        rec = generate_recommendations(
            appliance_forecasts = all_forecasts,
            tariff              = cfg.tariff,
            daily_budget        = cfg.daily_budget,
            forecast_date       = forecast_date,
        )
        log.info("Budget status: %s | predicted ₱%.2f | budget ₱%.2f",
                 rec.status, rec.predicted_cost_php, rec.daily_budget_php)
        for msg in rec.messages:
            log.info("  %s", msg)

        manifest["recommendation"] = asdict(rec)

        if not cfg.dry_run and cfg.save_csv:
            save_recommendation_json(asdict(rec), cfg.outputs_dir, forecast_date)
    else:
        log.warning("No successful forecasts — skipping recommendation layer.")

    # ── Step 9: Save run manifest ─────────────────────────────────────────────
    if not cfg.dry_run:
        save_run_manifest(manifest, cfg.outputs_dir, forecast_date)

    # ── Summary ───────────────────────────────────────────────────────────────
    log.info("=" * 60)
    log.info("[DONE] OK=%d | FAILED=%d", manifest["ok"], manifest["failed"])
    log.info("=" * 60)

    if manifest["failed"] > 0:
        sys.exit(1)


# =============================================================================
# CLI entry point
# =============================================================================

def _cli() -> None:
    parser = argparse.ArgumentParser(
        description="SARIMAX Daily Forecasting Pipeline",
    )
    parser.add_argument(
        "--date", type=str, default=None,
        help="Override forecast date (YYYY-MM-DD). Default: tomorrow.",
    )
    parser.add_argument(
        "--appliance", type=str, default=None,
        help="Run only one appliance (e.g. aircon).",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Skip all file/DB writes.",
    )
    parser.add_argument(
        "--budget", type=float, default=None,
        help="Override daily budget in PHP.",
    )
    args = parser.parse_args()

    cfg = PipelineConfig()

    if args.dry_run:
        cfg.dry_run = True
    if args.budget is not None:
        cfg.daily_budget = args.budget
    if args.appliance:
        if args.appliance not in cfg.appliances:
            log.error("Unknown appliance: %s. Valid: %s", args.appliance, cfg.appliances)
            sys.exit(1)
        cfg.appliances = [args.appliance]

    run_pipeline(cfg, force_date=args.date)


if __name__ == "__main__":
    _cli()
