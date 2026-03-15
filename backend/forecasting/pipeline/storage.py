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
        from pymongo import MongoClient, UpdateOne
    except ImportError:
        log.error("pymongo is not installed. Skipping MongoDB save.")
        return

    client = MongoClient(mongo_uri)
    col    = client[db_name][collection_name]

    ops = [
        UpdateOne(
            filter={"appliance": r["appliance"], "timestamp": r["timestamp"]},
            update={"$set": r},
            upsert=True,
        )
        for r in records
    ]

    if ops:
        result = col.bulk_write(ops)
        log.info(
            "[Mongo] %s | date=%s | upserted=%d modified=%d",
            appliance, forecast_date,
            result.upserted_count, result.modified_count,
        )
    client.close()
