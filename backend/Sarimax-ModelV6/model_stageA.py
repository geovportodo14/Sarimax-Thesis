#!/usr/bin/env python3
"""
Stage 3.5.1 - Pre-Modeling Checks (SARIMAX)

Summary:
This script runs batch pre-model diagnostics for each per-appliance model-ready
CSV used in the SARIMAX pipeline. It validates the hourly time index, checks
for gaps and duplicate timestamps, runs ADF stationarity tests on multiple
transformed versions of the energy series, computes key ACF signals, and
produces a guided differencing recommendation.

Instead of relying only on one rule-based (d, D) suggestion, this stage keeps
the ADF-based suggestion as the anchor and also generates a small set of nearby
differencing candidates that can be tested in the later modeling stage.

Input flow:
data/
  -> <appliance_model_ready>.csv

Processing flow:
per-appliance CSV
  -> validate required columns
  -> parse and sort timestamps
  -> enforce hourly index
  -> detect duplicate timestamps and missing hourly gaps
  -> run ADF on:
       level series
       first difference
       seasonal difference
       first difference then seasonal difference
       seasonal difference then first difference
  -> compute ACF at daily and weekly lags
  -> generate ADF-based anchor suggestion for d and D
  -> generate a small guided candidate set around the anchor suggestion

Output flow:
model/
  -> sarimax/
     -> <appliance_csv_stem>/
        -> premodel/
           -> <appliance_csv_stem>_premodel_report.json
     -> _premodel_summary.json
"""

from __future__ import annotations

import json
import time
import traceback
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import acf, adfuller


# =============================================================================
# Defaults
# =============================================================================

DEFAULT_INPUT_DIR = Path("data")
DEFAULT_SARIMAX_DIR = Path("model/sarimax")
DEFAULT_GLOB = "*.csv"

REQUIRED_COLS = ["timestamp", "energy"]


# =============================================================================
# Simple logger
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
class PreModelConfig:
    seasonal_period: int = 24
    weekly_period: int = 168
    adf_alpha: float = 0.05
    max_acf_lag: int = 200
    gap_threshold_hours: int = 2
    min_adf_samples: int = 50


# =============================================================================
# Path helpers
# =============================================================================

def get_premodel_output_dir(appliance: str) -> Path:
    """
    Build the premodel output folder for one appliance.
    """
    out_dir = DEFAULT_SARIMAX_DIR / appliance / "premodel"
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def get_summary_output_path() -> Path:
    """
    Keep the batch summary at the root SARIMAX folder.
    """
    DEFAULT_SARIMAX_DIR.mkdir(parents=True, exist_ok=True)
    return DEFAULT_SARIMAX_DIR / "_premodel_summary.json"


# =============================================================================
# Data loading and integrity helpers
# =============================================================================

def read_csv(path: Path) -> pd.DataFrame:
    """
    Load one appliance CSV and enforce the required base schema.
    """
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    log(f"Reading CSV: {path}")
    df = pd.read_csv(path)

    for col in REQUIRED_COLS:
        if col not in df.columns:
            raise ValueError(f"{path.name}: Missing required column: {col}")

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    bad_timestamps = int(df["timestamp"].isna().sum())
    if bad_timestamps > 0:
        raise ValueError(f"{path.name}: {bad_timestamps} rows have invalid timestamps")

    df = df.sort_values("timestamp")

    log(
        f"Loaded {path.name}: rows={len(df):,} | cols={len(df.columns)} | "
        f"range={df['timestamp'].min()} -> {df['timestamp'].max()}"
    )

    energy_nan = int(df["energy"].isna().sum())
    if energy_nan > 0:
        warn(f"{path.name}: energy has NaNs before reindex: {energy_nan:,}")

    return df


