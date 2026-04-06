#!/usr/bin/env python3
"""
Data Integrity Report

Summary:
This script performs batch data integrity checks for each per-appliance
model-ready CSV used in the SARIMAX pipeline. It validates timestamps,
checks for duplicate and missing hourly records, summarizes missing values,
previews object-to-numeric coercion issues in exogenous columns, and shows
a synthetic-versus-real split preview using the same boundaries as Stage 3.5.2.

Input flow:
data/
  -> <appliance_model_ready>.csv

Processing flow:
per-appliance CSV
  -> validate required columns
  -> parse and index timestamps
  -> check inferred frequency
  -> reindex to hourly range to detect timestamp gaps
  -> summarize NA counts and NA rows
  -> diagnose expected vs unexpected missingness
  -> preview exogenous object-to-numeric coercion behavior
  -> preview synthetic/real split counts and ranges

Output flow:
model/
  -> sarimax/
     -> <appliance_csv_stem>/
        -> integrity/
           -> <appliance_csv_stem>_integrity_report.json
           -> <appliance_csv_stem>_na_rows_sample.csv
     -> _integrity_summary.json
"""

from __future__ import annotations

import json
import traceback
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd


# =============================================================================
# Defaults
# =============================================================================

DEFAULT_INPUT_DIR = Path("data")
DEFAULT_SARIMAX_DIR = Path("model/sarimax")
DEFAULT_GLOB = "*.csv"

# Must match the hybrid split boundaries used in Stage 3.5.2
DEFAULT_SYNTHETIC_END = "2026-01-03 18:00:00"
DEFAULT_REAL_START = "2026-01-03 19:00:00"

REQUIRED_COLS = ["timestamp", "energy"]


# =============================================================================
# Logger
# =============================================================================

def _ts() -> str:
    return datetime.now().strftime("%H:%M:%S")


def log(msg: str) -> None:
    print(f"[{_ts()}] [INFO] {msg}", flush=True)


def warn(msg: str) -> None:
    print(f"[{_ts()}] [WARN] {msg}", flush=True)


def err(msg: str) -> None:
    print(f"[{_ts()}] [ERROR] {msg}", flush=True)


# =============================================================================
# Config
# =============================================================================

@dataclass
class IntegrityConfig:
    expected_freq: str = "h"
    sample_na_rows_max: int = 500
    infer_freq_head: int = 200
    synthetic_end: str = DEFAULT_SYNTHETIC_END
    real_start: str = DEFAULT_REAL_START

    # These are expected to have leading NaNs due to feature engineering.
    expected_na_prefix_cols: Tuple[str, ...] = (
        "lag_24",
        "lag_168",
        "rolling_mean_24",
        "rolling_mean_168",
    )


CFG = IntegrityConfig()


# =============================================================================
# Path helpers
# =============================================================================

def get_integrity_output_dir(appliance: str) -> Path:
    """
    Build the integrity output folder for one appliance.
    """
    out_dir = DEFAULT_SARIMAX_DIR / appliance / "integrity"
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def get_summary_output_path() -> Path:
    """
    Keep the batch summary at the root SARIMAX folder.
    """
    DEFAULT_SARIMAX_DIR.mkdir(parents=True, exist_ok=True)
    return DEFAULT_SARIMAX_DIR / "_integrity_summary.json"


# =============================================================================
# Data loading and checks
# =============================================================================

def load_csv(path: Path) -> pd.DataFrame:
    """
    Load one appliance CSV and enforce the required base schema.
    """
    df = pd.read_csv(path)

    for col in REQUIRED_COLS:
        if col not in df.columns:
            raise ValueError(f"{path.name}: missing required column '{col}'")

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    bad_timestamps = int(df["timestamp"].isna().sum())
    if bad_timestamps:
        raise ValueError(f"{path.name}: {bad_timestamps} invalid timestamps")

    df = df.sort_values("timestamp").set_index("timestamp")
    return df


def infer_frequency(idx: pd.DatetimeIndex, head: int) -> Optional[str]:
    """
    Infer frequency using only the first chunk of the index.
    """
    if len(idx) < 5:
        return None
    return pd.infer_freq(idx[: min(head, len(idx))])


