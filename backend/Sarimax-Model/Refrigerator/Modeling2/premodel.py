#!/usr/bin/env python3
"""
Stage 3.5.2A — Data Integrity Report (Per-Appliance, Batch, Zero-Args, Verbose)

RUN:
  python backend/scripts/stage35_2a_data_integrity_report.py

INPUT:
  Per-appliance model-ready CSVs in DEFAULT_INPUT_DIR
  Must include: timestamp, energy
  Other columns treated as exogenous.

OUTPUT:
  data/modeling/reports/sarimax_data_integrity/
    - <appliance_stem>_integrity_report.json
    - <appliance_stem>_na_rows_sample.csv
    - _integrity_summary.json

What it checks (per appliance):
  - Basic shape and timestamp range
  - Duplicate timestamps
  - Inferred frequency and missing hourly timestamps (reindex check)
  - NA counts per column + % NA
  - NA rows (count) and saves a SAMPLE of NA rows (not all, to keep size manageable)
  - Which columns contribute most to NA rows (expected lag/rolling vs unexpected)
  - Exog type coercion preview: object -> numeric (how many turn into NaN)
  - Hybrid split preview (synthetic vs real counts) using the same boundaries as Stage 3.5.2
"""

from __future__ import annotations

import json
import traceback
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

import numpy as np
import pandas as pd


# =============================================================================
# Defaults (EDIT ONCE IF NEEDED)
# =============================================================================

DEFAULT_INPUT_DIR = Path("data") 
DEFAULT_OUT_DIR = Path("model/pre_model/sarimax_data_integrity")
DEFAULT_GLOB = "*.csv"

# Must match your Stage 3.5.2 hybrid boundaries
DEFAULT_SYNTHETIC_END = "2026-01-02 23:00:00"
DEFAULT_REAL_START = "2026-01-03 00:00:00"


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
    expected_freq: str = "h"  # hourly
    sample_na_rows_max: int = 500  # save only first N NA rows to CSV
    infer_freq_head: int = 200
    synthetic_end: str = DEFAULT_SYNTHETIC_END
    real_start: str = DEFAULT_REAL_START

    # Columns that are EXPECTED to have NA at the beginning due to feature engineering
    expected_na_prefix_cols: Tuple[str, ...] = (
        "lag_24", "lag_168",
        "rolling_mean_24", "rolling_mean_168",
    )


CFG = IntegrityConfig()


# =============================================================================
# Helpers
# =============================================================================

REQUIRED_COLS = ["timestamp", "energy"]


def load_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    for c in REQUIRED_COLS:
        if c not in df.columns:
            raise ValueError(f"{path.name}: missing required column '{c}'")

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    bad = int(df["timestamp"].isna().sum())
    if bad:
        raise ValueError(f"{path.name}: {bad} invalid timestamps")

    df = df.sort_values("timestamp")
    df = df.set_index("timestamp")
    return df


def infer_frequency(idx: pd.DatetimeIndex, head: int) -> Optional[str]:
    if len(idx) < 5:
        return None
    return pd.infer_freq(idx[: min(head, len(idx))])


def hourly_reindex_gap_report(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Reindex to full hourly range and report missing timestamps count.
    """
    if len(df) == 0:
        return {"ok": False, "reason": "empty dataframe"}

    start = df.index.min()
    end = df.index.max()

    full_idx = pd.date_range(start, end, freq="h")
    dfh = df.reindex(full_idx)

    missing_ts_count = int(len(full_idx) - len(df.index.unique()))
    # missing energy after reindex can show true gaps
    missing_energy_after_reindex = int(dfh["energy"].isna().sum()) if "energy" in dfh.columns else None

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
    n = len(df)
    na_counts = df.isna().sum().to_dict()
    na_pct = {k: (float(v) / n * 100.0 if n else None) for k, v in na_counts.items()}

    na_rows_mask = df.isna().any(axis=1)
    na_rows_count = int(na_rows_mask.sum())

    # Which columns most frequently contribute to NA rows
    contrib = df.loc[na_rows_mask].isna().sum().sort_values(ascending=False)
    top_contrib = [{"column": str(k), "na_count_in_na_rows": int(v)} for k, v in contrib.head(20).items()]

    return {
        "n_rows": int(n),
        "na_rows_count": na_rows_count,
        "na_counts": {k: int(v) for k, v in na_counts.items()},
        "na_percent": na_pct,
        "top_na_contributors_in_na_rows": top_contrib,
    }


def expected_na_diagnosis(df: pd.DataFrame, cfg: IntegrityConfig) -> Dict[str, Any]:
    """
    Checks if NA patterns are mostly explained by expected feature engineering columns.
    """
    expected_cols = [c for c in cfg.expected_na_prefix_cols if c in df.columns]
    if not expected_cols:
        return {"expected_cols_present": [], "notes": "No expected lag/rolling cols present"}

    # Count NA rows attributable only to expected cols (i.e., other cols not NA)
    na_mask = df.isna().any(axis=1)
    na_df = df.loc[na_mask]

    other_cols = [c for c in df.columns if c not in expected_cols]
    only_expected_na_rows = 0
    if len(na_df) > 0 and other_cols:
        only_expected_na_rows = int((na_df[other_cols].isna().sum(axis=1) == 0).sum())

    # Rows where some "unexpected" columns are NA
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
    Preview which exog columns are non-numeric and how many values become NaN if coerced.
    (We DO NOT modify df here; this is a report-only check.)
    """
    exog_cols = [c for c in df.columns if c != "energy"]
    results = []
    for c in exog_cols:
        s = df[c]
        dtype = str(s.dtype)
        if dtype == "object":
            coerced = pd.to_numeric(s, errors="coerce")
            n_new_nan = int(coerced.isna().sum() - s.isna().sum())
            results.append({
                "column": c,
                "dtype": dtype,
                "n_rows": int(len(s)),
                "existing_nan": int(s.isna().sum()),
                "new_nan_if_coerced": n_new_nan,
                "example_values": [str(x) for x in s.dropna().astype(str).head(5).tolist()],
            })
    return {
        "object_columns_checked": len(results),
        "object_column_reports": results[:50],  # cap
        "note": "If new_nan_if_coerced > 0, you have non-numeric strings in exog.",
    }


def hybrid_split_preview(df: pd.DataFrame, cfg: IntegrityConfig) -> Dict[str, Any]:
    syn_end = pd.to_datetime(cfg.synthetic_end)
    real_start = pd.to_datetime(cfg.real_start)

    synthetic = df.loc[df.index <= syn_end]
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
        }
    }


