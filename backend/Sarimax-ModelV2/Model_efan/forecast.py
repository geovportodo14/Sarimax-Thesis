#!/usr/bin/env python3
"""
Stage 3.5.4 — Operational Next-24h Forecast (SARIMAX)

Purpose:
    Generate a single future 24-hour forecast AFTER the last timestamp
    in each model-ready CSV.

Example output:
    If the last observed timestamp is:
        2026-02-27 00:00:00
    this script will forecast:
        2026-02-27 01:00:00
        2026-02-27 02:00:00
        ...
        2026-02-28 00:00:00

Inputs expected per appliance:
    data/<appliance>.csv
    model/sarimax/<appliance>/
        best_model.pkl
        best_params.json

Outputs:
    model/sarimax/<appliance>/forecast/forecast_YYYY-MM-DD.csv

Notes:
    - This is NOT evaluation.
    - This is deployment/operational forecasting.
    - If future exogenous values do not exist, the script:
        * generates future-known calendar features
        * forward-fills remaining exogenous variables
          using the last observed row
"""

from __future__ import annotations

import argparse
import json
import traceback
import warnings
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAXResults

warnings.filterwarnings("ignore")


# =============================================================================
# Defaults
# =============================================================================

DEFAULT_INPUT_DIR = Path("data")
DEFAULT_MODELS_ROOT = Path("model/sarimax")
DEFAULT_GLOB = "*.csv"


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
class ForecastConfig:
    horizon: int = 24


# =============================================================================
# IO Helpers
# =============================================================================

def load_full_dataset(csv_path: Path) -> pd.DataFrame:
    log(f"Loading dataset: {csv_path}")
    df = pd.read_csv(csv_path)

    if "timestamp" not in df.columns or "energy" not in df.columns:
        raise ValueError(f"{csv_path.name}: must contain 'timestamp' and 'energy'")

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    bad = int(df["timestamp"].isna().sum())
    if bad:
        raise ValueError(f"{csv_path.name}: {bad} invalid timestamps")

    df = df.sort_values("timestamp").set_index("timestamp")

    if df.index.has_duplicates:
        raise ValueError(f"{csv_path.name}: duplicate timestamps found")

    log(f"Loaded rows={len(df):,} | range={df.index.min()} -> {df.index.max()}")
    return df


