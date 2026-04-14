#!/usr/bin/env python3
"""
Stage 3.5.2 - SARIMAX Model Estimation and Selection

Summary:
This script fits SARIMAX models for each per-appliance model-ready CSV using a
bounded grid search over non-seasonal and seasonal AR/MA terms. It preserves the
hybrid train/test split design, performs expanding-window time-series cross-
validation within TRAIN only, and selects the best model primarily using the
chosen CV metric, with AIC/BIC used as tie-breakers.

It also supports checkpointing and resume per appliance so long searches can be
continued safely without losing progress.

Input flow:
data/
  -> <appliance_model_ready>.csv

model/
  -> sarimax/
     -> <appliance_csv_stem>/
        -> premodel/
           -> <appliance_csv_stem>_premodel_report.json

Processing flow:
per-appliance model-ready CSV
  -> load model-ready data
  -> load premodel diagnostics
  -> derive seasonal period and differencing candidates
  -> build target and exogenous variables
  -> coerce exogenous columns to numeric
  -> drop NA rows if configured
  -> apply hybrid split:
       synthetic + earlier real -> TRAIN
       later real -> TEST
  -> build expanding-window CV folds inside TRAIN
  -> run bounded SARIMAX grid search across:
       guided (d, D) candidates
       p, q, P, Q bounds
  -> fit each candidate on TRAIN
  -> evaluate each candidate using CV inside TRAIN
  -> select best candidate by CV, then AIC/BIC
  -> refit the best model on full TRAIN
  -> save final artifacts and batch summary

Output flow:
model/
  -> sarimax/
     -> <appliance_csv_stem>/
        -> model/
           -> best_model.pkl
           -> best_params.json
           -> coefficients.csv
           -> search_results.csv
           -> split_manifest.json
           -> checkpoint.json
           -> search_results.partial.csv
     -> _fit_summary.json
"""

from __future__ import annotations

import json
import time
import traceback
import warnings
from dataclasses import asdict, dataclass
from datetime import datetime
from itertools import product
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX

warnings.filterwarnings("ignore")


# =============================================================================
# Defaults
# =============================================================================

DEFAULT_INPUT_DIR = Path("data")
DEFAULT_OUT_ROOT = Path("model/sarimax")
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
class FitConfig:
    # Hybrid split controls
    synthetic_end: str = "2026-01-03 18:00:00"
    real_start: str = "2026-01-03 19:00:00"
    real_train_ratio: float = 0.70
    require_full_day_boundary: bool = True
    train_end_hour: int = 23

    # Seasonal period fallback if premodel report is missing it
    default_seasonal_period: int = 24

    # Bounded search space for p, q, P, Q
    max_p: int = 3
    max_q: int = 3
    max_P: int = 2
    max_Q: int = 2
    max_total_order: int = 10

    # Fit options
    enforce_stationarity: bool = True
    enforce_invertibility: bool = True
    maxiter: int = 150
    disp: bool = False

    # Data handling
    dropna: bool = True
    min_rows_required: int = 300

    # Time-series CV inside TRAIN only
    cv_enabled: bool = True
    cv_horizon: int = 24
    cv_n_folds: int = 3
    cv_min_train_rows: int = 300
    cv_metric: str = "RMSE"  # RMSE, MAE, sMAPE
    cv_progress_every: int = 10

    # Checkpoint / resume
    checkpoint_every_n_models: int = 1
    checkpoint_every_seconds: int = 600


CFG = FitConfig()

# =============================================================================
# Appliance-specific config overrides
# =============================================================================
# Tighter bounds for appliances whose short-dataset signals are prone to
# overfitting.  Refrigerator and electric fan get reduced complexity limits
# and adjusted CV strategy; aircon keeps the default (proven effective).

APPLIANCE_CONFIG_OVERRIDES: Dict[str, Dict[str, Any]] = {
    "refrigerator_model_ready": {
        # Compressor cycling has short memory; limit AR/MA complexity
        "max_p": 2,
        "max_q": 2,
        "max_P": 1,
        "max_Q": 1,
        "max_total_order": 6,
        # sMAPE is more robust than RMSE for spiky compressor data
        "cv_metric": "sMAPE",
        # More folds for better selection stability with limited data
        "cv_n_folds": 5,
        "cv_min_train_rows": 200,
    },
    "electric_fan_model_ready": {
        # Intermittent usage; moderate complexity is sufficient
        "max_p": 2,
        "max_q": 2,
        "max_P": 1,
        "max_Q": 1,
        "max_total_order": 6,
        # sMAPE handles zero-inflation better for intermittent loads
        "cv_metric": "sMAPE",
        "cv_n_folds": 5,
        "cv_min_train_rows": 200,
    },
    # aircon_model_ready: no overrides — defaults are effective
}


def get_appliance_config(appliance_stem: str, base_cfg: FitConfig) -> FitConfig:
    """Return FitConfig with appliance-specific overrides applied."""
    overrides = APPLIANCE_CONFIG_OVERRIDES.get(appliance_stem, {})
    if not overrides:
        return base_cfg

    from dataclasses import asdict as _asdict
    merged = _asdict(base_cfg)
    merged.update(overrides)
    return FitConfig(**merged)