def save_na_rows_sample(df: pd.DataFrame, out_csv: Path, cfg: IntegrityConfig) -> Dict[str, Any]:
    na_rows = df[df.isna().any(axis=1)]
    n = len(na_rows)
    if n == 0:
        return {"saved": False, "na_rows": 0, "path": None}

    sample = na_rows.head(cfg.sample_na_rows_max).copy()
    # put timestamp back as a column for easier viewing
    sample = sample.reset_index().rename(columns={"index": "timestamp"})
    sample.to_csv(out_csv, index=False)

    return {"saved": True, "na_rows": int(n), "sample_rows_saved": int(len(sample)), "path": str(out_csv)}


# =============================================================================
# Per-file runner
# =============================================================================

def run_one(csv_path: Path, cfg: IntegrityConfig) -> Dict[str, Any]:
    appliance = csv_path.stem
    log(f"--- START integrity: {appliance} ---")

    df = load_csv(csv_path)

    dup_ts = int(df.index.duplicated().sum())
    inferred = infer_frequency(df.index, cfg.infer_freq_head)

    gap_info = hourly_reindex_gap_report(df)
    na_info = na_stats(df)
    expected_na_info = expected_na_diagnosis(df, cfg)
    exog_preview = exog_type_coercion_preview(df)
    split_preview = hybrid_split_preview(df, cfg)

    out_dir = DEFAULT_OUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

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
            "duplicate_timestamps": dup_ts,
            "inferred_frequency_first_head": inferred,
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
        "duplicate_timestamps": dup_ts,
        "missing_hour_timestamps_count": int(gap_info.get("missing_hour_timestamps_count", -1)) if gap_info.get("ok") else None,
    }


# =============================================================================
# Main (NO ARGS)
# =============================================================================

def main() -> None:
    log("==============================================")
    log("Stage 3.5.2A — Data Integrity Report (Preflight)")
    log(f"Input dir : {DEFAULT_INPUT_DIR}")
    log(f"Output dir: {DEFAULT_OUT_DIR}")
    log(f"Glob     : {DEFAULT_GLOB}")
    log(f"Config   : {asdict(CFG)}")
    log("==============================================")

    if not DEFAULT_INPUT_DIR.exists():
        raise FileNotFoundError(f"DEFAULT_INPUT_DIR not found: {DEFAULT_INPUT_DIR}")

    files = sorted(DEFAULT_INPUT_DIR.glob(DEFAULT_GLOB))
    if not files:
        raise FileNotFoundError(f"No CSV files found in {DEFAULT_INPUT_DIR} with pattern {DEFAULT_GLOB}")

    summary: Dict[str, Any] = {
        "timestamp": datetime.now().isoformat(),
        "config": asdict(CFG),
        "input_dir": str(DEFAULT_INPUT_DIR),
        "output_dir": str(DEFAULT_OUT_DIR),
        "n_files": len(files),
        "ok": 0,
        "failed": 0,
        "results": [],
        "failures": [],
    }

    for idx, f in enumerate(files, start=1):
        log(f"[{idx}/{len(files)}] Integrity check: {f.name}")
        try:
            res = run_one(f, CFG)
            summary["results"].append(res)
            summary["ok"] += 1
        except Exception as e:
            tb = traceback.format_exc()
            err(f"[{idx}/{len(files)}] FAILED {f.name}: {e}")
            err(tb)
            summary["failed"] += 1
            summary["failures"].append({
                "file": str(f),
                "error": str(e),
                "traceback": tb
            })

    DEFAULT_OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary_path = DEFAULT_OUT_DIR / "_integrity_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    log("==============================================")
    log(f"[DONE] Integrity reports complete | OK={summary['ok']} FAILED={summary['failed']}")
    log(f"Summary: {summary_path}")
    log("==============================================")


if __name__ == "__main__":
    main()
