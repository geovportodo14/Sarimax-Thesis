#!/usr/bin/env python3
"""
Rolling-Origin Evaluation (24h Horizon)

Summary:
This script evaluates each fitted SARIMAX appliance model using a daily
rolling-origin setup over the REAL TEST portion only. For each valid daily origin at 00:00, the model is re-fitted using all data
available up to that origin, then forecasts the next 24 hours and scores the
forecast against the observed hourly energy values.

To make the evaluation outputs more useful, this stage saves both:
- final scored predictions using clipped non-negative forecasts
- raw predictions before clipping for diagnostic inspection

Input flow:
data/
  -> <appliance_model_ready>.csv

model/
  -> sarimax/
     -> <appliance_csv_stem>/
        -> model/
           -> best_model.pkl
           -> best_params.json
           -> split_manifest.json

Processing flow:
full model-ready CSV
  -> load best fitted SARIMAX artifacts
  -> load split manifest
  -> isolate REAL TEST window only
  -> detect exogenous columns used by the selected model
  -> clean data for evaluation
  -> build daily rolling origins at 00:00 inside REAL TEST
  -> for each origin:
       -> refit using all prior data up to the origin
       -> forecast the next 24 hours
       -> keep raw forecast values
       -> clip forecast values at 0 for scoring
       -> store forecasts within the real test window
  -> align actuals with forecasts
  -> compute evaluation metrics
  -> compute residual diagnostics
  -> export evaluation artifacts

Output flow:
model/
  -> sarimax/
     -> <appliance_csv_stem>/
        -> evaluation/
           -> eval_predictions.csv
           -> eval_predictions_raw.csv
           -> eval_metrics.json
           -> eval_residual_diagnostics.json
           -> eval_residual_heatmap.csv
           -> eval_daily_metrics.csv
            -> eval_hourly_error.csv
            -> eval_dayofweek_error.csv
            -> eval_weekend_error.csv
            -> eval_peak_vs_nonpeak.json
            -> eval_zero_vs_nonzero.json
            -> eval_residual_vs_weather.csv 
            -> eval_residual_feature_table.csv
     -> _eval_summary.json
"""

from __future__ import annotations

import argparse
import json
import time
import traceback
import warnings
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.stattools import acf, pacf
from statsmodels.tsa.statespace.sarimax import SARIMAX, SARIMAXResults

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
class EvalConfig:
    horizon: int = 24
    # refit_every: int = 1
    min_train_rows: int = 300

    ljungbox_lags: int = 24
    max_acf_lag: int = 48
    max_pacf_lag: int = 48

    progress_every: int = 10


# =============================================================================
# Metrics
# =============================================================================

def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(np.abs(y_true - y_pred)))


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def nrmse(y_true: np.ndarray, y_pred: np.ndarray, eps: float = 1e-9) -> float:
    mean_true = float(np.mean(y_true))
    return float(rmse(y_true, y_pred) / max(mean_true, eps))


def smape(y_true: np.ndarray, y_pred: np.ndarray, eps: float = 1e-9) -> float:
    denom = np.maximum(np.abs(y_true) + np.abs(y_pred), eps)
    return float(np.mean(2.0 * np.abs(y_pred - y_true) / denom) * 100.0)


def mape_nonzero(y_true: np.ndarray, y_pred: np.ndarray, eps: float = 1e-9) -> float:
    mask = np.abs(y_true) > eps
    if not np.any(mask):
        return float("nan")
    return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100.0)