def enforce_hourly_index(
    df: pd.DataFrame,
    cfg: PreModelConfig,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Reindex to hourly frequency and summarize integrity issues.
    """
    info: Dict[str, Any] = {}

    log("Enforcing hourly index + integrity checks...")

    duplicate_count = int(df["timestamp"].duplicated().sum())
    info["duplicate_timestamp_rows"] = duplicate_count

    if duplicate_count > 0:
        warn(f"Duplicate timestamps found: {duplicate_count:,} (keeping last)")
        df = df.drop_duplicates(subset=["timestamp"], keep="last").copy()

    df = df.set_index("timestamp").sort_index()

    inferred = pd.infer_freq(df.index[:200]) if len(df.index) >= 5 else None
    info["inferred_frequency_first_200"] = inferred
    log(f"Inferred frequency (first 200): {inferred}")

    full_idx = pd.date_range(df.index.min(), df.index.max(), freq="h")
    df_hourly = df.reindex(full_idx)

    info["start"] = str(df_hourly.index.min())
    info["end"] = str(df_hourly.index.max())
    info["n_rows_hourly_index"] = int(df_hourly.shape[0])

    missing_timestamps = int(df_hourly.index.size - df.index.size)
    info["missing_hour_timestamps_count"] = missing_timestamps
    log(
        f"Reindexed hourly: rows={df_hourly.shape[0]:,} | "
        f"missing_timestamps={missing_timestamps:,}"
    )

    is_missing = df_hourly["energy"].isna()
    gap_blocks: List[Dict[str, Any]] = []

    if is_missing.any():
        missing_idx = np.where(is_missing.values)[0]
        runs = []
        start = prev = int(missing_idx[0])

        for i in missing_idx[1:]:
            i = int(i)
            if i == prev + 1:
                prev = i
            else:
                runs.append((start, prev))
                start = prev = i
        runs.append((start, prev))

        for a, b in runs:
            gap_blocks.append({
                "gap_start": str(df_hourly.index[a]),
                "gap_end": str(df_hourly.index[b]),
                "gap_length_hours": int(b - a + 1),
            })

    big_gaps = [g for g in gap_blocks if g["gap_length_hours"] >= cfg.gap_threshold_hours]
    info["gap_blocks_count"] = int(len(gap_blocks))
    info["gap_blocks_ge_threshold_count"] = int(len(big_gaps))
    info["gap_blocks_ge_threshold_examples"] = big_gaps[:10]

    if big_gaps:
        warn(
            f"Found gap blocks >= {cfg.gap_threshold_hours}h: "
            f"{len(big_gaps)} (showing up to 10 in report)"
        )
    else:
        log("No significant gap blocks found (>= threshold).")

    return df_hourly, info


# =============================================================================
# Statistical diagnostics
# =============================================================================

def adf_test(
    series: pd.Series,
    cfg: PreModelConfig,
    label: str,
    autolag: str = "AIC",
) -> Dict[str, Any]:
    """
    Run the ADF test on one series variant.
    """
    log(f"ADF test: {label} ...")

    x = series.dropna().astype(float)
    n = len(x)

    if n < cfg.min_adf_samples:
        warn(f"ADF skipped ({label}): too few samples n={n}")
        return {"ok": False, "reason": f"Too few samples for ADF after dropping NaNs: n={n}"}

    res = adfuller(x.values, autolag=autolag)
    out = {
        "ok": True,
        "adf_stat": float(res[0]),
        "p_value": float(res[1]),
        "used_lag": int(res[2]),
        "n_obs": int(res[3]),
        "critical_values": {k: float(v) for k, v in res[4].items()},
        "ic_best": float(res[5]),
    }

    log(
        f"ADF {label}: stat={out['adf_stat']:.4f} | "
        f"p={out['p_value']:.6f} | n={out['n_obs']}"
    )
    return out


def seasonal_difference(series: pd.Series, period: int) -> pd.Series:
    """
    Apply seasonal differencing at the given period.
    """
    return series - series.shift(period)


def acf_at_lags(
    series: pd.Series,
    lags: List[int],
    max_lag: int,
) -> Dict[str, Optional[float]]:
    """
    Compute ACF values at selected lags.
    """
    log(f"Computing ACF signals at lags {lags} (max_lag={max_lag}) ...")

    x = series.dropna().astype(float)
    if len(x) < 20:
        warn("ACF skipped: too few samples after dropping NaNs")
        return {f"acf_lag_{lag}": None for lag in lags}

    max_lag_eff = min(max_lag, max(lags), max(10, len(x) // 2))
    acf_vals = acf(x.values, nlags=max_lag_eff, fft=True)

    out: Dict[str, Optional[float]] = {}
    for lag in lags:
        out[f"acf_lag_{lag}"] = float(acf_vals[lag]) if lag <= max_lag_eff else None

    log(
        "ACF signals: " + ", ".join(
            f"{k}={v:.4f}" if v is not None else f"{k}=None"
            for k, v in out.items()
        )
    )
    return out


def build_anchor_differencing_suggestion(
    adf_level: Dict[str, Any],
    adf_diff1: Dict[str, Any],
    adf_seasonal: Dict[str, Any],
    cfg: PreModelConfig,
) -> Dict[str, Any]:
    """
    Build the ADF-based anchor suggestion for d and D.
    """
    def pval(adf_res: Dict[str, Any]) -> Optional[float]:
        return float(adf_res["p_value"]) if adf_res.get("ok") else None

    def is_stationary(p: Optional[float]) -> bool:
        return (p is not None) and (p < cfg.adf_alpha)

    p_level = pval(adf_level)
    p_diff1 = pval(adf_diff1)
    p_seasonal = pval(adf_seasonal)

    level_stationary = is_stationary(p_level)
    diff1_stationary = is_stationary(p_diff1)
    seasonal_stationary = is_stationary(p_seasonal)

    d = 0 if level_stationary else 1
    D = 1 if (not level_stationary and seasonal_stationary) else 0

    log(
        f"Anchor differencing suggestion: d={d}, D={D} "
        f"(p_level={p_level}, p_diff1={p_diff1}, p_seasonal={p_seasonal})"
    )

    return {
        "rule_based_d": int(d),
        "rule_based_D": int(D),
        "p_values": {
            "level": p_level,
            "diff1": p_diff1,
            "seasonal": p_seasonal,
        },
        "notes": {
            "level_stationary": bool(level_stationary),
            "diff1_stationary": bool(diff1_stationary),
            "seasonal_diff_stationary": bool(seasonal_stationary),
        },
    }


def build_guided_differencing_candidates(
    anchor_d: int,
    anchor_D: int,
) -> Dict[str, Any]:
    """
    Build a small guided candidate set around the anchor (d, D).

    This keeps the recommendation controlled and easy to justify.
    """
    candidate_order = [
        (anchor_d, anchor_D),
        (max(0, anchor_d - 1), anchor_D),
        (anchor_d + 1, anchor_D),
        (anchor_d, max(0, anchor_D - 1)),
        (anchor_d, anchor_D + 1),
        (max(0, anchor_d - 1), max(0, anchor_D - 1)),
        (anchor_d + 1, anchor_D + 1),
    ]

    seen = set()
    candidates: List[Dict[str, int]] = []

    for d, D in candidate_order:
        key = (int(d), int(D))
        if key in seen:
            continue
        seen.add(key)
        candidates.append({"d": int(d), "D": int(D)})

    log(
        "Guided differencing candidates: " +
        ", ".join(f"(d={c['d']}, D={c['D']})" for c in candidates)
    )

    return {
        "anchor_candidate": {"d": int(anchor_d), "D": int(anchor_D)},
        "candidate_set": candidates,
        "note": (
            "Use the anchor candidate first, then test nearby candidates in the "
            "modeling stage using AIC/BIC or validation performance."
        ),
    }


# =============================================================================
# Per-file runner
# =============================================================================

def run_one_file(input_csv: Path, cfg: PreModelConfig) -> Path:
    """
    Run the full pre-model diagnostic workflow for one appliance CSV.
    """
    t0 = time.perf_counter()
    appliance = input_csv.stem
    log(f"--- START file: {input_csv.name} ---")

    df = read_csv(input_csv)
    df_hourly, integrity = enforce_hourly_index(df, cfg)

    y = df_hourly["energy"]

    # Run ADF on the original and transformed series used for diagnostics.
    adf_level = adf_test(y, cfg, "energy(level)")

    y_diff1 = y.diff(1)
    adf_diff1 = adf_test(y_diff1, cfg, "energy(diff1)")

    y_seasonal = seasonal_difference(y, cfg.seasonal_period)
    adf_seasonal = adf_test(
        y_seasonal,
        cfg,
        f"energy(seasonal_diff_s={cfg.seasonal_period})",
    )

    y_diff1_then_seasonal = seasonal_difference(y_diff1, cfg.seasonal_period)
    adf_diff1_then_seasonal = adf_test(
        y_diff1_then_seasonal,
        cfg,
        f"energy(diff1_then_seasonal_s={cfg.seasonal_period})",
    )

    y_seasonal_then_diff1 = seasonal_difference(y, cfg.seasonal_period).diff(1)
    adf_seasonal_then_diff1 = adf_test(
        y_seasonal_then_diff1,
        cfg,
        f"energy(seasonal_s={cfg.seasonal_period}_then_diff1)",
    )

    acf_signals = acf_at_lags(
        y,
        lags=[cfg.seasonal_period, cfg.weekly_period],
        max_lag=cfg.max_acf_lag,
    )

    anchor_suggestion = build_anchor_differencing_suggestion(
        adf_level,
        adf_diff1,
        adf_seasonal,
        cfg,
    )

    guided_candidates = build_guided_differencing_candidates(
        anchor_d=anchor_suggestion["rule_based_d"],
        anchor_D=anchor_suggestion["rule_based_D"],
    )

    report = {
        "input_file": str(input_csv),
        "appliance_key": appliance,
        "config": asdict(cfg),
        "integrity": integrity,
        "adf": {
            "level_energy": adf_level,
            "diff1_energy": adf_diff1,
            "seasonal_diff_energy_s": adf_seasonal,
            "diff1_then_seasonal_s": adf_diff1_then_seasonal,
            "seasonal_s_then_diff1": adf_seasonal_then_diff1,
        },
        "seasonality_signals": acf_signals,
        "suggested_differencing": anchor_suggestion,
        "guided_differencing_candidates": guided_candidates,
    }

    out_dir = get_premodel_output_dir(appliance)
    out_path = out_dir / f"{appliance}_premodel_report.json"

    log(f"Writing report: {out_path}")
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    elapsed = time.perf_counter() - t0
    log(f"--- DONE file: {input_csv.name} | elapsed={elapsed:.2f}s ---")
    return out_path


# =============================================================================
# Main
# =============================================================================

def main() -> None:
    t_all = time.perf_counter()
    cfg = PreModelConfig()

    log("==============================================")
    log("Stage 3.5.1 - Pre-Modeling Checks (SARIMAX)")
    log(f"Input dir   : {DEFAULT_INPUT_DIR}")
    log(f"SARIMAX dir : {DEFAULT_SARIMAX_DIR}")
    log(f"Glob        : {DEFAULT_GLOB}")
    log(f"Config      : {asdict(cfg)}")
    log("==============================================")

    if not DEFAULT_INPUT_DIR.exists():
        raise FileNotFoundError(
            f"DEFAULT_INPUT_DIR not found: {DEFAULT_INPUT_DIR}\n"
            f"Edit DEFAULT_INPUT_DIR at top of the script to your real folder."
        )

    files = sorted(DEFAULT_INPUT_DIR.glob(DEFAULT_GLOB))
    if not files:
        raise FileNotFoundError(
            f"No CSV files found in {DEFAULT_INPUT_DIR} with pattern {DEFAULT_GLOB}"
        )

    log(f"Discovered {len(files)} appliance CSV files.")

    summary: Dict[str, Any] = {
        "config": asdict(cfg),
        "input_dir": str(DEFAULT_INPUT_DIR),
        "output_dir": str(DEFAULT_SARIMAX_DIR),
        "n_files": len(files),
        "files": [],
        "failures": [],
    }

    ok = 0
    failed = 0

    for idx, file_path in enumerate(files, start=1):
        log(f"[{idx}/{len(files)}] Processing: {file_path.name}")
        try:
            out_path = run_one_file(file_path, cfg)
            ok += 1
            summary["files"].append({
                "input": str(file_path),
                "output": str(out_path),
                "appliance_key": file_path.stem,
            })
        except Exception as e:
            failed += 1
            tb = traceback.format_exc()
            err(f"[{idx}/{len(files)}] FAILED: {file_path.name}: {e}")
            err(tb)
            summary["failures"].append({
                "input": str(file_path),
                "appliance_key": file_path.stem,
                "error": str(e),
                "traceback": tb,
            })

    summary["ok"] = ok
    summary["failed"] = failed

    summary_path = get_summary_output_path()
    log(f"Writing summary: {summary_path}")
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    total_elapsed = time.perf_counter() - t_all
    log("==============================================")
    log(f"[DONE] Pre-model checks complete | elapsed={total_elapsed:.2f}s")
    log(f"OK={ok} | FAILED={failed}")
    log(f"Summary: {summary_path}")
    log("==============================================")


if __name__ == "__main__":
    main()