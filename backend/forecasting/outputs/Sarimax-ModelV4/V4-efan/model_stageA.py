"""
Outputs:
  reports/sarimax_premodel/
    - <appliance_file_stem>_premodel_report.json
    - _premodel_summary.json

"""

from __future__ import annotations

import json
import time
import traceback
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller, acf


# =============================================================================
# Defaults 
# =============================================================================

DEFAULT_INPUT_DIR = Path("data")
DEFAULT_OUT_DIR = Path("model/reports")
DEFAULT_GLOB = "*.csv"


# =============================================================================
# Simple Logger
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
# Helpers
# =============================================================================

REQUIRED_COLS = ["timestamp", "energy"]


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    log(f"Reading CSV: {path}")
    df = pd.read_csv(path)

    for c in REQUIRED_COLS:
        if c not in df.columns:
            raise ValueError(f"{path.name}: Missing required column: {c}")

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    bad_ts = int(df["timestamp"].isna().sum())
    if bad_ts > 0:
        raise ValueError(f"{path.name}: {bad_ts} rows have invalid timestamps")

    df = df.sort_values("timestamp")

    log(f"Loaded {path.name}: rows={len(df):,} | cols={len(df.columns)} | "
        f"range={df['timestamp'].min()} -> {df['timestamp'].max()}")

    # quick NaN info
    energy_nan = int(df["energy"].isna().sum())
    if energy_nan > 0:
        warn(f"{path.name}: energy has NaNs before reindex: {energy_nan:,}")

    return df


def _enforce_hourly_index(df: pd.DataFrame, cfg: PreModelConfig) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    info: Dict[str, Any] = {}

    log("Enforcing hourly index + integrity checks...")

    # duplicates
    dup_count = int(df["timestamp"].duplicated().sum())
    info["duplicate_timestamp_rows"] = dup_count
    if dup_count > 0:
        warn(f"Duplicate timestamps found: {dup_count:,} (keeping last)")
        df = df.drop_duplicates(subset=["timestamp"], keep="last").copy()

    df = df.set_index("timestamp").sort_index()

    inferred = pd.infer_freq(df.index[:200]) if len(df.index) >= 5 else None
    info["inferred_frequency_first_200"] = inferred
    log(f"Inferred frequency (first 200): {inferred}")

    full_idx = pd.date_range(df.index.min(), df.index.max(), freq="h")
    dfh = df.reindex(full_idx)

    info["start"] = str(dfh.index.min())
    info["end"] = str(dfh.index.max())
    info["n_rows_hourly_index"] = int(dfh.shape[0])

    missing_ts = int(dfh.index.size - df.index.size)
    info["missing_hour_timestamps_count"] = missing_ts
    log(f"Reindexed hourly: rows={dfh.shape[0]:,} | missing_timestamps={missing_ts:,}")

    is_missing = dfh["energy"].isna()
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
            length = b - a + 1
            gap_blocks.append({
                "gap_start": str(dfh.index[a]),
                "gap_end": str(dfh.index[b]),
                "gap_length_hours": int(length),
            })

    big_gaps = [g for g in gap_blocks if g["gap_length_hours"] >= cfg.gap_threshold_hours]
    info["gap_blocks_count"] = int(len(gap_blocks))
    info["gap_blocks_ge_threshold_count"] = int(len(big_gaps))
    info["gap_blocks_ge_threshold_examples"] = big_gaps[:10]

    if big_gaps:
        warn(f"Found gap blocks >= {cfg.gap_threshold_hours}h: {len(big_gaps)} (showing up to 10 in report)")
    else:
        log("No significant gap blocks found (>= threshold).")

    return dfh, info


def _adf_test(series: pd.Series, cfg: PreModelConfig, label: str, autolag: str = "AIC") -> Dict[str, Any]:
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
    log(f"ADF {label}: stat={out['adf_stat']:.4f} | p={out['p_value']:.6f} | n={out['n_obs']}")
    return out


def _seasonal_difference(x: pd.Series, s: int) -> pd.Series:
    return x - x.shift(s)


def _acf_at_lags(series: pd.Series, lags: List[int], max_lag: int) -> Dict[str, Optional[float]]:
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

    log("ACF signals: " + ", ".join([f"{k}={v:.4f}" if v is not None else f"{k}=None" for k, v in out.items()]))
    return out


def _suggest_d_D(adf_level: Dict[str, Any],
                 adf_diff1: Dict[str, Any],
                 adf_seas: Dict[str, Any],
                 cfg: PreModelConfig) -> Dict[str, Any]:
    def pval(adf_res: Dict[str, Any]) -> Optional[float]:
        return float(adf_res["p_value"]) if adf_res.get("ok") else None

    def is_stat(p: Optional[float]) -> bool:
        return (p is not None) and (p < cfg.adf_alpha)

    p_level = pval(adf_level)
    p_diff1 = pval(adf_diff1)
    p_seas = pval(adf_seas)

    level_stat = is_stat(p_level)
    diff1_stat = is_stat(p_diff1)
    seas_stat = is_stat(p_seas)

    d = 0 if level_stat else 1
    D = 1 if (not level_stat and seas_stat) else 0

    log(f"Suggested differencing: d={d}, D={D} "
        f"(p_level={p_level}, p_diff1={p_diff1}, p_seasonal={p_seas})")

    return {
        "rule_based_d": int(d),
        "rule_based_D": int(D),
        "p_values": {"level": p_level, "diff1": p_diff1, "seasonal": p_seas},
        "notes": {
            "level_stationary": bool(level_stat),
            "diff1_stationary": bool(diff1_stat),
            "seasonal_diff_stationary": bool(seas_stat),
        }
    }


