#!/usr/bin/env python3
"""
Stage 3.5.3 — Rolling-Origin Evaluation (24h horizon)

RUN (recommended daily refit; fast):
  python backend/scripts/stage35_3_rolling_origin_eval.py

RUN (full refit every step; slow):
  python backend/scripts/stage35_3_rolling_origin_eval.py --refit_every 1

What it does (per appliance):
  - Loads Stage 3.5.2 artifacts:
      model/sarimax/<appliance_stem>/
        best_model.pkl
        best_params.json
        split_manifest.json
  - Loads full model-ready dataset CSV
  - Isolates REAL TEST ONLY based on split_manifest["ranges"]["real_test"]
  - Rolling-origin evaluation with horizon=24 hours:
      * At each origin, (optionally) refit model every N steps (refit_every)
      * Forecast next 24 hours
      * Collect the TRUE 24h-ahead forecast: prediction for (origin + horizon - 1)
  - Produces:
      model/sarimax/<appliance_stem>/evaluation/
        eval_predictions.csv
        eval_predictions_kwh.csv
        eval_metrics.json
        eval_residual_diagnostics.json
        eval_residual_heatmap.csv
        eval_residual_vs_temperature.csv   (if temperature exists)
      model/sarimax/evaluation/_eval_summary.json

Notes:
  - This script is for EVALUATION ONLY.
  - It does NOT generate a deployment/operational next-24h forecast.
  - Target is ENERGY per hour (hourly kWh, as in your dataset).
  - Energy cannot be negative, so forecasts are clipped at 0.
"""

from __future__ import annotations

import argparse
import json
import time
import traceback
import warnings
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

import numpy as np
import pandas as pd

from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.stattools import acf, pacf
from statsmodels.tsa.statespace.sarimax import SARIMAXResults

warnings.filterwarnings("ignore")


# =============================================================================
# Defaults
# =============================================================================

DEFAULT_INPUT_DIR = Path("data")
DEFAULT_MODELS_ROOT = Path("model/stageB/sarimax")
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
    refit_every: int = 24
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
    mu = float(np.mean(y_true))
    return float(rmse(y_true, y_pred) / max(mu, eps))


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
    log(f"Loading full model-ready dataset: {csv_path}")
    df = pd.read_csv(csv_path)

    if "timestamp" not in df.columns or "energy" not in df.columns:
        raise ValueError(f"{csv_path.name}: must contain 'timestamp' and 'energy'")

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    bad = int(df["timestamp"].isna().sum())
    if bad:
        raise ValueError(f"{csv_path.name}: {bad} invalid timestamps")

    df = df.sort_values("timestamp").set_index("timestamp")
    log(f"Loaded {csv_path.name}: rows={len(df):,} | range={df.index.min()} -> {df.index.max()}")
    return df