def hourly_reindex_gap_report(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Reindex to a full hourly range and report timestamp gaps.
    """
    if df.empty:
        return {"ok": False, "reason": "empty dataframe"}

    start = df.index.min()
    end = df.index.max()

    full_idx = pd.date_range(start, end, freq="h")
    df_hourly = df.reindex(full_idx)

    missing_ts_count = int(len(full_idx) - len(df.index.unique()))
    missing_energy_after_reindex = (
        int(df_hourly["energy"].isna().sum()) if "energy" in df_hourly.columns else None
    )

    return {
        "ok": True,
        "start": str(start),
        "end": str(end),
        "n_full_hourly_index": int(len(full_idx)),
        "n_original_unique_timestamps": int(len(df.index.unique())),
        "missing_hour_timestamps_count": missing_ts_count,
        "missing_energy_after_reindex_count": missing_energy_after_reindex,
    }


def na_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Summarize missing values per column and per row.
    """
    n_rows = len(df)
    na_counts = df.isna().sum().to_dict()
    na_percent = {
        col: (float(count) / n_rows * 100.0 if n_rows else None)
        for col, count in na_counts.items()
    }

    na_rows_mask = df.isna().any(axis=1)
    na_rows_count = int(na_rows_mask.sum())

    # Show which columns most often contribute to NA rows.
    contrib = df.loc[na_rows_mask].isna().sum().sort_values(ascending=False)
    top_contrib = [
        {"column": str(col), "na_count_in_na_rows": int(count)}
        for col, count in contrib.head(20).items()
    ]

    return {
        "n_rows": int(n_rows),
        "na_rows_count": na_rows_count,
        "na_counts": {col: int(count) for col, count in na_counts.items()},
        "na_percent": na_percent,
        "top_na_contributors_in_na_rows": top_contrib,
    }


def expected_na_diagnosis(df: pd.DataFrame, cfg: IntegrityConfig) -> Dict[str, Any]:
    """
    Check whether NA rows are mostly explained by expected lag/rolling columns.
    """
    expected_cols = [col for col in cfg.expected_na_prefix_cols if col in df.columns]
    if not expected_cols:
        return {
            "expected_cols_present": [],
            "notes": "No expected lag/rolling cols present",
        }

    na_mask = df.isna().any(axis=1)
    na_df = df.loc[na_mask]

    other_cols = [col for col in df.columns if col not in expected_cols]

    only_expected_na_rows = 0
    if len(na_df) > 0 and other_cols:
        only_expected_na_rows = int((na_df[other_cols].isna().sum(axis=1) == 0).sum())

    unexpected_na_rows = int(len(na_df) - only_expected_na_rows)

    return {
        "expected_cols_present": expected_cols,
        "na_rows_total": int(len(na_df)),
        "na_rows_only_expected_cols": int(only_expected_na_rows),
        "na_rows_with_unexpected_missing": int(unexpected_na_rows),
        "note": "If unexpected_missing > 0, check weather merge or upstream gaps.",
    }


def exog_type_coercion_preview(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Preview object exogenous columns and how many values would become NaN
    if coerced to numeric.
    """
    exog_cols = [col for col in df.columns if col != "energy"]
    results: List[Dict[str, Any]] = []

    for col in exog_cols:
        series = df[col]
        dtype = str(series.dtype)

        if dtype == "object":
            coerced = pd.to_numeric(series, errors="coerce")
            n_new_nan = int(coerced.isna().sum() - series.isna().sum())

            results.append({
                "column": col,
                "dtype": dtype,
                "n_rows": int(len(series)),
                "existing_nan": int(series.isna().sum()),
                "new_nan_if_coerced": n_new_nan,
                "example_values": [str(x) for x in series.dropna().astype(str).head(5).tolist()],
            })

    return {
        "object_columns_checked": len(results),
        "object_column_reports": results[:50],
        "note": "If new_nan_if_coerced > 0, you have non-numeric strings in exog.",
    }


def hybrid_split_preview(df: pd.DataFrame, cfg: IntegrityConfig) -> Dict[str, Any]:
    """
    Preview synthetic and real partitions using the configured split boundaries.
    """
    synthetic_end = pd.to_datetime(cfg.synthetic_end)
    real_start = pd.to_datetime(cfg.real_start)

    synthetic = df.loc[df.index <= synthetic_end]
    real = df.loc[df.index >= real_start]

    return {
        "synthetic_end": cfg.synthetic_end,
        "real_start": cfg.real_start,
        "counts": {
            "synthetic": int(len(synthetic)),
            "real": int(len(real)),
            "total": int(len(df)),
        },
        "ranges": {
            "synthetic": [str(synthetic.index.min()), str(synthetic.index.max())] if len(synthetic) else [None, None],
            "real": [str(real.index.min()), str(real.index.max())] if len(real) else [None, None],
            "total": [str(df.index.min()), str(df.index.max())],
        },
    }


def save_na_rows_sample(df: pd.DataFrame, out_csv: Path, cfg: IntegrityConfig) -> Dict[str, Any]:
    """
    Save only the first N NA rows for easier inspection.
    """
    na_rows = df[df.isna().any(axis=1)]
    n_na_rows = len(na_rows)

    if n_na_rows == 0:
        return {"saved": False, "na_rows": 0, "path": None}

    sample = na_rows.head(cfg.sample_na_rows_max).copy()
    sample = sample.reset_index().rename(columns={"index": "timestamp"})
    sample.to_csv(out_csv, index=False)

    return {
        "saved": True,
        "na_rows": int(n_na_rows),
        "sample_rows_saved": int(len(sample)),
        "path": str(out_csv),
    }


# =============================================================================
# Per-file runner
# =============================================================================

def run_one(csv_path: Path, cfg: IntegrityConfig) -> Dict[str, Any]:
    """
    Run the full integrity report for one appliance CSV.
    """
    appliance = csv_path.stem
    log(f"--- START integrity: {appliance} ---")

    df = load_csv(csv_path)

    duplicate_timestamps = int(df.index.duplicated().sum())
    inferred_frequency = infer_frequency(df.index, cfg.infer_freq_head)

    gap_info = hourly_reindex_gap_report(df)
    na_info = na_stats(df)
    expected_na_info = expected_na_diagnosis(df, cfg)
    exog_preview = exog_type_coercion_preview(df)
    split_preview = hybrid_split_preview(df, cfg)

    out_dir = get_integrity_output_dir(appliance)

    na_sample_path = out_dir / f"{appliance}_na_rows_sample.csv"
    na_sample_meta = save_na_rows_sample(df, na_sample_path, cfg)

    report = {
        "appliance": appliance,
        "input_file": str(csv_path),
        "timestamp": datetime.now().isoformat(),
        "basic": {
            "n_rows": int(len(df)),
            "n_cols": int(df.shape[1]),
            "start": str(df.index.min()),
            "end": str(df.index.max()),
            "duplicate_timestamps": duplicate_timestamps,
            "inferred_frequency_first_head": inferred_frequency,
            "columns": list(df.columns),
        },
        "hourly_index_gap_check": gap_info,
        "missing_values": na_info,
        "expected_na_diagnosis": expected_na_info,
        "exog_object_coercion_preview": exog_preview,
        "hybrid_split_preview": split_preview,
        "na_rows_sample": na_sample_meta,
    }

    report_path = out_dir / f"{appliance}_integrity_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    log(f"Saved integrity report: {report_path}")
    if na_sample_meta.get("saved"):
        log(f"Saved NA rows sample: {na_sample_path}")

    log(f"--- DONE integrity: {appliance} ---")

    return {
        "appliance": appliance,
        "report_path": str(report_path),
        "na_rows": int(na_info["na_rows_count"]),
        "duplicate_timestamps": duplicate_timestamps,
        "missing_hour_timestamps_count": (
            int(gap_info.get("missing_hour_timestamps_count", -1))
            if gap_info.get("ok")
            else None
        ),
    }


# =============================================================================
# Main
# =============================================================================

def main() -> None:
    log("==============================================")
    log("Data Integrity Report (Preflight)")
    log(f"Input dir   : {DEFAULT_INPUT_DIR}")
    log(f"SARIMAX dir : {DEFAULT_SARIMAX_DIR}")
    log(f"Glob        : {DEFAULT_GLOB}")
    log(f"Config      : {asdict(CFG)}")
    log("==============================================")

    if not DEFAULT_INPUT_DIR.exists():
        raise FileNotFoundError(f"DEFAULT_INPUT_DIR not found: {DEFAULT_INPUT_DIR}")

    files = sorted(DEFAULT_INPUT_DIR.glob(DEFAULT_GLOB))
    if not files:
        raise FileNotFoundError(
            f"No CSV files found in {DEFAULT_INPUT_DIR} with pattern {DEFAULT_GLOB}"
        )

    summary: Dict[str, Any] = {
        "timestamp": datetime.now().isoformat(),
        "config": asdict(CFG),
        "input_dir": str(DEFAULT_INPUT_DIR),
        "output_dir": str(DEFAULT_SARIMAX_DIR),
        "n_files": len(files),
        "ok": 0,
        "failed": 0,
        "results": [],
        "failures": [],
    }

    for idx, csv_path in enumerate(files, start=1):
        log(f"[{idx}/{len(files)}] Integrity check: {csv_path.name}")
        try:
            result = run_one(csv_path, CFG)
            summary["results"].append(result)
            summary["ok"] += 1
        except Exception as e:
            tb = traceback.format_exc()
            err(f"[{idx}/{len(files)}] FAILED {csv_path.name}: {e}")
            err(tb)

            summary["failed"] += 1
            summary["failures"].append({
                "file": str(csv_path),
                "error": str(e),
                "traceback": tb,
            })

    summary_path = get_summary_output_path()
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    log("==============================================")
    log(f"[DONE] Integrity reports complete | OK={summary['ok']} FAILED={summary['failed']}")
    log(f"Summary: {summary_path}")
    log("==============================================")


if __name__ == "__main__":
    main()