def _run_one_file(input_csv: Path, out_dir: Path, cfg: PreModelConfig) -> Path:
    t0 = time.perf_counter()
    log(f"--- START file: {input_csv.name} ---")

    df = _read_csv(input_csv)
    dfh, integrity = _enforce_hourly_index(df, cfg)

    y = dfh["energy"]

    # ADF tests
    adf_level = _adf_test(y, cfg, "energy(level)")
    y_diff1 = y.diff(1)
    adf_diff1 = _adf_test(y_diff1, cfg, "energy(diff1)")

    y_seas = _seasonal_difference(y, cfg.seasonal_period)
    adf_seas = _adf_test(y_seas, cfg, f"energy(seasonal_diff_s={cfg.seasonal_period})")

    y_diff1_seas = _seasonal_difference(y_diff1, cfg.seasonal_period)
    adf_diff1_seas = _adf_test(y_diff1_seas, cfg, f"energy(diff1_then_seasonal_s={cfg.seasonal_period})")

    y_seas_diff1 = _seasonal_difference(y, cfg.seasonal_period).diff(1)
    adf_seas_diff1 = _adf_test(y_seas_diff1, cfg, f"energy(seasonal_s={cfg.seasonal_period}_then_diff1)")

    # ACF signals
    acf_signals = _acf_at_lags(
        y,
        lags=[cfg.seasonal_period, cfg.weekly_period],
        max_lag=cfg.max_acf_lag
    )

    suggestion = _suggest_d_D(adf_level, adf_diff1, adf_seas, cfg)

    report = {
        "input_file": str(input_csv),
        "appliance_key": input_csv.stem,
        "config": asdict(cfg),
        "integrity": integrity,
        "adf": {
            "level_energy": adf_level,
            "diff1_energy": adf_diff1,
            "seasonal_diff_energy_s": adf_seas,
            "diff1_then_seasonal_s": adf_diff1_seas,
            "seasonal_s_then_diff1": adf_seas_diff1,
        },
        "seasonality_signals": acf_signals,
        "suggested_differencing": suggestion,
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{input_csv.stem}_premodel_report.json"
    log(f"Writing report: {out_path}")
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    dt = time.perf_counter() - t0
    log(f"--- DONE file: {input_csv.name} | elapsed={dt:.2f}s ---")
    return out_path


# =============================================================================
# Main
# =============================================================================

def main() -> None:
    t_all = time.perf_counter()
    cfg = PreModelConfig()

    in_dir = DEFAULT_INPUT_DIR
    out_dir = DEFAULT_OUT_DIR

    log("==============================================")
    log("Stage 3.5.1 — Pre-Modeling Checks (SARIMAX)")
    log(f"Input dir : {in_dir}")
    log(f"Output dir: {out_dir}")
    log(f"Glob      : {DEFAULT_GLOB}")
    log(f"Config    : {asdict(cfg)}")
    log("==============================================")

    if not in_dir.exists():
        raise FileNotFoundError(
            f"DEFAULT_INPUT_DIR not found: {in_dir}\n"
            f"Edit DEFAULT_INPUT_DIR at top of the script to your real folder."
        )

    files = sorted(in_dir.glob(DEFAULT_GLOB))
    if not files:
        raise FileNotFoundError(f"No CSV files found in {in_dir} with pattern {DEFAULT_GLOB}")

    log(f"Discovered {len(files)} appliance CSV files.")

    summary: Dict[str, Any] = {
        "config": asdict(cfg),
        "input_dir": str(in_dir),
        "n_files": len(files),
        "files": [],
        "failures": [],
    }

    ok = 0
    fail = 0

    for idx, f in enumerate(files, start=1):
        log(f"[{idx}/{len(files)}] Processing: {f.name}")
        try:
            out_path = _run_one_file(f, out_dir, cfg)
            ok += 1
            summary["files"].append({
                "input": str(f),
                "output": str(out_path),
                "appliance_key": f.stem,
            })
        except Exception as e:
            fail += 1
            err(f"[{idx}/{len(files)}] FAILED: {f.name}: {e}")
            tb = traceback.format_exc()
            err(tb)
            summary["failures"].append({
                "input": str(f),
                "appliance_key": f.stem,
                "error": str(e),
                "traceback": tb,
            })

    summary["ok"] = ok
    summary["failed"] = fail

    out_dir.mkdir(parents=True, exist_ok=True)
    summary_path = out_dir / "_premodel_summary.json"
    log(f"Writing summary: {summary_path}")
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    total_dt = time.perf_counter() - t_all
    log("==============================================")
    log(f"[DONE] Pre-model checks complete | elapsed={total_dt:.2f}s")
    log(f"OK={ok} | FAILED={fail}")
    log(f"Summary: {summary_path}")
    log("==============================================")


if __name__ == "__main__":
    main()