# =============================================================================
# Metrics
# =============================================================================

def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(np.abs(y_true - y_pred)))


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def smape(y_true: np.ndarray, y_pred: np.ndarray, eps: float = 1e-9) -> float:
    denom = np.maximum(np.abs(y_true) + np.abs(y_pred), eps)
    return float(np.mean(2.0 * np.abs(y_pred - y_true) / denom) * 100.0)


def score_arrays(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    return {
        "RMSE": rmse(y_true, y_pred),
        "MAE": mae(y_true, y_pred),
        "sMAPE": smape(y_true, y_pred),
    }


# =============================================================================
# Path helpers
# =============================================================================

def get_appliance_root_dir(appliance: str) -> Path:
    out_dir = DEFAULT_OUT_ROOT / appliance
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def get_model_output_dir(appliance: str) -> Path:
    out_dir = get_appliance_root_dir(appliance) / "model"
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def get_premodel_report_path(appliance: str) -> Path:
    return DEFAULT_OUT_ROOT / appliance / "premodel" / f"{appliance}_premodel_report.json"


def get_batch_summary_path() -> Path:
    DEFAULT_OUT_ROOT.mkdir(parents=True, exist_ok=True)
    return DEFAULT_OUT_ROOT / "_fit_summary.json"


# =============================================================================
# IO helpers
# =============================================================================

def load_model_ready_csv(path: Path) -> pd.DataFrame:
    """
    Load one model-ready appliance CSV.
    """
    log(f"Loading model-ready CSV: {path}")
    df = pd.read_csv(path)

    if "timestamp" not in df.columns or "energy" not in df.columns:
        raise ValueError(f"{path.name}: must contain 'timestamp' and 'energy' columns")

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    bad_ts = int(df["timestamp"].isna().sum())
    if bad_ts > 0:
        raise ValueError(f"{path.name}: {bad_ts} invalid timestamps")

    df = df.sort_values("timestamp").set_index("timestamp")
    log(f"Loaded {path.name}: rows={len(df):,} | range={df.index.min()} -> {df.index.max()}")
    return df


def load_premodel_report(appliance: str) -> Dict[str, Any]:
    """
    Load the Stage 3.5.1 premodel report for one appliance.
    """
    report_path = get_premodel_report_path(appliance)
    if not report_path.exists():
        raise FileNotFoundError(f"Missing premodel report for {appliance}: {report_path}")

    log(f"Loading premodel report: {report_path}")
    return json.loads(report_path.read_text(encoding="utf-8"))


def ensure_numeric_exog(exog: pd.DataFrame) -> pd.DataFrame:
    """
    Coerce exogenous columns into numeric form for SARIMAX.
    """
    out = exog.copy()
    for col in out.columns:
        if out[col].dtype == "bool":
            out[col] = out[col].astype(int)
        if out[col].dtype == "object":
            out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def build_y_exog(df: pd.DataFrame) -> Tuple[pd.Series, Optional[pd.DataFrame], List[str]]:
    """
    Split the dataframe into target and exogenous inputs.
    """
    y = df["energy"].astype(float)
    exog_cols = [col for col in df.columns if col != "energy"]

    if not exog_cols:
        warn("No exogenous columns found. Model will fit without exog.")
        return y, None, []

    X = ensure_numeric_exog(df[exog_cols].copy())
    return y, X, exog_cols


# =============================================================================
# Premodel-derived search settings
# =============================================================================

def get_differencing_candidates(report: Dict[str, Any]) -> List[Dict[str, int]]:
    """
    Get guided differencing candidates from the premodel report.

    Falls back to the single rule-based suggestion if guided candidates
    are not present.
    """
    guided = report.get("guided_differencing_candidates", {})
    candidate_set = guided.get("candidate_set", [])

    if candidate_set:
        cleaned: List[Dict[str, int]] = []
        seen = set()

        for item in candidate_set:
            d = int(item["d"])
            D = int(item["D"])
            key = (d, D)
            if key in seen:
                continue
            seen.add(key)
            cleaned.append({"d": d, "D": D})

        if cleaned:
            return cleaned

    suggested = report.get("suggested_differencing", {})
    return [{
        "d": int(suggested.get("rule_based_d", 0)),
        "D": int(suggested.get("rule_based_D", 0)),
    }]


def get_seasonal_period(report: Dict[str, Any], cfg: FitConfig) -> int:
    """
    Get the seasonal period from premodel config if available.
    """
    return int(report.get("config", {}).get("seasonal_period", cfg.default_seasonal_period))


# =============================================================================
# Hybrid split
# =============================================================================

def hybrid_split(data: pd.DataFrame, cfg: FitConfig) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """
    Split the data into:
      synthetic = <= synthetic_end
      real      = >= real_start

    TRAIN = synthetic + earlier real portion
    TEST  = later real portion
    """
    syn_end = pd.to_datetime(cfg.synthetic_end)
    real_start = pd.to_datetime(cfg.real_start)

    if data.index.min() > syn_end:
        warn("Data starts after synthetic_end; synthetic block may be empty.")
    if data.index.max() < real_start:
        warn("Data ends before real_start; real block may be empty.")

    synthetic = data.loc[data.index <= syn_end].copy()
    real = data.loc[data.index >= real_start].copy().sort_index()

    if len(real) == 0:
        raise RuntimeError(
            f"Real block is empty using real_start={cfg.real_start}. "
            f"Check your timestamps and update FitConfig.real_start."
        )

    raw_cut = int(np.floor(len(real) * cfg.real_train_ratio))
    raw_cut = min(max(raw_cut, 1), len(real) - 1)
    raw_split_ts = pd.Timestamp(real.index[raw_cut])

    if cfg.require_full_day_boundary:
        candidates = real.loc[
            (real.index <= raw_split_ts) &
            (real.index.hour == cfg.train_end_hour)
        ]

        if len(candidates) == 0:
            raise RuntimeError(
                f"No timestamp at hour={cfg.train_end_hour}:00 found on or before raw split "
                f"timestamp {raw_split_ts} in real block."
            )

        train_end_ts = pd.Timestamp(candidates.index.max())
    else:
        train_end_ts = raw_split_ts

    test_start_ts = train_end_ts + pd.Timedelta(hours=1)

    real_train = real.loc[real.index <= train_end_ts].copy()
    real_test = real.loc[real.index >= test_start_ts].copy()

    train = pd.concat([synthetic, real_train], axis=0).sort_index()
    test = real_test.sort_index()

    if len(real_test) == 0:
        warn("TEST set is empty after full-day-boundary split.")

    manifest = {
        "synthetic_end": cfg.synthetic_end,
        "real_start": cfg.real_start,
        "real_train_ratio": cfg.real_train_ratio,
        "require_full_day_boundary": cfg.require_full_day_boundary,
        "train_end_hour": cfg.train_end_hour,
        "raw_split_ts": str(raw_split_ts),
        "train_end_ts": str(train_end_ts),
        "test_start_ts": str(test_start_ts),
        "counts": {
            "synthetic": int(len(synthetic)),
            "real_total": int(len(real)),
            "real_train": int(len(real_train)),
            "real_test": int(len(real_test)),
            "train_total": int(len(train)),
            "test_total": int(len(test)),
        },
        "ranges": {
            "synthetic": [str(synthetic.index.min()), str(synthetic.index.max())] if len(synthetic) else [None, None],
            "real": [str(real.index.min()), str(real.index.max())],
            "real_train": [str(real_train.index.min()), str(real_train.index.max())] if len(real_train) else [None, None],
            "real_test": [str(real_test.index.min()), str(real_test.index.max())] if len(real_test) else [None, None],
            "train": [str(train.index.min()), str(train.index.max())],
            "test": [str(test.index.min()), str(test.index.max())] if len(test) else [None, None],
        },
    }

    return train, test, manifest


# =============================================================================
# Search helpers
# =============================================================================

def iter_orders(
    cfg: FitConfig,
    d: int,
    D: int,
) -> List[Tuple[Tuple[int, int, int], Tuple[int, int, int, int]]]:
    """
    Build the bounded search space for one (d, D) pair.
    """
    combos = []

    for p, q, P, Q in product(
        range(cfg.max_p + 1),
        range(cfg.max_q + 1),
        range(cfg.max_P + 1),
        range(cfg.max_Q + 1),
    ):
        if (p + q + P + Q) > cfg.max_total_order:
            continue
        combos.append(((p, d, q), (P, D, Q, None)))  # seasonal period injected later

    return combos


def build_search_plan(
    cfg: FitConfig,
    differencing_candidates: List[Dict[str, int]],
    seasonal_period: int,
) -> List[Dict[str, Any]]:
    """
    Build the full search plan across all guided (d, D) candidates.
    """
    plan: List[Dict[str, Any]] = []

    for pair in differencing_candidates:
        d = int(pair["d"])
        D = int(pair["D"])

        for order, seasonal_template in iter_orders(cfg, d=d, D=D):
            seasonal_order = (
                seasonal_template[0],
                seasonal_template[1],
                seasonal_template[2],
                seasonal_period,
            )
            plan.append({
                "order": order,
                "seasonal_order": seasonal_order,
                "d": d,
                "D": D,
                "s": seasonal_period,
            })

    return plan


def fit_one_model(
    y_train: pd.Series,
    X_train: Optional[pd.DataFrame],
    order: Tuple[int, int, int],
    seasonal_order: Tuple[int, int, int, int],
    cfg: FitConfig,
) -> Dict[str, Any]:
    """
    Fit one SARIMAX candidate on the full TRAIN set.
    """
    t0 = time.perf_counter()
    record: Dict[str, Any] = {
        "p": order[0],
        "d": order[1],
        "q": order[2],
        "P": seasonal_order[0],
        "D": seasonal_order[1],
        "Q": seasonal_order[2],
        "s": seasonal_order[3],
        "aic": None,
        "bic": None,
        "converged": False,
        "fit_seconds": None,
        "error": None,
    }

    try:
        model = SARIMAX(
            endog=y_train,
            exog=X_train,
            order=order,
            seasonal_order=seasonal_order,
            enforce_stationarity=cfg.enforce_stationarity,
            enforce_invertibility=cfg.enforce_invertibility,
        )
        res = model.fit(disp=cfg.disp, maxiter=cfg.maxiter)

        record["aic"] = float(res.aic) if np.isfinite(res.aic) else None
        record["bic"] = float(res.bic) if np.isfinite(res.bic) else None
        record["converged"] = bool(getattr(res, "mle_retvals", {}).get("converged", True))
        record["fit_seconds"] = float(time.perf_counter() - t0)
        record["_result_obj"] = res
        return record

    except Exception as e:
        record["fit_seconds"] = float(time.perf_counter() - t0)
        record["error"] = str(e)
        return record


# =============================================================================
# CV helpers
# =============================================================================

def build_cv_origins(train_df: pd.DataFrame, cfg: FitConfig) -> List[pd.Timestamp]:
    """
    Build expanding-window CV origins inside TRAIN only.

    Each origin forecasts the next full 24-hour horizon.
    """
    if len(train_df) < (cfg.cv_min_train_rows + cfg.cv_horizon):
        return []

    idx = train_df.index.sort_values()
    possible_origins: List[pd.Timestamp] = []

    for ts in idx:
        if ts.hour != 0:
            continue

        train_part = train_df.loc[train_df.index < ts]
        val_end = ts + pd.Timedelta(hours=cfg.cv_horizon - 1)

        if len(train_part) < cfg.cv_min_train_rows:
            continue
        if val_end > idx.max():
            continue

        val_idx = pd.date_range(ts, periods=cfg.cv_horizon, freq="h")
        val_df = train_df.reindex(val_idx)

        if len(val_df) != cfg.cv_horizon:
            continue
        if val_df["energy"].isna().any():
            continue
        if val_df.isna().any().any():
            continue

        possible_origins.append(ts)

    if not possible_origins:
        return []

    if len(possible_origins) <= cfg.cv_n_folds:
        return possible_origins

    selected = np.linspace(0, len(possible_origins) - 1, cfg.cv_n_folds).round().astype(int)
    selected = sorted(set(int(x) for x in selected))
    return [possible_origins[i] for i in selected]


def evaluate_candidate_cv(
    train_df: pd.DataFrame,
    exog_cols: List[str],
    order: Tuple[int, int, int],
    seasonal_order: Tuple[int, int, int, int],
    cv_origins: List[pd.Timestamp],
    cfg: FitConfig,
) -> Dict[str, Any]:
    """
    Run expanding-window CV for one candidate inside TRAIN only.
    """
    if not cfg.cv_enabled:
        return {
            "cv_enabled": False,
            "cv_n_folds_requested": 0,
            "cv_n_folds_ok": 0,
            "cv_metric": cfg.cv_metric,
            "cv_mean": None,
            "cv_std": None,
            "cv_rmse_mean": None,
            "cv_mae_mean": None,
            "cv_smape_mean": None,
            "cv_fold_details": [],
            "cv_error": None,
        }

    if not cv_origins:
        return {
            "cv_enabled": True,
            "cv_n_folds_requested": int(cfg.cv_n_folds),
            "cv_n_folds_ok": 0,
            "cv_metric": cfg.cv_metric,
            "cv_mean": None,
            "cv_std": None,
            "cv_rmse_mean": None,
            "cv_mae_mean": None,
            "cv_smape_mean": None,
            "cv_fold_details": [],
            "cv_error": "No eligible CV folds were available inside TRAIN.",
        }

    fold_details: List[Dict[str, Any]] = []
    rmse_vals: List[float] = []
    mae_vals: List[float] = []
    smape_vals: List[float] = []

    for fold_idx, origin in enumerate(cv_origins, start=1):
        try:
            tr = train_df.loc[train_df.index < origin].copy()
            val_idx = pd.date_range(origin, periods=cfg.cv_horizon, freq="h")
            va = train_df.reindex(val_idx).copy()

            y_tr = tr["energy"].astype(float)
            X_tr = tr[exog_cols].copy() if exog_cols else None
            if X_tr is not None:
                X_tr = ensure_numeric_exog(X_tr)

            y_va = va["energy"].astype(float).values
            X_va = va[exog_cols].copy() if exog_cols else None
            if X_va is not None:
                X_va = ensure_numeric_exog(X_va)
                if X_va.isna().any().any():
                    raise ValueError("Validation exog contains NaN values.")

            model = SARIMAX(
                endog=y_tr,
                exog=X_tr,
                order=order,
                seasonal_order=seasonal_order,
                enforce_stationarity=cfg.enforce_stationarity,
                enforce_invertibility=cfg.enforce_invertibility,
            )
            res = model.fit(disp=False, maxiter=cfg.maxiter)

            fc = res.get_forecast(steps=cfg.cv_horizon, exog=X_va).predicted_mean
            y_hat = np.clip(fc.values.astype(float), a_min=0.0, a_max=None)

            scores = score_arrays(y_va, y_hat)
            rmse_vals.append(scores["RMSE"])
            mae_vals.append(scores["MAE"])
            smape_vals.append(scores["sMAPE"])

            fold_details.append({
                "fold": int(fold_idx),
                "origin": str(origin),
                "train_end": str(origin - pd.Timedelta(hours=1)),
                "val_start": str(origin),
                "val_end": str(origin + pd.Timedelta(hours=cfg.cv_horizon - 1)),
                "train_rows": int(len(tr)),
                "RMSE": float(scores["RMSE"]),
                "MAE": float(scores["MAE"]),
                "sMAPE": float(scores["sMAPE"]),
                "converged": bool(getattr(res, "mle_retvals", {}).get("converged", True)),
                "error": None,
            })

        except Exception as e:
            fold_details.append({
                "fold": int(fold_idx),
                "origin": str(origin),
                "train_end": str(origin - pd.Timedelta(hours=1)),
                "val_start": str(origin),
                "val_end": str(origin + pd.Timedelta(hours=cfg.cv_horizon - 1)),
                "train_rows": int(len(train_df.loc[train_df.index < origin])),
                "RMSE": None,
                "MAE": None,
                "sMAPE": None,
                "converged": False,
                "error": str(e),
            })

    if not rmse_vals:
        return {
            "cv_enabled": True,
            "cv_n_folds_requested": int(cfg.cv_n_folds),
            "cv_n_folds_ok": 0,
            "cv_metric": cfg.cv_metric,
            "cv_mean": None,
            "cv_std": None,
            "cv_rmse_mean": None,
            "cv_mae_mean": None,
            "cv_smape_mean": None,
            "cv_fold_details": fold_details,
            "cv_error": "All CV folds failed.",
        }

    metric_name = cfg.cv_metric.upper()
    if metric_name == "SMAPE":
        metric_values = smape_vals
    elif metric_name == "MAE":
        metric_values = mae_vals
    else:
        metric_values = rmse_vals

    return {
        "cv_enabled": True,
        "cv_n_folds_requested": int(cfg.cv_n_folds),
        "cv_n_folds_ok": int(len(rmse_vals)),
        "cv_metric": cfg.cv_metric,
        "cv_mean": float(np.mean(metric_values)),
        "cv_std": float(np.std(metric_values)),
        "cv_rmse_mean": float(np.mean(rmse_vals)),
        "cv_mae_mean": float(np.mean(mae_vals)),
        "cv_smape_mean": float(np.mean(smape_vals)),
        "cv_fold_details": fold_details,
        "cv_error": None,
    }


# =============================================================================
# Model ranking and artifact helpers
# =============================================================================

def strip_result_obj(rec: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if rec is None:
        return None
    return {k: v for k, v in rec.items() if k != "_result_obj"}


def pick_best(records: List[Dict[str, Any]], cfg: FitConfig) -> Optional[Dict[str, Any]]:
    """
    Pick the best model using:
      1. converged valid candidates
      2. CV mean
      3. CV std
      4. AIC
      5. BIC
    """
    good = [r for r in records if r["aic"] is not None and r["bic"] is not None]
    if not good:
        return None

    converged = [r for r in good if r.get("converged")]
    pool = converged if converged else good

    if cfg.cv_enabled:
        pool_cv = [
            r for r in pool
            if r.get("cv_n_folds_ok", 0) > 0 and r.get("cv_mean") is not None
        ]
        if pool_cv:
            return sorted(
                pool_cv,
                key=lambda r: (
                    r["cv_mean"],
                    r.get("cv_std", float("inf")),
                    r["aic"],
                    r["bic"],
                ),
            )[0]

    return sorted(pool, key=lambda r: (r["aic"], r["bic"]))[0]


def save_coefficients(res, out_csv: Path) -> None:
    """
    Save coefficient estimates and intervals for the final fitted model.
    """
    params = res.params
    bse = res.bse
    pvalues = res.pvalues
    conf = res.conf_int()
    conf.columns = ["ci_lower", "ci_upper"]

    coef_df = pd.DataFrame({
        "term": params.index,
        "coef": params.values,
        "std_err": bse.values,
        "p_value": pvalues.values,
        "ci_lower": conf["ci_lower"].values,
        "ci_upper": conf["ci_upper"].values,
    })
    coef_df.to_csv(out_csv, index=False)


def final_outputs_exist(out_dir: Path) -> bool:
    """
    Check whether final model artifacts already exist.
    """
    required = [
        out_dir / "best_model.pkl",
        out_dir / "best_params.json",
        out_dir / "coefficients.csv",
        out_dir / "search_results.csv",
        out_dir / "split_manifest.json",
    ]
    return all(path.exists() for path in required)


# =============================================================================
# Checkpoint helpers
# =============================================================================

def load_checkpoint(
    checkpoint_path: Path,
    partial_search_path: Path,
) -> Tuple[int, List[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """
    Load resume state for one appliance if available.
    """
    start_idx = 0
    records: List[Dict[str, Any]] = []
    best_so_far: Optional[Dict[str, Any]] = None

    if checkpoint_path.exists():
        log(f"Loading checkpoint: {checkpoint_path}")
        ckpt = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        start_idx = int(ckpt.get("last_completed_combo_idx", 0))
        best_so_far = ckpt.get("best_so_far")

        if partial_search_path.exists():
            prev_df = pd.read_csv(partial_search_path)
            records = prev_df.to_dict(orient="records")
            log(f"Loaded partial search results: rows={len(records):,} from {partial_search_path}")

    return start_idx, records, best_so_far


def save_checkpoint(
    checkpoint_path: Path,
    partial_search_path: Path,
    appliance: str,
    i: int,
    total_combos: int,
    best_so_far: Optional[Dict[str, Any]],
    exog_cols: List[str],
    manifest: Dict[str, Any],
    cv_origins: List[pd.Timestamp],
    records: List[Dict[str, Any]],
    search_plan_meta: Dict[str, Any],
) -> None:
    """
    Save current progress and partial search results.
    """
    pd.DataFrame(records).to_csv(partial_search_path, index=False)

    checkpoint = {
        "appliance": appliance,
        "last_completed_combo_idx": int(i),
        "total_combos": int(total_combos),
        "best_so_far": strip_result_obj(best_so_far),
        "exog_columns": exog_cols,
        "manifest": manifest,
        "cv_origins": [str(x) for x in cv_origins],
        "search_plan_meta": search_plan_meta,
        "updated_at": datetime.now().isoformat(),
    }
    checkpoint_path.write_text(json.dumps(checkpoint, indent=2), encoding="utf-8")


def cleanup_checkpoint_files(checkpoint_path: Path, partial_search_path: Path) -> None:
    """
    Remove temporary resume files after successful completion.
    """
    if checkpoint_path.exists():
        checkpoint_path.unlink()
    if partial_search_path.exists():
        partial_search_path.unlink()


# =============================================================================
# Per-appliance pipeline
# =============================================================================

def run_for_appliance(csv_path: Path, cfg: FitConfig) -> Dict[str, Any]:
    """
    Run the full Stage 3.5.2 fitting pipeline for one appliance.
    """
    appliance = csv_path.stem

    # Apply appliance-specific config overrides (tighter bounds for ref/efan)
    cfg = get_appliance_config(appliance, cfg)
    log(f"--- START appliance: {appliance} ---")
    if appliance in APPLIANCE_CONFIG_OVERRIDES:
        log(f"Applied config overrides for {appliance}: {APPLIANCE_CONFIG_OVERRIDES[appliance]}")

    out_dir = get_model_output_dir(appliance)

    model_path = out_dir / "best_model.pkl"
    coef_path = out_dir / "coefficients.csv"
    search_path = out_dir / "search_results.csv"
    params_path = out_dir / "best_params.json"
    split_path = out_dir / "split_manifest.json"
    checkpoint_path = out_dir / "checkpoint.json"
    partial_search_path = out_dir / "search_results.partial.csv"

    if final_outputs_exist(out_dir):
        log(f"Appliance {appliance} already completed. Skipping.")
        return {
            "appliance": appliance,
            "status": "skipped_already_done",
            "out_dir": str(out_dir),
        }

    df = load_model_ready_csv(csv_path)
    report = load_premodel_report(appliance)

    differencing_candidates = get_differencing_candidates(report)
    seasonal_period = get_seasonal_period(report, cfg)

    log(
        "Derived from Stage 3.5.1: "
        f"s={seasonal_period} | "
        f"differencing_candidates={differencing_candidates}"
    )

    y, X, exog_cols = build_y_exog(df)
    data = pd.concat([y.rename("energy"), X], axis=1) if X is not None else y.to_frame("energy")

    # Drop rows with missing values from lag/rolling features before fitting.
    if cfg.dropna:
        before = len(data)
        data = data.dropna()
        dropped = before - len(data)
        log(f"Drop-NA: dropped={dropped:,} | remaining={len(data):,}")

    if len(data) < cfg.min_rows_required:
        raise RuntimeError(f"Too few rows after dropna: n={len(data)} < {cfg.min_rows_required}")

    train_df, test_df, manifest = hybrid_split(data, cfg)
    log("Hybrid split manifest (counts): " + json.dumps(manifest["counts"]))

    if len(test_df) == 0:
        warn("TEST set is empty after hybrid split. Stage 3.5.3 will have nothing to evaluate.")
    if len(train_df) < cfg.min_rows_required:
        warn(f"TRAIN set is small (n={len(train_df)}). Fits may be unstable.")

    y_train = train_df["energy"].astype(float)
    X_train = train_df.drop(columns=["energy"]) if len(train_df.columns) > 1 else None

    cv_origins = build_cv_origins(train_df, cfg)
    if cfg.cv_enabled:
        log(
            "CV setup: "
            f"enabled={cfg.cv_enabled} | horizon={cfg.cv_horizon} | "
            f"requested_folds={cfg.cv_n_folds} | eligible_folds={len(cv_origins)} | "
            f"metric={cfg.cv_metric}"
        )
        if cv_origins:
            log("CV origins: " + ", ".join(str(x) for x in cv_origins))
        else:
            warn("No eligible CV folds found inside TRAIN. Selection will fall back to AIC/BIC.")

    search_plan = build_search_plan(cfg, differencing_candidates, seasonal_period)
    total_combos = len(search_plan)

    search_plan_meta = {
        "differencing_candidates": differencing_candidates,
        "seasonal_period": seasonal_period,
        "total_combos": int(total_combos),
    }

    log(f"Search space size (bounded): {total_combos:,} models")

    start_idx, records, best_so_far = load_checkpoint(checkpoint_path, partial_search_path)

    if start_idx > 0:
        log(f"Resuming appliance {appliance} from combo index {start_idx + 1}/{total_combos}")
        if len(records) != start_idx:
            warn(
                f"Checkpoint mismatch: partial rows={len(records)} but "
                f"last_completed_combo_idx={start_idx}. Will proceed using checkpoint index."
            )

    last_ckpt_time = time.time()

    for i, candidate in enumerate(search_plan, start=1):
        if i <= start_idx:
            continue

        order = candidate["order"]
        seasonal_order = candidate["seasonal_order"]

        if i == 1 or i % cfg.cv_progress_every == 0 or i == total_combos:
            log(f"[{i}/{total_combos}] Trying order={order}, seasonal={seasonal_order}")

        # Fit on full TRAIN for AIC/BIC and final candidate stats.
        rec = fit_one_model(y_train, X_train, order, seasonal_order, cfg)

        # Add expanding-window CV inside TRAIN.
        cv_info = evaluate_candidate_cv(
            train_df=train_df,
            exog_cols=exog_cols,
            order=order,
            seasonal_order=seasonal_order,
            cv_origins=cv_origins,
            cfg=cfg,
        )
        rec.update(cv_info)

        records.append(strip_result_obj(rec))

        # Keep a live best tracker for checkpointing.
        candidate_ok = rec.get("aic") is not None and rec.get("bic") is not None
        if candidate_ok:
            if best_so_far is None:
                best_so_far = rec
                log(
                    "  -> current BEST: "
                    f"AIC={rec['aic']:.2f}, BIC={rec['bic']:.2f}, conv={rec.get('converged')}, "
                    f"cv_mean={rec.get('cv_mean')}, cv_folds_ok={rec.get('cv_n_folds_ok')}"
                )
            else:
                prev_best = pick_best([strip_result_obj(best_so_far), strip_result_obj(rec)], cfg)
                is_new_best = (
                    prev_best is not None and
                    prev_best["p"] == rec["p"] and
                    prev_best["d"] == rec["d"] and
                    prev_best["q"] == rec["q"] and
                    prev_best["P"] == rec["P"] and
                    prev_best["D"] == rec["D"] and
                    prev_best["Q"] == rec["Q"] and
                    prev_best["s"] == rec["s"]
                )
                if is_new_best:
                    best_so_far = rec
                    log(
                        "  -> new BEST: "
                        f"AIC={rec['aic']:.2f}, BIC={rec['bic']:.2f}, conv={rec.get('converged')}, "
                        f"cv_mean={rec.get('cv_mean')}, cv_folds_ok={rec.get('cv_n_folds_ok')}"
                    )

        should_checkpoint = (
            (cfg.checkpoint_every_n_models > 0 and i % cfg.checkpoint_every_n_models == 0) or
            ((time.time() - last_ckpt_time) >= cfg.checkpoint_every_seconds) or
            (i == total_combos)
        )

        if should_checkpoint:
            save_checkpoint(
                checkpoint_path=checkpoint_path,
                partial_search_path=partial_search_path,
                appliance=appliance,
                i=i,
                total_combos=total_combos,
                best_so_far=best_so_far,
                exog_cols=exog_cols,
                manifest=manifest,
                cv_origins=cv_origins,
                records=records,
                search_plan_meta=search_plan_meta,
            )
            last_ckpt_time = time.time()
            log(
                f"Checkpoint saved: combo={i}/{total_combos} | "
                f"partial_rows={len(records):,} | path={checkpoint_path.name}"
            )

    best = pick_best(records, cfg)
    if best is None and best_so_far is not None:
        best = strip_result_obj(best_so_far)

    if best is None:
        raise RuntimeError("No valid models produced AIC/BIC. Consider loosening bounds or checking exog NaNs.")

    best_order = (int(best["p"]), int(best["d"]), int(best["q"]))
    best_seasonal = (int(best["P"]), int(best["D"]), int(best["Q"]), int(best["s"]))
    log(f"Refitting BEST for saving: order={best_order}, seasonal={best_seasonal}")

    best_model = SARIMAX(
        endog=y_train,
        exog=X_train,
        order=best_order,
        seasonal_order=best_seasonal,
        enforce_stationarity=cfg.enforce_stationarity,
        enforce_invertibility=cfg.enforce_invertibility,
    )
    best_res = best_model.fit(disp=cfg.disp, maxiter=cfg.maxiter)

    log(f"Saving model: {model_path}")
    best_res.save(str(model_path))

    log(f"Saving coefficients: {coef_path}")
    save_coefficients(best_res, coef_path)

    log(f"Saving search table: {search_path}")
    pd.DataFrame(records).to_csv(search_path, index=False)

    log(f"Saving split manifest: {split_path}")
    split_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    params = {
        "appliance": appliance,
        "timestamp": datetime.now().isoformat(),
        "fit_config": asdict(cfg),
        "derived_from_premodel": {
            "seasonal_period": seasonal_period,
            "differencing_candidates": differencing_candidates,
            "premodel_report": str(get_premodel_report_path(appliance)),
        },
        "model_selection": {
            "selection_strategy": (
                "time_series_cv_then_aic_bic_tiebreak"
                if cfg.cv_enabled else
                "aic_bic_only"
            ),
            "cv_enabled": bool(cfg.cv_enabled),
            "cv_metric": cfg.cv_metric,
            "cv_horizon": int(cfg.cv_horizon),
            "cv_n_folds_requested": int(cfg.cv_n_folds),
            "cv_n_folds_eligible": int(len(cv_origins)),
            "search_space_total_models": int(total_combos),
        },
        "best": {
            "order": {
                "p": int(best["p"]),
                "d": int(best["d"]),
                "q": int(best["q"]),
            },
            "seasonal_order": {
                "P": int(best["P"]),
                "D": int(best["D"]),
                "Q": int(best["Q"]),
                "s": int(best["s"]),
            },
            "aic": float(best_res.aic),
            "bic": float(best_res.bic),
            "converged": bool(getattr(best_res, "mle_retvals", {}).get("converged", True)),
            "cv_metric": best.get("cv_metric"),
            "cv_mean": best.get("cv_mean"),
            "cv_std": best.get("cv_std"),
            "cv_rmse_mean": best.get("cv_rmse_mean"),
            "cv_mae_mean": best.get("cv_mae_mean"),
            "cv_smape_mean": best.get("cv_smape_mean"),
            "cv_n_folds_ok": best.get("cv_n_folds_ok"),
        },
        "exog_columns": exog_cols,
        "n_total_rows_after_dropna": int(len(data)),
        "split_counts": manifest["counts"],
        "split_ranges": manifest["ranges"],
        "artifacts": {
            "model_path": str(model_path),
            "coefficients_csv": str(coef_path),
            "search_results_csv": str(search_path),
            "split_manifest_json": str(split_path),
        },
    }

    log(f"Saving best params: {params_path}")
    params_path.write_text(json.dumps(params, indent=2), encoding="utf-8")

    cleanup_checkpoint_files(checkpoint_path, partial_search_path)

    log(
        f"--- DONE appliance: {appliance} | "
        f"AIC={best_res.aic:.2f}, BIC={best_res.bic:.2f}, "
        f"CV={best.get('cv_metric')}:{best.get('cv_mean')} ---"
    )

    return {
        "appliance": appliance,
        "status": "ok",
        "best_aic": float(best_res.aic),
        "best_bic": float(best_res.bic),
        "best_cv_metric": best.get("cv_metric"),
        "best_cv_mean": best.get("cv_mean"),
        "best_order": params["best"]["order"],
        "best_seasonal_order": params["best"]["seasonal_order"],
        "out_dir": str(out_dir),
        "split_counts": manifest["counts"],
    }


# =============================================================================
# Main
# =============================================================================

def main() -> None:
    t_all = time.perf_counter()

    log("==============================================")
    log("SARIMAX Model Estimation and Fitting")
    log(f"Input dir   : {DEFAULT_INPUT_DIR}")
    log(f"Output root : {DEFAULT_OUT_ROOT}")
    log(f"Glob        : {DEFAULT_GLOB}")
    log(f"FitConfig   : {asdict(CFG)}")
    log("==============================================")

    if not DEFAULT_INPUT_DIR.exists():
        raise FileNotFoundError(f"DEFAULT_INPUT_DIR not found: {DEFAULT_INPUT_DIR}")
    if not DEFAULT_OUT_ROOT.exists():
        raise FileNotFoundError(f"DEFAULT_OUT_ROOT not found: {DEFAULT_OUT_ROOT}")

    files = sorted(DEFAULT_INPUT_DIR.glob(DEFAULT_GLOB))
    if not files:
        raise FileNotFoundError(f"No CSV files found in {DEFAULT_INPUT_DIR} with pattern {DEFAULT_GLOB}")

    log(f"Discovered {len(files)} appliance CSV files.")

    summary: Dict[str, Any] = {
        "timestamp": datetime.now().isoformat(),
        "config": asdict(CFG),
        "input_dir": str(DEFAULT_INPUT_DIR),
        "output_root": str(DEFAULT_OUT_ROOT),
        "n_files": len(files),
        "ok": 0,
        "failed": 0,
        "results": [],
        "failures": [],
    }

    for idx, csv_path in enumerate(files, start=1):
        log(f"[{idx}/{len(files)}] Processing: {csv_path.name}")
        try:
            t0 = time.perf_counter()
            res = run_for_appliance(csv_path, CFG)
            summary["results"].append(res)
            summary["ok"] += 1
            log(f"[{idx}/{len(files)}] OK {csv_path.stem} | elapsed={time.perf_counter() - t0:.2f}s")
        except Exception as e:
            summary["failed"] += 1
            tb = traceback.format_exc()
            err(f"[{idx}/{len(files)}] FAILED {csv_path.stem}: {e}")
            err(tb)
            summary["failures"].append({
                "appliance": csv_path.stem,
                "input": str(csv_path),
                "error": str(e),
                "traceback": tb,
            })

    summary_path = get_batch_summary_path()
    log(f"Writing batch summary: {summary_path}")
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    log("==============================================")
    log(f"[DONE] Model Training complete | elapsed={time.perf_counter() - t_all:.2f}s")
    log(f"OK={summary['ok']} | FAILED={summary['failed']}")
    log(f"Summary: {summary_path}")
    log("==============================================")


if __name__ == "__main__":
    main()