def load_split_manifest(appliance_dir: Path) -> Dict[str, Any]:
    p = appliance_dir / "split_manifest.json"
    if not p.exists():
        raise FileNotFoundError(f"Missing split_manifest.json: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


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
        if out[c].dtype == "object":
            out[c] = pd.to_numeric(out[c], errors="coerce")
    return out


def slice_real_test(df: pd.DataFrame, manifest: Dict[str, Any]) -> Tuple[pd.DataFrame, pd.Timestamp, pd.Timestamp]:
    rt = manifest.get("ranges", {}).get("real_test")
    if not rt or not isinstance(rt, list) or len(rt) != 2:
        raise ValueError("split_manifest missing ranges.real_test")

    start = pd.to_datetime(rt[0])
    end = pd.to_datetime(rt[1])

    test = df.loc[(df.index >= start) & (df.index <= end)].copy()
    if len(test) == 0:
        raise RuntimeError(f"REAL TEST slice empty for range {start} -> {end}")

    return test, start, end


def build_train_upto(df: pd.DataFrame, origin: pd.Timestamp) -> pd.DataFrame:
    return df.loc[df.index < origin].copy()


def build_forecast_inputs(
    df_full: pd.DataFrame,
    origin: pd.Timestamp,
    horizon: int,
    exog_cols: List[str],
) -> Tuple[pd.DatetimeIndex, Optional[pd.DataFrame]]:
    idx = pd.date_range(origin, periods=horizon, freq="h")
    if exog_cols:
        Xf = df_full.reindex(idx)[exog_cols]
        Xf = ensure_numeric_exog(Xf)
        return idx, Xf
    return idx, None


def clean_for_model(df: pd.DataFrame, exog_cols: List[str]) -> pd.DataFrame:
    cols = ["energy"] + exog_cols
    cols = [c for c in cols if c in df.columns]
    return df[cols].dropna().copy()


# =============================================================================
# Rolling-origin evaluation core
# =============================================================================

def rolling_origin_eval(
    df_full: pd.DataFrame,
    test_df: pd.DataFrame,
    model_dir: Path,
    appliance: str,
    cfg: EvalConfig
) -> Dict[str, Any]:
    manifest = load_split_manifest(model_dir)
    best_params = load_best_params(model_dir)
    base_res = load_best_model(model_dir)

    test_start = test_df.index.min()
    test_end = test_df.index.max()

    exog_cols = best_params.get("exog_columns", detect_exog_columns(df_full))
    if exog_cols:
        for c in exog_cols:
            if c not in df_full.columns:
                warn(f"Exog column from params not found in dataset: {c}")

    exog_cols = [c for c in exog_cols if c in df_full.columns and c != "energy"]
    log(f"Exog columns used: {len(exog_cols)}")

    pred = pd.Series(index=test_df.index, dtype=float)

    if len(test_df) < cfg.horizon:
        raise RuntimeError(f"Test window too short for horizon={cfg.horizon}. n={len(test_df)}")

    origins = list(test_df.index[: -(cfg.horizon - 1)])
    n_origins = len(origins)

    log(f"REAL TEST window: {test_start} -> {test_end} | test_n={len(test_df)} | origins_n={n_origins}")
    log(f"Rolling-origin: horizon={cfg.horizon} | refit_every={cfg.refit_every}")

    current_res = base_res
    last_refit_origin: Optional[pd.Timestamp] = None

    log(f"Rolling-origin evaluation starting: {n_origins} origins")

    for i, origin in enumerate(origins, start=1):
        do_refit = (last_refit_origin is None) or ((i - 1) % cfg.refit_every == 0)

        if i == 1 or i % cfg.progress_every == 0 or i == n_origins:
            log(
                f"[{i}/{n_origins}] origin={origin} "
                f"| horizon={cfg.horizon} "
                f"| refit_every={cfg.refit_every} "
                f"| refit={do_refit}"
            )

        if do_refit:
            train_df = build_train_upto(df_full, origin)
            train_y = train_df["energy"].astype(float)

            if len(train_y) < cfg.min_train_rows:
                warn(f"Origin {origin}: train too small (n={len(train_y)}). Skipping refit; using previous model.")
            else:
                log(f"  -> refitting model (train_end={origin - pd.Timedelta(hours=1)})")

                train_X = train_df[exog_cols] if exog_cols else None
                if train_X is not None:
                    train_X = ensure_numeric_exog(train_X)

                order = best_params["best"]["order"]
                seas = best_params["best"]["seasonal_order"]

                p, d, q = int(order["p"]), int(order["d"]), int(order["q"])
                P, D, Q, s = int(seas["P"]), int(seas["D"]), int(seas["Q"]), int(seas["s"])

                from statsmodels.tsa.statespace.sarimax import SARIMAX
                m = SARIMAX(
                    endog=train_y,
                    exog=train_X,
                    order=(p, d, q),
                    seasonal_order=(P, D, Q, s),
                    enforce_stationarity=bool(best_params["fit_config"]["enforce_stationarity"]),
                    enforce_invertibility=bool(best_params["fit_config"]["enforce_invertibility"]),
                )

                t0 = time.perf_counter()
                current_res = m.fit(disp=False, maxiter=int(best_params["fit_config"]["maxiter"]))
                dt = time.perf_counter() - t0
                last_refit_origin = origin

                log(
                    f"Refit @ origin={origin} | train_n={len(train_y):,} | took={dt:.2f}s "
                    f"| converged={getattr(current_res, 'mle_retvals', {}).get('converged', True)}"
                )
        else:
            if i == 1 or i % cfg.progress_every == 0 or i == n_origins:
                log("  -> reusing previously fitted model")

        f_idx, Xf = build_forecast_inputs(df_full, origin, cfg.horizon, exog_cols)
        if Xf is not None and Xf.isna().any().any():
            warn(f"Missing exog values in forecast horizon @ origin={origin}. Skipping origin.")
            continue

        try:
            fc = current_res.get_forecast(steps=cfg.horizon, exog=Xf).predicted_mean
            fc.index = f_idx
            fc = fc.clip(lower=0.0)
        except Exception as e:
            warn(f"Forecast failed @ origin={origin}: {e}")
            continue

        target_ts = origin + pd.Timedelta(hours=cfg.horizon - 1)
        if test_start <= target_ts <= test_end:
            pred.loc[target_ts] = float(fc.loc[target_ts])

        if i == 1 or i % cfg.progress_every == 0 or i == n_origins:
            filled = int(pred.notna().sum())
            log(f"[{i}/{n_origins}] origin={origin} | filled_preds={filled}/{len(test_df)}")

    pred = pred.clip(lower=0.0)

    actual = test_df["energy"].astype(float)
    aligned = pd.DataFrame({"actual_energy": actual, "pred_energy": pred}).dropna()
    residual = aligned["actual_energy"] - aligned["pred_energy"]
    aligned["residual"] = residual

    y_true = aligned["actual_energy"].values
    y_hat = aligned["pred_energy"].values

    metrics = {
        "n_test_total": int(len(test_df)),
        "n_scored": int(len(aligned)),
        "horizon": int(cfg.horizon),
        "refit_every": int(cfg.refit_every),
        "MAE": mae(y_true, y_hat),
        "RMSE": rmse(y_true, y_hat),
        "NRMSE": nrmse(y_true, y_hat),
        "sMAPE": smape(y_true, y_hat),
        "MAPE_nonzero": mape_nonzero(y_true, y_hat),
        "R2": r2(y_true, y_hat),
        "note_mape_nonzero": "MAPE computed only on hours where actual_energy != 0",
        "note_clip": "Predictions were clipped at 0 to enforce non-negative energy.",
    }

    resid_vals = residual.values
    resid_summary = {
        "mean": float(np.mean(resid_vals)) if len(resid_vals) else None,
        "std": float(np.std(resid_vals)) if len(resid_vals) else None,
        "min": float(np.min(resid_vals)) if len(resid_vals) else None,
        "max": float(np.max(resid_vals)) if len(resid_vals) else None,
        "median": float(np.median(resid_vals)) if len(resid_vals) else None,
        "n": int(len(resid_vals)),
    }

    if len(resid_vals) >= (cfg.ljungbox_lags + 5):
        lb = acorr_ljungbox(resid_vals, lags=[cfg.ljungbox_lags], return_df=True)
        lj = {
            "lags": int(cfg.ljungbox_lags),
            "lb_stat": float(lb["lb_stat"].iloc[0]),
            "lb_pvalue": float(lb["lb_pvalue"].iloc[0]),
            "interpretation": "p>0.05 suggests residuals are not significantly autocorrelated",
        }
    else:
        lj = {"note": "Too few residual samples for Ljung-Box at requested lags."}

    acf_arr = None
    pacf_arr = None
    if len(resid_vals) >= 20:
        max_acf = min(cfg.max_acf_lag, max(10, len(resid_vals) // 2))
        max_pacf = min(cfg.max_pacf_lag, max(10, len(resid_vals) // 2))
        acf_arr = acf(resid_vals, nlags=max_acf, fft=True).tolist()
        pacf_arr = pacf(resid_vals, nlags=max_pacf, method="ywmle").tolist()

    diagnostics = {
        "residual_summary": resid_summary,
        "ljung_box": lj,
        "acf": {"max_lag": (len(acf_arr) - 1) if acf_arr else None, "values": acf_arr},
        "pacf": {"max_lag": (len(pacf_arr) - 1) if pacf_arr else None, "values": pacf_arr},
    }

    heat_df = aligned.copy()
    heat_df["date"] = heat_df.index.date
    heat_df["hour_of_day"] = heat_df.index.hour
    heat = heat_df.pivot_table(index="date", columns="hour_of_day", values="residual", aggfunc="mean")

    rvst = None
    if "temperature" in test_df.columns:
        tmp = test_df[["temperature"]].copy()
        tmp = tmp.join(aligned[["residual"]], how="inner")
        rvst = tmp.reset_index()[["timestamp", "temperature", "residual"]].rename(columns={"timestamp": "ts"})

    aligned_sorted = aligned.sort_index().copy()

    return {
        "manifest": manifest,
        "metrics": metrics,
        "diagnostics": diagnostics,
        "predictions": aligned_sorted,
        "heatmap": heat,
        "residual_vs_temperature": rvst,
    }


# =============================================================================
# Main
# =============================================================================

def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Stage 3.5.3 Rolling-Origin Evaluation (SARIMAX)")
    p.add_argument("--refit_every", type=int, default=24, help="Refit frequency in steps (24=daily, 168=weekly, 1=every step)")
    p.add_argument("--horizon", type=int, default=24, help="Forecast horizon in hours")
    return p


def main() -> None:
    args = build_argparser().parse_args()

    cfg = EvalConfig(
        horizon=int(args.horizon),
        refit_every=int(args.refit_every),
    )

    log("==============================================")
    log("Stage 3.5.3 — Rolling-Origin Evaluation (24h horizon)")
    log(f"Input dir   : {DEFAULT_INPUT_DIR}")
    log(f"Models root : {DEFAULT_MODELS_ROOT}")
    log(f"EvalConfig  : {asdict(cfg)}")
    log("==============================================")

    if not DEFAULT_INPUT_DIR.exists():
        raise FileNotFoundError(f"DEFAULT_INPUT_DIR not found: {DEFAULT_INPUT_DIR}")
    if not DEFAULT_MODELS_ROOT.exists():
        raise FileNotFoundError(f"DEFAULT_MODELS_ROOT not found: {DEFAULT_MODELS_ROOT}")

    csvs = sorted(DEFAULT_INPUT_DIR.glob(DEFAULT_GLOB))
    if not csvs:
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

    for idx, csv_path in enumerate(csvs, start=1):
        appliance = csv_path.stem
        model_dir = DEFAULT_MODELS_ROOT / appliance

        if not model_dir.exists():
            warn(f"[{idx}/{len(csvs)}] Skip (no model dir): {appliance}")
            continue

        log(f"[{idx}/{len(csvs)}] Evaluating: {appliance}")
        try:
            df_full = load_full_dataset(csv_path)

            best_params = load_best_params(model_dir)
            exog_cols = best_params.get("exog_columns", detect_exog_columns(df_full))
            exog_cols = [c for c in exog_cols if c in df_full.columns and c != "energy"]

            df_full_clean = clean_for_model(df_full, exog_cols)

            manifest = load_split_manifest(model_dir)
            test_df, _, _ = slice_real_test(df_full_clean, manifest)

            out_dir = model_dir / "evaluation"
            out_dir.mkdir(parents=True, exist_ok=True)

            result = rolling_origin_eval(df_full_clean, test_df, model_dir, appliance, cfg)

            pred_path = out_dir / "eval_predictions.csv"
            pred_extra_path = out_dir / "eval_predictions_kwh.csv"
            metrics_path = out_dir / "eval_metrics.json"
            diag_path = out_dir / "eval_residual_diagnostics.json"
            heat_path = out_dir / "eval_residual_heatmap.csv"

            log(f"Saving predictions: {pred_path}")
            base_cols = ["actual_energy", "pred_energy", "residual"]
            result["predictions"][base_cols].reset_index().rename(columns={"index": "timestamp"}).to_csv(pred_path, index=False)

            log(f"Saving predictions (extra): {pred_extra_path}")
            result["predictions"].reset_index().rename(columns={"index": "timestamp"}).to_csv(pred_extra_path, index=False)

            log(f"Saving metrics: {metrics_path}")
            metrics_path.write_text(json.dumps(result["metrics"], indent=2), encoding="utf-8")

            log(f"Saving residual diagnostics: {diag_path}")
            diag_path.write_text(json.dumps(result["diagnostics"], indent=2), encoding="utf-8")

            log(f"Saving residual heatmap table: {heat_path}")
            result["heatmap"].to_csv(heat_path)

            if result["residual_vs_temperature"] is not None:
                rvst_path = out_dir / "eval_residual_vs_temperature.csv"
                log(f"Saving residual vs temperature: {rvst_path}")
                result["residual_vs_temperature"].to_csv(rvst_path, index=False)

            summary["results"].append({
                "appliance": appliance,
                "status": "ok",
                "n_test_total": int(result["metrics"]["n_test_total"]),
                "n_scored": int(result["metrics"]["n_scored"]),
                "metrics": result["metrics"],
                "artifacts": {
                    "eval_predictions_csv": str(pred_path),
                    "eval_predictions_extra_csv": str(pred_extra_path),
                    "eval_metrics_json": str(metrics_path),
                    "eval_residual_diagnostics_json": str(diag_path),
                    "eval_residual_heatmap_csv": str(heat_path),
                }
            })
            summary["ok"] += 1

            log(f"[{idx}/{len(csvs)}] OK {appliance} | scored={result['metrics']['n_scored']} | MAE={result['metrics']['MAE']:.6f}")

        except Exception as e:
            tb = traceback.format_exc()
            err(f"[{idx}/{len(csvs)}] FAILED {appliance}: {e}")
            err(tb)
            summary["failed"] += 1
            summary["failures"].append({
                "appliance": appliance,
                "input": str(csv_path),
                "error": str(e),
                "traceback": tb
            })

    summary_dir = DEFAULT_MODELS_ROOT / "evaluation"
    summary_dir.mkdir(parents=True, exist_ok=True)
    summary_path = summary_dir / "_eval_summary.json"

    log(f"Writing eval summary: {summary_path}")
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    log("==============================================")
    log(f"[DONE] Stage 3.5.3 complete | elapsed={time.perf_counter() - t_all:.2f}s")
    log(f"OK={summary['ok']} | FAILED={summary['failed']}")
    log(f"Summary: {summary_path}")
    log("==============================================")


if __name__ == "__main__":
    main()