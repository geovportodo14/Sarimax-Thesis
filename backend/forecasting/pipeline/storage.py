"""
forecasting/pipeline/storage.py
=================================
Saves forecast outputs in two modes:
  1. CSV  → outputs/<forecast_date>/<appliance>_forecast.csv
  2. MongoDB → daily_forecasts collection (optional)

Both modes store the same schema.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

log = logging.getLogger("sarimax_pipeline.storage")


# ---------------------------------------------------------------------------
# CSV / JSON
# ---------------------------------------------------------------------------

def save_forecast_csv(
    records: List[Dict[str, Any]],
    appliance: str,
    outputs_dir: Path,
    forecast_date: str,
) -> Path:
    out_dir = outputs_dir / forecast_date
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{appliance}_forecast.csv"
    df = pd.DataFrame(records)
    df.to_csv(path, index=False)
    log.info("CSV saved: %s", path)
    return path


def save_run_manifest(
    manifest: Dict[str, Any],
    outputs_dir: Path,
    forecast_date: str,
) -> Path:
    """Save a JSON summary of the pipeline run."""
    out_dir = outputs_dir / forecast_date
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "_run_manifest.json"
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    log.info("Run manifest saved: %s", path)
    return path


def save_recommendation_json(
    rec_dict: Dict[str, Any],
    outputs_dir: Path,
    forecast_date: str,
) -> Path:
    out_dir = outputs_dir / forecast_date
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "_recommendation.json"
    path.write_text(json.dumps(rec_dict, indent=2), encoding="utf-8")
    log.info("Recommendation saved: %s", path)
    return path


def save_schedule_json(
    schedule_dict: Dict[str, Any],
    outputs_dir: Path,
    forecast_date: str,
) -> Path:
    out_dir = outputs_dir / forecast_date
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "_schedule.json"
    path.write_text(json.dumps(schedule_dict, indent=2), encoding="utf-8")
    log.info("Schedule JSON saved: %s", path)
    return path


def save_schedule_csv(
    rows: List[Dict[str, Any]],
    outputs_dir: Path,
    forecast_date: str,
) -> Path:
    out_dir = outputs_dir / forecast_date
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "optimized_schedule.csv"
    pd.DataFrame(rows).to_csv(path, index=False)
    log.info("Schedule CSV saved: %s", path)
    return path


# ---------------------------------------------------------------------------
# MongoDB (optional)
# ---------------------------------------------------------------------------

def save_to_mongo(
    records: List[Dict[str, Any]],
    appliance: str,
    forecast_date: str,
    mongo_uri: str,
    db_name: str,
    collection_name: str,
) -> None:
    """
    Upsert forecast records into MongoDB.
    One document per (appliance, timestamp).
    """
    try:
        from pymongo import MongoClient
    except ImportError:
        log.error("pymongo is not installed. Skipping MongoDB save.")
        return

    client = MongoClient(mongo_uri)
    col = client[db_name][collection_name]

    import pandas as pd

    prepared: List[Dict[str, Any]] = []
    for r in records:
        doc = dict(r)
        dt = pd.to_datetime(doc["timestamp"], errors="coerce")
        if pd.isna(dt):
            log.warning("[Mongo] Skipping invalid timestamp for %s: %s", appliance, doc.get("timestamp"))
            continue

        # Normalize to Manila for charting hour buckets, keep UTC datetime for precision.
        if dt.tzinfo is None:
            local_dt = dt.tz_localize("Asia/Manila")
        else:
            local_dt = dt.tz_convert("Asia/Manila")

        doc["timestamp"] = local_dt.strftime("%H:00")
        doc["hour"] = int(local_dt.hour)
        doc["timestamp_dt"] = local_dt.tz_convert("UTC").to_pydatetime()
        prepared.append(doc)

    if prepared:
        # Replace this appliance+date atomically enough for daily runs.
        # Prevents stale duplicates from legacy timestamp formats.
        alias_keys = {appliance}
        if appliance == "electric_fan":
            alias_keys.add("electricfan")
        elif appliance == "electricfan":
            alias_keys.add("electric_fan")

        delete_result = col.delete_many({
            "appliance": {"$in": list(alias_keys)},
            "forecast_date": forecast_date,
        })
        insert_result = col.insert_many(prepared, ordered=True)
        log.info(
            "[Mongo] %s | date=%s | deleted=%d inserted=%d",
            appliance,
            forecast_date,
            delete_result.deleted_count,
            len(insert_result.inserted_ids),
        )

    client.close()
