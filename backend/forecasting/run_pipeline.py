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
    8. Run MILP appliance scheduling (post-forecast optimizer)
    9. Generate budget-aware recommendations
   10. Save outputs (CSV + optional MongoDB)
   11. Write run manifest JSON
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import traceback
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

import pandas as pd

# ── Local imports ─────────────────────────────────────────────────────────────
# Resolve paths relative to this file so the script can be run from any cwd.
_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))           # ensure `forecasting` package is importable

from forecasting.config import (
    APPLIANCE_MODEL_DIR,
    APPLIANCE_MODEL_DIR_V2,
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
from forecasting.pipeline.scheduler import optimize_schedule
from forecasting.pipeline.storage   import (
    save_forecast_csv,
    save_recommendation_json,
    save_run_manifest,
    save_schedule_csv,
    save_schedule_json,
    save_to_mongo,
)
from forecasting.pipeline.weather   import fallback_weather, fetch_weather_forecast
from forecasting.pipeline.viz        import generate_forecast_plot

log = get_logger("sarimax_pipeline", LOGS_DIR)
MANILA_TZ = ZoneInfo("Asia/Manila")


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
    df = df.dropna(subset=["timestamp"])

    # Normalize CSV history to Manila time (+08:00) so it aligns with
    # forecast windows and lag lookups.
    if getattr(df["timestamp"].dt, "tz", None) is None:
        df["timestamp"] = df["timestamp"].dt.tz_localize(MANILA_TZ)
    else:
        df["timestamp"] = df["timestamp"].dt.tz_convert(MANILA_TZ)

    df = df.sort_values("timestamp").drop_duplicates("timestamp").set_index("timestamp")
    return df


def load_history_from_mongo(cfg: PipelineConfig, appliance: str, target_date: Optional[str] = None) -> pd.DataFrame:
    """
    Fetch history from MongoDB `energybuckets` collection.
    If target_date is provided (YYYY-MM-DD in Manila time), fetches data
    BEFORE that date.  MongoDB stores dates in UTC, so we subtract one day
    from the upper bound to avoid cutting off evening (Manila) readings
    that fall on the previous UTC date.
    """
    from pymongo import MongoClient
    from forecasting.config import APPLIANCE_MAP_MONGO, HISTORY_COLLECTION, MONGO_DB, MONGO_URI

    mongo_app_name = APPLIANCE_MAP_MONGO.get(appliance, appliance)
    try:
        import certifi
        ca_file = certifi.where()
    except ImportError:
        ca_file = None
    client = MongoClient(
        MONGO_URI,
        tlsCAFile=ca_file,
        serverSelectionTimeoutMS=15000,
        socketTimeoutMS=20000,
        connectTimeoutMS=15000,
    )
    col = client[MONGO_DB][HISTORY_COLLECTION]

    # Query criteria
    query: dict[str, Any] = {"appliance_type": mongo_app_name}
    if target_date:
        # Mongo date field is UTC.  Manila = UTC+8, so a Manila date's
        # earliest UTC timestamp is the previous day at 16:00 UTC.
        # Use $lte previous day so we don't lose the evening bucket.
        from datetime import datetime, timedelta
        target_dt = datetime.strptime(target_date, "%Y-%m-%d")
        # Include the UTC day before the Manila target date
        upper_bound = (target_dt - timedelta(days=1)).strftime("%Y-%m-%d")
        query["date"] = {"$lte": upper_bound}

    # Fetch up to 90 days so we reach real sensor data even if recent
    # days have flat/placeholder readings (real data ends ~March 28).
    cursor = col.find(
        query,
        {"readings": 1, "date": 1}
    ).sort("date", -1).limit(90)

    all_readings = []
    for doc in cursor:
        for r in doc.get("readings", []):
            pw = r.get("processed_data", {}).get("power_w", None)
            if pw is None:
                continue
            row = {
                "timestamp":   r["timestamp"],
                "energy":      pw / 1000.0,  # kWh proxy
                "power":       pw,
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

    # Ensure timestamps are localized to UTC and then converted to Manila local time
    if df["timestamp"].dt.tz is None:
        df["timestamp"] = df["timestamp"].dt.tz_localize("UTC")
    df["timestamp"] = df["timestamp"].dt.tz_convert("Asia/Manila")

    df = df.sort_values("timestamp").drop_duplicates("timestamp").set_index("timestamp")

    # Filter to only readings before target_date in Manila time
    if target_date:
        cutoff = pd.Timestamp(target_date, tz="Asia/Manila")
        df = df[df.index < cutoff]

    # Drop flat/placeholder days: if a full day has zero variance in energy,
    # those readings are not real sensor data — remove them.
    if not df.empty:
        df["_date"] = df.index.date
        daily_std = df.groupby("_date")["energy"].std()
        flat_dates = set(daily_std[daily_std < 1e-6].index)
        if flat_dates:
            before = len(df)
            df = df[~df["_date"].isin(flat_dates)]
            dropped = before - len(df)
            if dropped:
                log.info("[%s] Dropped %d flat/placeholder readings (%d days)",
                         appliance, dropped, len(flat_dates))
        df = df.drop(columns=["_date"])

    if df.empty:
        raise ValueError(f"No valid (non-flat) readings in MongoDB for appliance: {mongo_app_name}")

    # Resample to hourly — SARIMAX models were trained on hourly data.
    # Mongo readings are at 10-minute intervals; aggregate to 1H.
    freq = pd.infer_freq(df.index)
    if freq is None or pd.tseries.frequencies.to_offset(freq) < pd.tseries.frequencies.to_offset("1h"):
        log.info("[%s] Resampling %d sub-hourly readings to hourly", appliance, len(df))
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        df = df[numeric_cols].resample("1h").mean().dropna(how="all")

    log.info("[%s] History loaded from Mongo (Manila Time) | rows=%d | last_ts=%s",
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
    # ── 1. Pre-computed lookup (V2 only, before history load) ────────────────
    # If the forecast date falls within the training range, use the accurate
    # pre-computed predictions and skip history loading entirely.
    if cfg.use_v2_models and appliance in APPLIANCE_MODEL_DIR_V2 and force_date:
        from forecasting.pipeline.forecaster_v2 import _try_precomputed_lookup

        stage_dirs = {
            k: Path(v) if Path(v).is_absolute() else cfg.models_root / v
            for k, v in APPLIANCE_MODEL_DIR_V2[appliance].items()
        }
        start_ts = pd.Timestamp(force_date)
        if start_ts.tzinfo is None:
            start_ts = start_ts.tz_localize(MANILA_TZ)
        future_idx = pd.date_range(start=start_ts, periods=cfg.horizon, freq="h")
        if future_idx.tz is None:
            future_idx = future_idx.tz_localize(MANILA_TZ)

        precomp = _try_precomputed_lookup(appliance, stage_dirs, future_idx, cfg.horizon, generated_at)
        if precomp is not None:
            fc = precomp
            forecast_date = future_idx[0].strftime("%Y-%m-%d")
            # Save results then return — skip history loading entirely
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
                "last_actual_ts": "precomputed",
                "forecast_start": str(future_idx[0]),
                "forecast_end":   str(future_idx[-1]),
                "total_kwh":      fc.total_kwh,
                "total_cost_php": round(fc.total_kwh * cfg.tariff, 4),
                "n_rows":         fc.n_rows,
            }, fc

    # ── 2. Load history ───────────────────────────────────────────────────────
    history = load_history(cfg, appliance, target_date=force_date)

    # ── 3. Determine forecast window ──────────────────────────────────────────
    last_actual_ts = history.index.max()

    if force_date:
        # Allow operator override (e.g. backfill runs)
        start_ts = pd.Timestamp(force_date)
        if start_ts.tzinfo is None:
            start_ts = start_ts.tz_localize(MANILA_TZ)
        else:
            start_ts = start_ts.tz_convert(MANILA_TZ)
        future_idx = pd.date_range(start=start_ts, periods=cfg.horizon, freq="h")
        log.info("[%s] Forced forecast date: %s", appliance, force_date)
    else:
        future_idx = build_forecast_index(last_actual_ts, cfg.horizon)

    if future_idx.tz is None:
        future_idx = future_idx.tz_localize(MANILA_TZ)
    else:
        future_idx = future_idx.tz_convert(MANILA_TZ)

    forecast_date = future_idx[0].strftime("%Y-%m-%d")

    # ── 4. Weather (shared by both V1 and V2 paths) ──────────────────────────
    weather_for_appliance: Optional[pd.DataFrame] = None
    if weather_df is not None and len(weather_df) == 24:
        weather_for_appliance = weather_df
    else:
        w_cols = [c for c in ("temperature", "humidity", "rainfall") if c in history.columns]
        if w_cols:
            weather_for_appliance = fallback_weather(future_idx, history, w_cols)

    # ── 5-7. Forecast (V2 or V1) ─────────────────────────────────────────────
    if cfg.use_v2_models and appliance in APPLIANCE_MODEL_DIR_V2:
        from forecasting.pipeline.forecaster_v2 import forecast_appliance_v2

        stage_dirs = {
            k: Path(v) if Path(v).is_absolute() else cfg.models_root / v
            for k, v in APPLIANCE_MODEL_DIR_V2[appliance].items()
        }
        fc: ApplianceForecast = forecast_appliance_v2(
            appliance=appliance,
            stage_dirs=stage_dirs,
            history=history,
            future_idx=future_idx,
            weather_df=weather_for_appliance,
            horizon=cfg.horizon,
            generated_at=generated_at,
        )
    else:
        model_dir_val = APPLIANCE_MODEL_DIR.get(appliance, appliance)
        model_dir = Path(model_dir_val) if Path(model_dir_val).is_absolute() else cfg.models_root / model_dir_val

        if not model_dir.exists():
            raise FileNotFoundError(f"Model directory not found: {model_dir}")

        params = load_best_params(model_dir)
        exog_cols = params.get("exog_columns", [])

        future_exog = build_future_exog(
            history=history,
            future_idx=future_idx,
            exog_columns=exog_cols,
            weather_df=weather_for_appliance,
        )

        fc = forecast_appliance(
            appliance=appliance,
            model_dir=model_dir,
            future_exog=future_exog,
            future_idx=future_idx,
            history=history,
            horizon=cfg.horizon,
            generated_at=generated_at,
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
    now_mnl = pd.Timestamp.now(tz=MANILA_TZ)
    generated_at  = now_mnl.isoformat()
    forecast_date = force_date or (now_mnl + pd.Timedelta(days=1)).strftime("%Y-%m-%d")

    # ── Step 0: Scrape latest Meralco tariff (optional) ──────────────────────
    if cfg.meralco_scraper_enabled:
        try:
            from forecasting.meralco_scraper import scrape_latest_tariff
            result = scrape_latest_tariff()
            scraped_tariff = result["tariff_php"]
            log.info(
                "[meralco_scraper] %s rates for %s — effective tariff ₱%.4f/kWh",
                "Cached" if result["cached"] else "Scraped",
                result["month_key"],
                scraped_tariff,
            )
            cfg.tariff = scraped_tariff
        except Exception as exc:
            log.warning(
                "[meralco_scraper] Failed to fetch latest rates: %s. "
                "Falling back to configured tariff ₱%.2f/kWh.",
                exc, cfg.tariff,
            )

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
            "scheduler_enabled": cfg.scheduler_enabled,
            "scheduler_max_shift_hours": cfg.scheduler_max_shift_hours,
            "scheduler_peak_penalty": cfg.scheduler_peak_penalty,
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

    # ── Step 8: Post-forecast optimization (MILP scheduler) ──────────────────
    schedule_dict: Optional[Dict[str, Any]] = None
    if all_forecasts and cfg.scheduler_enabled:
        try:
            schedule = optimize_schedule(
                appliance_forecasts=all_forecasts,
                forecast_date=forecast_date,
                generated_at=generated_at,
                base_tariff=cfg.tariff,
                appliance_rules=cfg.scheduler_appliance_rules,
                comfort_penalty=cfg.scheduler_comfort_penalty,
                tariff_multipliers=cfg.scheduler_tariff_multipliers,
                max_shift_default=cfg.scheduler_max_shift_hours,
                peak_penalty=cfg.scheduler_peak_penalty,
                horizon=cfg.horizon,
                budget_constraint_php=cfg.daily_budget,
                binary_mode=cfg.scheduler_binary_mode,
            )
            schedule_dict = schedule.to_dict()
            manifest["optimization"] = {
                "status": schedule.status,
                "solver": schedule.solver,
                "binary_mode": cfg.scheduler_binary_mode,
                "budget_php": cfg.daily_budget,
                "baseline_total_cost_php": schedule.baseline_total_cost_php,
                "optimized_total_cost_php": schedule.optimized_total_cost_php,
                "estimated_savings_php": schedule.estimated_savings_php,
                "estimated_savings_pct": schedule.estimated_savings_pct,
                "baseline_peak_kwh": schedule.baseline_peak_kwh,
                "optimized_peak_kwh": schedule.optimized_peak_kwh,
                "peak_reduction_kwh": schedule.peak_reduction_kwh,
                "time_block_summary": schedule.time_block_summary,
            }

            # Log the human-readable ON/OFF schedule (MILP.md output format)
            if schedule.time_block_summary:
                log.info("[scheduler] Recommended appliance schedule:")
                for app, blocks in schedule.time_block_summary.items():
                    log.info("  %-16s %s", app.replace("_", " ").title() + ":", blocks)

            if not cfg.dry_run and cfg.save_csv:
                save_schedule_json(schedule_dict, cfg.outputs_dir, forecast_date)
                save_schedule_csv(schedule.to_csv_rows(), cfg.outputs_dir, forecast_date)
        except Exception as exc:
            tb = traceback.format_exc()
            log.error("[scheduler] FAILED: %s\n%s", exc, tb)
            manifest["optimization"] = {
                "status": "error",
                "error": str(exc),
            }

    # ── Step 9: Budget recommendation ─────────────────────────────────────────
    if all_forecasts:
        rec = generate_recommendations(
            appliance_forecasts = all_forecasts,
            tariff              = cfg.tariff,
            daily_budget        = cfg.daily_budget,
            forecast_date       = forecast_date,
            schedule_result     = schedule_dict,
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

    # ── Step 10: Save run manifest ────────────────────────────────────────────
    if not cfg.dry_run:
        save_run_manifest(manifest, cfg.outputs_dir, forecast_date)

    # ── Step 11: Automatic Visualization ──────────────────────────────────────
    if manifest["ok"] > 0 and not cfg.dry_run:
        try:
            plot_file = generate_forecast_plot(cfg.outputs_dir, forecast_date, cfg.appliances)
            if plot_file:
                log.info("Pipeline visualization complete.")
        except Exception as e:
            log.error(f"Visualization failed: {e}")

    # Summary ───────────────────────────────────────────────────────────────
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