def r2(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    ss_res = float(np.sum((y_true - y_pred) ** 2))
    ss_tot = float(np.sum((y_true - np.mean(y_true)) ** 2))
    if ss_tot <= 0:
        return float("nan")
    return float(1.0 - ss_res / ss_tot)


# =============================================================================
# IO helpers
# =============================================================================

def load_full_dataset(csv_path: Path) -> pd.DataFrame:
    """
    Load one full model-ready appliance dataset.
    """
    log(f"Loading full model-ready dataset: {csv_path}")
    df = pd.read_csv(csv_path)

    if "timestamp" not in df.columns or "energy" not in df.columns:
        raise ValueError(f"{csv_path.name}: must contain 'timestamp' and 'energy'")

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    bad_timestamps = int(df["timestamp"].isna().sum())
    if bad_timestamps:
        raise ValueError(f"{csv_path.name}: {bad_timestamps} invalid timestamps")

    df = df.sort_values("timestamp").set_index("timestamp")
    log(f"Loaded {csv_path.name}: rows={len(df):,} | range={df.index.min()} -> {df.index.max()}")
    return df


def load_split_manifest(model_dir: Path) -> Dict[str, Any]:
    """
    Load the saved train/test split manifest.
    """
    path = model_dir / "model" / "split_manifest.json"
    if not path.exists():
        raise FileNotFoundError(f"Missing split_manifest.json: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_best_params(model_dir: Path) -> Dict[str, Any]:
    """
    Load the saved best-model parameter summary.
    """
    path = model_dir / "model" / "best_params.json"
    if not path.exists():
        raise FileNotFoundError(f"Missing best_params.json: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_best_model(model_dir: Path) -> SARIMAXResults:
    """
    Load the saved best fitted model.
    """
    path = model_dir / "model" / "best_model.pkl"
    if not path.exists():
        raise FileNotFoundError(f"Missing best_model.pkl: {path}")
    log(f"Loading best model: {path}")
    return SARIMAXResults.load(str(path))


def get_evaluation_output_dir(model_dir: Path) -> Path:
    """
    Build the evaluation output folder for one appliance.
    """
    out_dir = model_dir / "evaluation"
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def detect_exog_columns(df: pd.DataFrame) -> List[str]:
    """
    Detect all possible exogenous columns from the dataset.
    """
    return [col for col in df.columns if col != "energy"]


def ensure_numeric_exog(X: pd.DataFrame) -> pd.DataFrame:
    """
    Coerce exogenous columns to numeric form for forecasting.
    """
    out = X.copy()
    for col in out.columns:
        if pd.api.types.is_bool_dtype(out[col]):
            out[col] = out[col].astype(int)
        if out[col].dtype == "object":
            out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def clean_for_model(df: pd.DataFrame, exog_cols: List[str]) -> pd.DataFrame:
    """
    Keep only model-needed columns and drop rows with missing values.
    """
    cols = ["energy"] + exog_cols
    cols = [col for col in cols if col in df.columns]
    return df[cols].dropna().copy()


def slice_real_test(
    df: pd.DataFrame,
    manifest: Dict[str, Any],
) -> Tuple[pd.DataFrame, pd.Timestamp, pd.Timestamp]:
    """
    Slice only the REAL TEST window using the saved split manifest.
    """
    real_test_range = manifest.get("ranges", {}).get("real_test")
    if not real_test_range or not isinstance(real_test_range, list) or len(real_test_range) != 2:
        raise ValueError("split_manifest missing ranges.real_test")

    start = pd.to_datetime(real_test_range[0])
    end = pd.to_datetime(real_test_range[1])

    test = df.loc[(df.index >= start) & (df.index <= end)].copy()
    if len(test) == 0:
        raise RuntimeError(f"REAL TEST slice empty for range {start} -> {end}")

    return test, start, end


def build_train_upto(df: pd.DataFrame, origin: pd.Timestamp) -> pd.DataFrame:
    """
    Build the expanding training window up to but not including the origin.
    """
    return df.loc[df.index < origin].copy()


def build_forecast_inputs(
    df_full: pd.DataFrame,
    origin: pd.Timestamp,
    horizon: int,
    exog_cols: List[str],
) -> Tuple[pd.DatetimeIndex, Optional[pd.DataFrame]]:
    """
    Build the forecast index and exogenous inputs for one horizon.
    """
    idx = pd.date_range(origin, periods=horizon, freq="h")

    if exog_cols:
        X_forecast = df_full.reindex(idx)[exog_cols]
        X_forecast = ensure_numeric_exog(X_forecast)
        return idx, X_forecast

    return idx, None

def compute_metric_bundle(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """
    Compute the main evaluation metrics for one prediction set.
    """
    return {
        "MAE": mae(y_true, y_pred),
        "RMSE": rmse(y_true, y_pred),
        "NRMSE": nrmse(y_true, y_pred),
        "sMAPE": smape(y_true, y_pred),
        "MAPE_nonzero": mape_nonzero(y_true, y_pred),
        "R2": r2(y_true, y_pred),
    }


def build_daily_metrics(predictions: pd.DataFrame) -> pd.DataFrame:
    """
    Compute one metrics row per forecast day so unstable days are easy to inspect.
    """
    rows: List[Dict[str, Any]] = []

    if predictions.empty:
        return pd.DataFrame(columns=[
            "date",
            "n_hours",
            "n_raw_negative_predictions",
            "pct_raw_negative_predictions",
            "MAE",
            "RMSE",
            "NRMSE",
            "sMAPE",
            "MAPE_nonzero",
            "R2",
        ])

    work = predictions.copy()
    work["date"] = work.index.date

    for date_value, grp in work.groupby("date"):
        y_true = grp["actual_energy"].values
        y_pred = grp["pred_energy"].values
        y_pred_raw = grp["pred_energy_raw"].values

        metric_row = compute_metric_bundle(y_true, y_pred)

        rows.append({
            "date": str(date_value),
            "n_hours": int(len(grp)),
            "n_raw_negative_predictions": int((y_pred_raw < 0).sum()),
            "pct_raw_negative_predictions": float((y_pred_raw < 0).mean() * 100.0),
            **metric_row,
        })

    return pd.DataFrame(rows).sort_values("date").reset_index(drop=True)

def build_hourly_error_table(predictions: pd.DataFrame) -> pd.DataFrame:
    """
    Summarize forecast error by hour of day.
    """
    if predictions.empty:
        return pd.DataFrame(columns=[
            "hour",
            "n",
            "residual_mean",
            "residual_std",
            "MAE",
            "RMSE",
            "sMAPE",
        ])

    work = predictions.copy()
    work["hour"] = work.index.hour

    rows: List[Dict[str, Any]] = []
    for hour, grp in work.groupby("hour"):
        y_true = grp["actual_energy"].values
        y_pred = grp["pred_energy"].values

        rows.append({
            "hour": int(hour),
            "n": int(len(grp)),
            "residual_mean": float(grp["residual"].mean()),
            "residual_std": float(grp["residual"].std()) if len(grp) > 1 else 0.0,
            "MAE": mae(y_true, y_pred),
            "RMSE": rmse(y_true, y_pred),
            "sMAPE": smape(y_true, y_pred),
        })

    return pd.DataFrame(rows).sort_values("hour").reset_index(drop=True)


def build_dayofweek_error_table(predictions: pd.DataFrame) -> pd.DataFrame:
    """
    Summarize forecast error by day of week.
    Monday=0 ... Sunday=6
    """
    if predictions.empty:
        return pd.DataFrame(columns=[
            "day_of_week",
            "n",
            "residual_mean",
            "residual_std",
            "MAE",
            "RMSE",
            "sMAPE",
        ])

    work = predictions.copy()
    work["day_of_week"] = work.index.dayofweek

    rows: List[Dict[str, Any]] = []
    for day_of_week, grp in work.groupby("day_of_week"):
        y_true = grp["actual_energy"].values
        y_pred = grp["pred_energy"].values

        rows.append({
            "day_of_week": int(day_of_week),
            "n": int(len(grp)),
            "residual_mean": float(grp["residual"].mean()),
            "residual_std": float(grp["residual"].std()) if len(grp) > 1 else 0.0,
            "MAE": mae(y_true, y_pred),
            "RMSE": rmse(y_true, y_pred),
            "sMAPE": smape(y_true, y_pred),
        })

    return pd.DataFrame(rows).sort_values("day_of_week").reset_index(drop=True)


def build_weekend_error_table(predictions: pd.DataFrame) -> pd.DataFrame:
    """
    Summarize forecast error for weekday vs weekend.
    is_weekend: 0=weekday, 1=weekend
    """
    if predictions.empty:
        return pd.DataFrame(columns=[
            "is_weekend",
            "n",
            "residual_mean",
            "residual_std",
            "MAE",
            "RMSE",
            "sMAPE",
        ])

    work = predictions.copy()
    work["is_weekend"] = (work.index.dayofweek >= 5).astype(int)

    rows: List[Dict[str, Any]] = []
    for is_weekend, grp in work.groupby("is_weekend"):
        y_true = grp["actual_energy"].values
        y_pred = grp["pred_energy"].values

        rows.append({
            "is_weekend": int(is_weekend),
            "n": int(len(grp)),
            "residual_mean": float(grp["residual"].mean()),
            "residual_std": float(grp["residual"].std()) if len(grp) > 1 else 0.0,
            "MAE": mae(y_true, y_pred),
            "RMSE": rmse(y_true, y_pred),
            "sMAPE": smape(y_true, y_pred),
        })

    return pd.DataFrame(rows).sort_values("is_weekend").reset_index(drop=True)


def build_peak_vs_nonpeak_metrics(predictions: pd.DataFrame) -> Dict[str, Any]:
    """
    Compare performance on peak vs non-peak actual demand hours.
    Peak hours are defined using the 90th percentile of actual energy.
    """
    if predictions.empty:
        return {
            "peak_threshold_actual_energy": None,
            "groups": {},
        }

    work = predictions.copy()
    threshold = float(work["actual_energy"].quantile(0.90))
    work["is_peak"] = (work["actual_energy"] >= threshold).astype(int)

    groups: Dict[str, Any] = {}
    for is_peak, grp in work.groupby("is_peak"):
        label = "peak" if int(is_peak) == 1 else "non_peak"
        y_true = grp["actual_energy"].values
        y_pred = grp["pred_energy"].values

        groups[label] = {
            "n": int(len(grp)),
            "actual_energy_mean": float(grp["actual_energy"].mean()),
            "pred_energy_mean": float(grp["pred_energy"].mean()),
            "residual_mean": float(grp["residual"].mean()),
            "MAE": mae(y_true, y_pred),
            "RMSE": rmse(y_true, y_pred),
            "sMAPE": smape(y_true, y_pred),
        }

    return {
        "peak_threshold_actual_energy": threshold,
        "groups": groups,
    }


def build_zero_vs_nonzero_metrics(predictions: pd.DataFrame) -> Dict[str, Any]:
    """
    Compare performance on zero-consumption vs non-zero-consumption hours.
    """
    if predictions.empty:
        return {"groups": {}}

    work = predictions.copy()
    work["is_zero"] = (work["actual_energy"] == 0).astype(int)

    groups: Dict[str, Any] = {}
    for is_zero, grp in work.groupby("is_zero"):
        label = "zero_actual" if int(is_zero) == 1 else "nonzero_actual"
        y_true = grp["actual_energy"].values
        y_pred = grp["pred_energy"].values

        groups[label] = {
            "n": int(len(grp)),
            "actual_energy_mean": float(grp["actual_energy"].mean()),
            "pred_energy_mean": float(grp["pred_energy"].mean()),
            "residual_mean": float(grp["residual"].mean()),
            "MAE": mae(y_true, y_pred),
            "RMSE": rmse(y_true, y_pred),
            "sMAPE": smape(y_true, y_pred),
        }

    return {"groups": groups}


def build_residual_vs_weather_table(
    test_df: pd.DataFrame,
    predictions: pd.DataFrame,
) -> Optional[pd.DataFrame]:
    """
    Join residuals with available weather variables for later plotting/inspection.
    """
    weather_cols = ["temperature", "humidity", "rainfall"]
    available_weather = [col for col in weather_cols if col in test_df.columns]

    if not available_weather:
        return None

    tmp = test_df[available_weather].copy()
    tmp = tmp.join(
        predictions[[
            "actual_energy",
            "pred_energy_raw",
            "pred_energy",
            "residual_raw",
            "residual",
            "clip_delta",
            "was_clipped",
        ]],
        how="inner",
    )

    return tmp.reset_index().rename(columns={"timestamp": "ts"})


def build_residual_feature_table(
    df_full: pd.DataFrame,
    predictions: pd.DataFrame,
) -> Optional[pd.DataFrame]:
    """
    Join residuals with selected diagnostic features already present in the dataset.
    """
    feature_cols = [
        "lag_24",
        "lag_168",
        "rolling_mean_24",
        "rolling_mean_168",
        "is_weekend",
    ]
    available_cols = [col for col in feature_cols if col in df_full.columns]

    if not available_cols:
        return None

    tmp = df_full[available_cols].copy()
    tmp = tmp.join(
        predictions[[
            "actual_energy",
            "pred_energy",
            "residual",
        ]],
        how="inner",
    )

    return tmp.reset_index().rename(columns={"timestamp": "ts"})

# =============================================================================
# Rolling-origin evaluation core
# =============================================================================

def rolling_origin_eval(
    df_full: pd.DataFrame,
    test_df: pd.DataFrame,
    model_dir: Path,
    appliance: str,
    cfg: EvalConfig,
) -> Dict[str, Any]:
    """
    Run daily rolling-origin evaluation over the REAL TEST block.
    """
    manifest = load_split_manifest(model_dir)
    best_params = load_best_params(model_dir)
    base_res = load_best_model(model_dir)

    test_start = test_df.index.min()
    test_end = test_df.index.max()

    exog_cols = best_params.get("exog_columns", detect_exog_columns(df_full))
    exog_cols = [col for col in exog_cols if col in df_full.columns and col != "energy"]

    if exog_cols:
        log(f"Exog columns used: {len(exog_cols)}")
    else:
        log("Exog columns used: 0")

    raw_pred = pd.Series(index=test_df.index, dtype=float)
    clipped_pred = pd.Series(index=test_df.index, dtype=float)

    if len(test_df) < cfg.horizon:
        raise RuntimeError(f"Test window too short for horizon={cfg.horizon}. n={len(test_df)}")

    # Use only midnight origins so each forecast covers one full next-day path.
    origins = [ts for ts in test_df.index if ts.hour == 0]

    # Keep only origins whose full horizon stays inside the REAL TEST window.
    origins = [
        ts for ts in origins
        if (ts + pd.Timedelta(hours=cfg.horizon - 1)) <= test_df.index.max()
    ]

    n_origins = len(origins)

    log(f"REAL TEST window: {test_start} -> {test_end} | test_n={len(test_df)} | origins_n={n_origins}")
    log(f"Rolling-origin: horizon={cfg.horizon} | refit_each_origin=True")

    current_res = base_res

    for i, origin in enumerate(origins, start=1):
        do_refit = True

        if i == 1 or i % cfg.progress_every == 0 or i == n_origins:
            log(
                f"[{i}/{n_origins}] origin={origin} | "
                f"horizon={cfg.horizon} | refit=True"
            )

        if do_refit:
            train_df = build_train_upto(df_full, origin)
            train_y = train_df["energy"].astype(float)

            if len(train_y) < cfg.min_train_rows:
                warn(f"Origin {origin}: train too small (n={len(train_y)}). Reusing previous model.")
            else:
                train_X = train_df[exog_cols] if exog_cols else None
                if train_X is not None:
                    train_X = ensure_numeric_exog(train_X)

                order = best_params["best"]["order"]
                seasonal = best_params["best"]["seasonal_order"]

                p, d, q = int(order["p"]), int(order["d"]), int(order["q"])
                P = int(seasonal["P"])
                D = int(seasonal["D"])
                Q = int(seasonal["Q"])
                s = int(seasonal["s"])

                model = SARIMAX(
                    endog=train_y,
                    exog=train_X,
                    order=(p, d, q),
                    seasonal_order=(P, D, Q, s),
                    enforce_stationarity=bool(best_params["fit_config"]["enforce_stationarity"]),
                    enforce_invertibility=bool(best_params["fit_config"]["enforce_invertibility"]),
                )

                t0 = time.perf_counter()
                current_res = model.fit(
                    disp=False,
                    maxiter=int(best_params["fit_config"]["maxiter"]),
                )
                elapsed = time.perf_counter() - t0

                log(
                    f"  -> refit done | train_n={len(train_y):,} | "
                    f"took={elapsed:.2f}s | "
                    f"converged={getattr(current_res, 'mle_retvals', {}).get('converged', True)}"
                )

        forecast_idx, X_forecast = build_forecast_inputs(df_full, origin, cfg.horizon, exog_cols)
        if X_forecast is not None and X_forecast.isna().any().any():
            warn(f"Missing exog values in forecast horizon @ origin={origin}. Skipping origin.")
            continue

        try:
            forecast_raw = current_res.get_forecast(
                steps=cfg.horizon,
                exog=X_forecast,
            ).predicted_mean
            forecast_raw.index = forecast_idx
            forecast_clipped = forecast_raw.clip(lower=0.0)
        except Exception as e:
            warn(f"Forecast failed @ origin={origin}: {e}")
            continue

        # Keep only timestamps still inside the real test scoring window.
        forecast_window = forecast_idx[(forecast_idx >= test_start) & (forecast_idx <= test_end)]

        for ts in forecast_window:
            raw_pred.loc[ts] = float(forecast_raw.loc[ts])
            clipped_pred.loc[ts] = float(forecast_clipped.loc[ts])

        if i == 1 or i % cfg.progress_every == 0 or i == n_origins:
            filled = int(clipped_pred.notna().sum())
            log(f"[{i}/{n_origins}] origin={origin} | filled_preds={filled}/{len(test_df)}")

    actual = test_df["energy"].astype(float)

    predictions = pd.DataFrame({
        "actual_energy": actual,
        "pred_energy_raw": raw_pred,
        "pred_energy": clipped_pred,
    }).dropna()

    predictions["residual_raw"] = predictions["actual_energy"] - predictions["pred_energy_raw"]
    predictions["residual"] = predictions["actual_energy"] - predictions["pred_energy"]
    predictions["clip_delta"] = predictions["pred_energy"] - predictions["pred_energy_raw"]
    predictions["was_clipped"] = (predictions["pred_energy_raw"] < 0).astype(int)
    daily_metrics = build_daily_metrics(predictions)

    hourly_error = build_hourly_error_table(predictions)
    dayofweek_error = build_dayofweek_error_table(predictions)
    weekend_error = build_weekend_error_table(predictions)
    peak_vs_nonpeak = build_peak_vs_nonpeak_metrics(predictions)
    zero_vs_nonzero = build_zero_vs_nonzero_metrics(predictions)

    residual_vs_weather = build_residual_vs_weather_table(
        test_df=test_df,
        predictions=predictions,
    )

    residual_feature_table = build_residual_feature_table(
        df_full=df_full,
        predictions=predictions,
    )

    y_true = predictions["actual_energy"].values
    y_hat = predictions["pred_energy"].values

    metrics = {
        "n_test_total": int(len(test_df)),
        "n_scored": int(len(predictions)),
        "horizon": int(cfg.horizon),
        "refit_each_origin": True,
        "MAE": mae(y_true, y_hat),
        "RMSE": rmse(y_true, y_hat),
        "NRMSE": nrmse(y_true, y_hat),
        "sMAPE": smape(y_true, y_hat),
        "MAPE_nonzero": mape_nonzero(y_true, y_hat),
        "R2": r2(y_true, y_hat),
        "n_forecast_days": int(n_origins),
        "n_raw_negative_predictions": int((predictions["pred_energy_raw"] < 0).sum()),
        "pct_raw_negative_predictions": float((predictions["pred_energy_raw"] < 0).mean() * 100.0),
        "note_mape_nonzero": "MAPE computed only on hours where actual_energy != 0",
        "note_scoring_prediction": "Primary evaluation metrics use clipped non-negative forecasts.",
        "note_raw_output": "Raw forecasts before clipping are saved separately for diagnostics.",
        "n_days_scored": int(daily_metrics["date"].nunique()) if not daily_metrics.empty else 0,
        "worst_day_by_rmse": (
            daily_metrics.sort_values("RMSE", ascending=False).iloc[0].to_dict()
            if not daily_metrics.empty else None
        ),
        "worst_day_by_mae": (
            daily_metrics.sort_values("MAE", ascending=False).iloc[0].to_dict()
            if not daily_metrics.empty else None
        ),
    }

    residual = predictions["residual"]
    resid_vals = residual.values

    residual_summary = {
        "mean": float(np.mean(resid_vals)) if len(resid_vals) else None,
        "std": float(np.std(resid_vals)) if len(resid_vals) else None,
        "min": float(np.min(resid_vals)) if len(resid_vals) else None,
        "max": float(np.max(resid_vals)) if len(resid_vals) else None,
        "median": float(np.median(resid_vals)) if len(resid_vals) else None,
        "n": int(len(resid_vals)),
    }

    if len(resid_vals) >= (cfg.ljungbox_lags + 5):
        lb = acorr_ljungbox(resid_vals, lags=[cfg.ljungbox_lags], return_df=True)
        ljung_box = {
            "lags": int(cfg.ljungbox_lags),
            "lb_stat": float(lb["lb_stat"].iloc[0]),
            "lb_pvalue": float(lb["lb_pvalue"].iloc[0]),
            "interpretation": "p>0.05 suggests residuals are not significantly autocorrelated",
        }
    else:
        ljung_box = {"note": "Too few residual samples for Ljung-Box at requested lags."}

    acf_values = None
    pacf_values = None

    if len(resid_vals) >= 20:
        max_acf = min(cfg.max_acf_lag, max(10, len(resid_vals) // 2))
        max_pacf = min(cfg.max_pacf_lag, max(10, len(resid_vals) // 2))
        acf_values = acf(resid_vals, nlags=max_acf, fft=True).tolist()
        pacf_values = pacf(resid_vals, nlags=max_pacf, method="ywmle").tolist()

    diagnostics = {
        "residual_summary": residual_summary,
        "ljung_box": ljung_box,
        "acf": {
            "max_lag": (len(acf_values) - 1) if acf_values else None,
            "values": acf_values,
        },
        "pacf": {
            "max_lag": (len(pacf_values) - 1) if pacf_values else None,
            "values": pacf_values,
        },
    }

    heat_df = predictions.copy()
    heat_df["date"] = heat_df.index.date
    heat_df["hour_of_day"] = heat_df.index.hour
    heatmap = heat_df.pivot_table(
        index="date",
        columns="hour_of_day",
        values="residual",
        aggfunc="mean",
    )

    return {
        "manifest": manifest,
        "metrics": metrics,
        "diagnostics": diagnostics,
        "predictions": predictions.sort_index(),
        "heatmap": heatmap,
        "daily_metrics": daily_metrics,
        "hourly_error": hourly_error,
        "dayofweek_error": dayofweek_error,
        "weekend_error": weekend_error,
        "peak_vs_nonpeak": peak_vs_nonpeak,
        "zero_vs_nonzero": zero_vs_nonzero,
        "residual_vs_weather": residual_vs_weather,
        "residual_feature_table": residual_feature_table,
    }


# =============================================================================
# CLI
# =============================================================================

def build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Rolling-Origin Evaluation (SARIMAX)"
    )
    parser.add_argument(
        "--horizon",
        type=int,
        default=24,
        help="Forecast horizon in hours",
    )
    return parser


# =============================================================================
# Main
# =============================================================================

def main() -> None:
    args = build_argparser().parse_args()

    cfg = EvalConfig(
        horizon=int(args.horizon),
    )

    log("==============================================")
    log("Rolling-Origin Evaluation (24h horizon)")
    log(f"Input dir   : {DEFAULT_INPUT_DIR}")
    log(f"Models root : {DEFAULT_MODELS_ROOT}")
    log(f"EvalConfig  : {asdict(cfg)}")
    log("==============================================")

    if not DEFAULT_INPUT_DIR.exists():
        raise FileNotFoundError(f"DEFAULT_INPUT_DIR not found: {DEFAULT_INPUT_DIR}")
    if not DEFAULT_MODELS_ROOT.exists():
        raise FileNotFoundError(f"DEFAULT_MODELS_ROOT not found: {DEFAULT_MODELS_ROOT}")

    csv_paths = sorted(DEFAULT_INPUT_DIR.glob(DEFAULT_GLOB))
    if not csv_paths:
        raise FileNotFoundError(f"No CSV files found in {DEFAULT_INPUT_DIR} with pattern {DEFAULT_GLOB}")

    summary: Dict[str, Any] = {
        "timestamp": datetime.now().isoformat(),
        "eval_config": asdict(cfg),
        "input_dir": str(DEFAULT_INPUT_DIR),
        "models_root": str(DEFAULT_MODELS_ROOT),
        "ok": 0,
        "failed": 0,
        "results": [],
        "failures": [],
    }

    t_all = time.perf_counter()

    for idx, csv_path in enumerate(csv_paths, start=1):
        appliance = csv_path.stem
        model_dir = DEFAULT_MODELS_ROOT / appliance

        if not model_dir.exists():
            warn(f"[{idx}/{len(csv_paths)}] Skip (no model dir): {appliance}")
            continue

        log(f"[{idx}/{len(csv_paths)}] Evaluating: {appliance}")

        try:
            df_full = load_full_dataset(csv_path)

            best_params = load_best_params(model_dir)
            exog_cols = best_params.get("exog_columns", detect_exog_columns(df_full))
            exog_cols = [col for col in exog_cols if col in df_full.columns and col != "energy"]

            df_full_clean = clean_for_model(df_full, exog_cols)

            manifest = load_split_manifest(model_dir)
            test_df, _, _ = slice_real_test(df_full_clean, manifest)

            out_dir = get_evaluation_output_dir(model_dir)

            result = rolling_origin_eval(
                df_full=df_full_clean,
                test_df=test_df,
                model_dir=model_dir,
                appliance=appliance,
                cfg=cfg,
            )

            pred_path = out_dir / "eval_predictions.csv"
            pred_raw_path = out_dir / "eval_predictions_raw.csv"
            metrics_path = out_dir / "eval_metrics.json"
            diagnostics_path = out_dir / "eval_residual_diagnostics.json"
            heatmap_path = out_dir / "eval_residual_heatmap.csv"
            daily_metrics_path = out_dir / "eval_daily_metrics.csv"
            hourly_error_path = out_dir / "eval_hourly_error.csv"
            dayofweek_error_path = out_dir / "eval_dayofweek_error.csv"
            weekend_error_path = out_dir / "eval_weekend_error.csv"
            peak_vs_nonpeak_path = out_dir / "eval_peak_vs_nonpeak.json"
            zero_vs_nonzero_path = out_dir / "eval_zero_vs_nonzero.json"
            residual_vs_weather_path = out_dir / "eval_residual_vs_weather.csv"
            residual_feature_table_path = out_dir / "eval_residual_feature_table.csv"

            log(f"Saving daily metrics: {daily_metrics_path}")
            result["daily_metrics"].to_csv(daily_metrics_path, index=False)

            log(f"Saving hourly error table: {hourly_error_path}")
            result["hourly_error"].to_csv(hourly_error_path, index=False)

            log(f"Saving day-of-week error table: {dayofweek_error_path}")
            result["dayofweek_error"].to_csv(dayofweek_error_path, index=False)

            log(f"Saving weekend error table: {weekend_error_path}")
            result["weekend_error"].to_csv(weekend_error_path, index=False)

            log(f"Saving peak vs non-peak metrics: {peak_vs_nonpeak_path}")
            peak_vs_nonpeak_path.write_text(
                json.dumps(result["peak_vs_nonpeak"], indent=2),
                encoding="utf-8",
            )

            log(f"Saving zero vs non-zero metrics: {zero_vs_nonzero_path}")
            zero_vs_nonzero_path.write_text(
                json.dumps(result["zero_vs_nonzero"], indent=2),
                encoding="utf-8",
            )

            if result["residual_vs_weather"] is not None:
                log(f"Saving residual vs weather table: {residual_vs_weather_path}")
                result["residual_vs_weather"].to_csv(residual_vs_weather_path, index=False)

            if result["residual_feature_table"] is not None:
                log(f"Saving residual feature table: {residual_feature_table_path}")
                result["residual_feature_table"].to_csv(residual_feature_table_path, index=False)
                
            log(f"Saving scored predictions: {pred_path}")
            scored_cols = [
                "actual_energy",
                "pred_energy",
                "residual",
                "was_clipped",
            ]
            (
                result["predictions"][scored_cols]
                .reset_index()
                .rename(columns={"index": "timestamp"})
                .to_csv(pred_path, index=False)
            )

            log(f"Saving raw predictions: {pred_raw_path}")
            raw_cols = [
                "actual_energy",
                "pred_energy_raw",
                "residual_raw",
                "pred_energy",
                "residual",
                "clip_delta",
                "was_clipped",
            ]
            (
                result["predictions"][raw_cols]
                .reset_index()
                .rename(columns={"index": "timestamp"})
                .to_csv(pred_raw_path, index=False)
            )

            log(f"Saving metrics: {metrics_path}")
            metrics_path.write_text(json.dumps(result["metrics"], indent=2), encoding="utf-8")

            log(f"Saving residual diagnostics: {diagnostics_path}")
            diagnostics_path.write_text(json.dumps(result["diagnostics"], indent=2), encoding="utf-8")

            log(f"Saving residual heatmap table: {heatmap_path}")
            result["heatmap"].to_csv(heatmap_path)

            artifacts = {
                "eval_predictions_csv": str(pred_path),
                "eval_predictions_raw_csv": str(pred_raw_path),
                "eval_metrics_json": str(metrics_path),
                "eval_residual_diagnostics_json": str(diagnostics_path),
                "eval_residual_heatmap_csv": str(heatmap_path),
                "eval_daily_metrics_csv": str(daily_metrics_path),
                "eval_hourly_error_csv": str(hourly_error_path),
                "eval_dayofweek_error_csv": str(dayofweek_error_path),
                "eval_weekend_error_csv": str(weekend_error_path),
                "eval_peak_vs_nonpeak_json": str(peak_vs_nonpeak_path),
                "eval_zero_vs_nonzero_json": str(zero_vs_nonzero_path),
            }

            if result["residual_vs_weather"] is not None:
                artifacts["eval_residual_vs_weather_csv"] = str(residual_vs_weather_path)

            if result["residual_feature_table"] is not None:
                artifacts["eval_residual_feature_table_csv"] = str(residual_feature_table_path)
                
            summary["results"].append({
                "appliance": appliance,
                "status": "ok",
                "n_test_total": int(result["metrics"]["n_test_total"]),
                "n_scored": int(result["metrics"]["n_scored"]),
                "metrics": result["metrics"],
                "artifacts": artifacts,
            })
            summary["ok"] += 1

            log(
                f"[{idx}/{len(csv_paths)}] OK {appliance} | "
                f"scored={result['metrics']['n_scored']} | "
                f"MAE={result['metrics']['MAE']:.6f}"
            )

        except Exception as e:
            tb = traceback.format_exc()
            err(f"[{idx}/{len(csv_paths)}] FAILED {appliance}: {e}")
            err(tb)

            summary["failed"] += 1
            summary["failures"].append({
                "appliance": appliance,
                "input": str(csv_path),
                "error": str(e),
                "traceback": tb,
            })

    summary_path = DEFAULT_MODELS_ROOT / "_eval_summary.json"

    log(f"Writing eval summary: {summary_path}")
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    log("==============================================")
    log(f"[DONE] Model Evaluation complete | elapsed={time.perf_counter() - t_all:.2f}s")
    log(f"OK={summary['ok']} | FAILED={summary['failed']}")
    log(f"Summary: {summary_path}")
    log("==============================================")


if __name__ == "__main__":
    main()