def load_best_params(appliance_dir: Path) -> Dict[str, Any]:
    p = appliance_dir / "best_params.json"
    if not p.exists():
        raise FileNotFoundError(f"Missing best_params.json: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def load_best_model(appliance_dir: Path) -> SARIMAXResults:
    p = appliance_dir / "best_model.pkl"
    if not p.exists():
        raise FileNotFoundError(f"Missing best_model.pkl: {p}")
    log(f"Loading best model: {p}")
    return SARIMAXResults.load(str(p))


def detect_exog_columns(df: pd.DataFrame) -> List[str]:
    return [c for c in df.columns if c != "energy"]


def ensure_numeric_exog(X: pd.DataFrame) -> pd.DataFrame:
    out = X.copy()
    for c in out.columns:
        if pd.api.types.is_bool_dtype(out[c]):
            out[c] = out[c].astype(int)
        elif out[c].dtype == "object":
            out[c] = pd.to_numeric(out[c], errors="coerce")
    return out


def clean_for_model(df: pd.DataFrame, exog_cols: List[str]) -> pd.DataFrame:
    cols = ["energy"] + exog_cols
    cols = [c for c in cols if c in df.columns]
    out = df[cols].copy()

    # Drop rows that would break forecasting/training state consistency
    out = out.dropna()

    if len(out) == 0:
        raise ValueError("No valid rows remain after dropping NaNs from required columns")

    return out


# =============================================================================
# Future exog builder
# =============================================================================

def build_future_exog(
    df_full: pd.DataFrame,
    exog_cols: List[str],
    future_idx: pd.DatetimeIndex,
) -> Optional[pd.DataFrame]:
    if not exog_cols:
        return None

    Xf = pd.DataFrame(index=future_idx, columns=exog_cols)

    # Generate future-known calendar features if present
    if "hour_of_day" in Xf.columns:
        Xf["hour_of_day"] = future_idx.hour

    if "day_of_week" in Xf.columns:
        Xf["day_of_week"] = future_idx.dayofweek

    if "is_weekend" in Xf.columns:
        Xf["is_weekend"] = (future_idx.dayofweek >= 5).astype(int)

    # Optional common calendar flags
    if "month" in Xf.columns:
        Xf["month"] = future_idx.month

    if "day" in Xf.columns:
        Xf["day"] = future_idx.day

    if "day_of_month" in Xf.columns:
        Xf["day_of_month"] = future_idx.day

    if "day_of_year" in Xf.columns:
        Xf["day_of_year"] = future_idx.dayofyear

    if "week_of_year" in Xf.columns:
        iso = future_idx.isocalendar()
        Xf["week_of_year"] = iso.week.astype(int).to_numpy()

    if "is_month_start" in Xf.columns:
        Xf["is_month_start"] = future_idx.is_month_start.astype(int)

    if "is_month_end" in Xf.columns:
        Xf["is_month_end"] = future_idx.is_month_end.astype(int)

    # Fill remaining columns using last observed values
    last_row = df_full[exog_cols].iloc[-1]

    for c in exog_cols:
        if Xf[c].isna().any():
            Xf[c] = Xf[c].fillna(last_row[c])

    Xf = ensure_numeric_exog(Xf)

    # Final safeguard
    missing_cols = Xf.columns[Xf.isna().any()].tolist()
    if missing_cols:
        raise RuntimeError(
            f"Could not construct future exog. Remaining NaN columns: {missing_cols}"
        )

    return Xf


# =============================================================================
# Forecast core
# =============================================================================

def forecast_next_24h(
    df_full: pd.DataFrame,
    model_dir: Path,
    appliance: str,
    cfg: ForecastConfig,
) -> pd.DataFrame:
    best_params = load_best_params(model_dir)
    res = load_best_model(model_dir)

    exog_cols = best_params.get("exog_columns", detect_exog_columns(df_full))
    exog_cols = [c for c in exog_cols if c in df_full.columns and c != "energy"]

    last_ts = df_full.index.max()
    future_idx = pd.date_range(
        start=last_ts + pd.Timedelta(hours=1),
        periods=cfg.horizon,
        freq="h",
    )

    Xf = build_future_exog(df_full, exog_cols, future_idx)

    log(
        f"{appliance}: forecasting next {cfg.horizon} hours "
        f"from {future_idx.min()} to {future_idx.max()}"
    )

    fc = res.get_forecast(steps=cfg.horizon, exog=Xf).predicted_mean
    fc.index = future_idx
    fc = fc.clip(lower=0.0)

    out = pd.DataFrame({
        "timestamp": future_idx,
        "pred_energy": fc.values,
    })
    out["pred_energy_4dp"] = out["pred_energy"].round(4)

    return out


# =============================================================================
# Main
# =============================================================================

def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Stage 3.5.4 Operational Next-24h Forecast")
    p.add_argument("--horizon", type=int, default=24, help="Forecast horizon in hours")
    p.add_argument("--appliance", type=str, default=None, help="Optional CSV stem to run only one appliance")
    return p


def main() -> None:
    args = build_argparser().parse_args()

    cfg = ForecastConfig(horizon=int(args.horizon))

    log("==============================================")
    log("Stage 3.5.4 — Operational Next-24h Forecast")
    log(f"Input dir   : {DEFAULT_INPUT_DIR}")
    log(f"Models root : {DEFAULT_MODELS_ROOT}")
    log(f"Config      : {asdict(cfg)}")
    log("==============================================")

    if not DEFAULT_INPUT_DIR.exists():
        raise FileNotFoundError(f"Input dir not found: {DEFAULT_INPUT_DIR}")

    if not DEFAULT_MODELS_ROOT.exists():
        raise FileNotFoundError(f"Models root not found: {DEFAULT_MODELS_ROOT}")

    csvs = sorted(DEFAULT_INPUT_DIR.glob(DEFAULT_GLOB))
    if not csvs:
        raise FileNotFoundError(f"No CSV files found in {DEFAULT_INPUT_DIR} with pattern {DEFAULT_GLOB}")

    if args.appliance:
        csvs = [p for p in csvs if p.stem == args.appliance]
        if not csvs:
            raise FileNotFoundError(f"No CSV found for appliance stem: {args.appliance}")

    summary: Dict[str, Any] = {
        "timestamp": datetime.now().isoformat(),
        "config": asdict(cfg),
        "input_dir": str(DEFAULT_INPUT_DIR),
        "models_root": str(DEFAULT_MODELS_ROOT),
        "ok": 0,
        "failed": 0,
        "results": [],
        "failures": [],
    }

    for idx, csv_path in enumerate(csvs, start=1):
        appliance = csv_path.stem
        model_dir = DEFAULT_MODELS_ROOT / appliance

        if not model_dir.exists():
            warn(f"[{idx}/{len(csvs)}] Skip (no model dir): {appliance}")
            continue

        log(f"[{idx}/{len(csvs)}] Forecasting: {appliance}")

        try:
            df_full = load_full_dataset(csv_path)

            best_params = load_best_params(model_dir)
            exog_cols = best_params.get("exog_columns", detect_exog_columns(df_full))
            exog_cols = [c for c in exog_cols if c in df_full.columns and c != "energy"]

            df_full_clean = clean_for_model(df_full, exog_cols)

            fc = forecast_next_24h(df_full_clean, model_dir, appliance, cfg)

            # Sanity checks
            if len(fc) != cfg.horizon:
                raise ValueError(f"Expected {cfg.horizon} forecast rows, got {len(fc)}")

            ts = pd.to_datetime(fc["timestamp"], errors="coerce")
            if ts.isna().any():
                raise ValueError("Forecast contains invalid timestamps")
            if not ts.is_monotonic_increasing:
                raise ValueError("Forecast timestamps are not sorted")
            if len(ts) > 1 and not (ts.diff().dropna() == pd.Timedelta(hours=1)).all():
                raise ValueError("Forecast timestamps are not hourly")

            forecast_dir = model_dir / "forecast"
            forecast_dir.mkdir(parents=True, exist_ok=True)

            day_str = ts.iloc[0].strftime("%Y-%m-%d")
            out_path = forecast_dir / f"forecast_{day_str}.csv"

            log(f"Saving forecast: {out_path}")
            fc.to_csv(out_path, index=False)

            summary["results"].append({
                "appliance": appliance,
                "status": "ok",
                "last_observed_timestamp": str(df_full_clean.index.max()),
                "forecast_start": str(fc["timestamp"].min()),
                "forecast_end": str(fc["timestamp"].max()),
                "n_rows": int(len(fc)),
                "artifact": str(out_path),
            })
            summary["ok"] += 1

            log(
                f"[{idx}/{len(csvs)}] OK {appliance} | "
                f"forecast_start={fc['timestamp'].min()} | "
                f"forecast_end={fc['timestamp'].max()}"
            )

        except Exception as e:
            tb = traceback.format_exc()
            err(f"[{idx}/{len(csvs)}] FAILED {appliance}: {e}")
            err(tb)

            summary["failed"] += 1
            summary["failures"].append({
                "appliance": appliance,
                "input": str(csv_path),
                "error": str(e),
                "traceback": tb,
            })

    summary_dir = DEFAULT_MODELS_ROOT / "forecast"
    summary_dir.mkdir(parents=True, exist_ok=True)
    summary_path = summary_dir / "_forecast_summary.json"

    log(f"Writing forecast summary: {summary_path}")
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    log("==============================================")
    log(f"[DONE] Forecasting complete | OK={summary['ok']} | FAILED={summary['failed']}")
    log(f"Summary: {summary_path}")
    log("==============================================")


if __name__ == "__main__":
    main()