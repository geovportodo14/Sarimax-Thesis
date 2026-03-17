"""
Outputs (per appliance):
  model/sarimax/<appliance_stem>/
    - best_model.pkl
    - best_params.json
    - coefficients.csv
    - search_results.csv
    - split_manifest.json
    - checkpoint.json                  # during run only
    - search_results.partial.csv       # during run only
  model/sarimax/_fit_summary.json

Modified version:
  - Preserves original hybrid split + bounded grid search + AIC/BIC logic
  - Adds expanding-window time-series CV inside TRAIN only
  - Selects best model primarily by CV metric, then AIC/BIC as tie-breakers
  - Adds checkpoint/resume support per appliance
  - Skips already-finished appliances on restart
  - Saves progress after every candidate model
"""

from __future__ import annotations

import json
import time
import traceback
import warnings
from dataclasses import dataclass, asdict
from datetime import datetime
from itertools import product
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX

warnings.filterwarnings("ignore")


# =============================================================================
# Defaults
# =============================================================================

DEFAULT_INPUT_DIR = Path("data")
DEFAULT_PREMODEL_DIR = Path("model/reports")
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
# Config (bounded search; hybrid train/test split; CV selection)
# =============================================================================

@dataclass
class FitConfig:
    # --- Hybrid split controls (Option C) ---
    synthetic_end: str = "2026-01-03 18:00:00"
    real_start: str = "2026-01-03 19:00:00"

    # Portion of REAL data to include in TRAIN (first segment chronologically).
    real_train_ratio: float = 0.70

    # Snap split so training always ends at 23:00 and test starts at next day 00:00
    require_full_day_boundary: bool = True
    train_end_hour: int = 23

    # --- Seasonal period default (overridden by Stage 3.5.1 if present) ---
    default_seasonal_period: int = 24

    # --- Bounds for systematic grid search ---
    max_p: int = 3
    max_q: int = 3
    max_P: int = 2
    max_Q: int = 2
    max_total_order: int = 10  # p+q+P+Q cap

    # Fit options
    enforce_stationarity: bool = True
    enforce_invertibility: bool = True
    maxiter: int = 150
    disp: bool = False

    # Exog handling
    dropna: bool = True
    min_rows_required: int = 300  # after dropna, to avoid nonsense fits

    # --- time-series CV selection ---
    cv_enabled: bool = True
    cv_horizon: int = 24
    cv_n_folds: int = 3
    cv_min_train_rows: int = 300
    cv_metric: str = "RMSE"  # RMSE, MAE, sMAPE
    cv_progress_every: int = 10

    # --- checkpoint / resume ---
    checkpoint_every_n_models: int = 1   # safer than time-only
    checkpoint_every_seconds: int = 600  # optional extra flush cadence


CFG = FitConfig()


# =============================================================================
# Basic metrics
# =============================================================================

def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(np.abs(y_true - y_pred)))


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def smape(y_true: np.ndarray, y_pred: np.ndarray, eps: float = 1e-9) -> float:
    denom = np.maximum(np.abs(y_true) + np.abs(y_pred), eps)
    return float(np.mean(2.0 * np.abs(y_pred - y_true) / denom) * 100.0)


# =============================================================================
# IO helpers
# =============================================================================

def load_model_ready_csv(path: Path) -> pd.DataFrame:
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


def load_premodel_report(appliance_stem: str) -> Dict[str, Any]:
    report_path = DEFAULT_PREMODEL_DIR / f"{appliance_stem}_premodel_report.json"
    if not report_path.exists():
        raise FileNotFoundError(f"Missing premodel report for {appliance_stem}: {report_path}")
    log(f"Loading premodel report: {report_path}")
    return json.loads(report_path.read_text(encoding="utf-8"))


def ensure_numeric_exog(exog: pd.DataFrame) -> pd.DataFrame:
    out = exog.copy()
    for c in out.columns:
        if out[c].dtype == "bool":
            out[c] = out[c].astype(int)
        if out[c].dtype == "object":
            out[c] = pd.to_numeric(out[c], errors="coerce")
    return out


def build_y_exog(df: pd.DataFrame) -> Tuple[pd.Series, Optional[pd.DataFrame], List[str]]:
    y = df["energy"].astype(float)
    exog_cols = [c for c in df.columns if c != "energy"]
    if not exog_cols:
        warn("No exogenous columns found. Model will fit without exog.")
        return y, None, []
    X = ensure_numeric_exog(df[exog_cols].copy())
    return y, X, exog_cols


# =============================================================================
# Hybrid split (Option C)
# =============================================================================

def hybrid_split(data: pd.DataFrame, cfg: FitConfig) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """
    Split by time boundary:
      synthetic = <= synthetic_end
      real      = >= real_start

    TRAIN = synthetic + earlier real portion
    TEST  = later real portion

    If require_full_day_boundary=True:
      - compute raw split inside REAL block using real_train_ratio
      - move TRAIN end to the last timestamp at 23:00 on or before the raw split
      - TEST starts at next hour, which should be next day 00:00
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
        }
    }

    return train, test, manifest


# =============================================================================
# Search / Fit / CV helpers
# =============================================================================

def iter_orders(cfg: FitConfig, d: int, D: int) -> List[Tuple[Tuple[int, int, int], Tuple[int, int, int, int]]]:
    combos = []
    for p, q, P, Q in product(
        range(cfg.max_p + 1),
        range(cfg.max_q + 1),
        range(cfg.max_P + 1),
        range(cfg.max_Q + 1),
    ):
        if (p + q + P + Q) > cfg.max_total_order:
            continue
        combos.append(((p, d, q), (P, D, Q, None)))  # s injected later
    return combos


def fit_one_model(
    y_train: pd.Series,
    X_train: Optional[pd.DataFrame],
    order: Tuple[int, int, int],
    seasonal_order: Tuple[int, int, int, int],
    cfg: FitConfig
) -> Dict[str, Any]:
    t0 = time.perf_counter()
    record: Dict[str, Any] = {
        "p": order[0], "d": order[1], "q": order[2],
        "P": seasonal_order[0], "D": seasonal_order[1], "Q": seasonal_order[2], "s": seasonal_order[3],
        "aic": None, "bic": None, "converged": False, "fit_seconds": None,
        "error": None
    }
    try:
        model = SARIMAX(
            endog=y_train,
            exog=X_train,
            order=order,
            seasonal_order=seasonal_order,
            enforce_stationarity=cfg.enforce_stationarity,
            enforce_invertibility=cfg.enforce_invertibility
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


def build_cv_origins(train_df: pd.DataFrame, cfg: FitConfig) -> List[pd.Timestamp]:
    """
    Build expanding-window CV origins within TRAIN only.

    Each origin corresponds to forecasting:
      origin 00:00 -> origin+23h
    while training uses all rows before origin.
    """
    if len(train_df) < (cfg.cv_min_train_rows + cfg.cv_horizon):
        return []

    idx = train_df.index.sort_values()

    possible_origins = []
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

    sel = np.linspace(0, len(possible_origins) - 1, cfg.cv_n_folds).round().astype(int)
    sel = sorted(set(int(x) for x in sel))
    return [possible_origins[i] for i in sel]


def score_arrays(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    return {
        "RMSE": rmse(y_true, y_pred),
        "MAE": mae(y_true, y_pred),
        "sMAPE": smape(y_true, y_pred),
    }


def evaluate_candidate_cv(
    train_df: pd.DataFrame,
    exog_cols: List[str],
    order: Tuple[int, int, int],
    seasonal_order: Tuple[int, int, int, int],
    cv_origins: List[pd.Timestamp],
    cfg: FitConfig,
) -> Dict[str, Any]:
    """
    Expanding-window CV over TRAIN only.
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


def pick_best(records: List[Dict[str, Any]], cfg: FitConfig) -> Optional[Dict[str, Any]]:
    good = [r for r in records if r["aic"] is not None and r["bic"] is not None]
    if not good:
        return None

    converged = [r for r in good if r.get("converged")]
    pool = converged if converged else good

    if cfg.cv_enabled:
        pool_cv = [r for r in pool if r.get("cv_n_folds_ok", 0) > 0 and r.get("cv_mean") is not None]
        if pool_cv:
            return sorted(
                pool_cv,
                key=lambda r: (
                    r["cv_mean"],
                    r.get("cv_std", float("inf")),
                    r["aic"],
                    r["bic"],
                )
            )[0]

    return sorted(pool, key=lambda r: (r["aic"], r["bic"]))[0]


def save_coefficients(res, out_csv: Path) -> None:
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


# =============================================================================
# Checkpoint helpers
# =============================================================================

def strip_result_obj(rec: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if rec is None:
        return None
    return {k: v for k, v in rec.items() if k != "_result_obj"}


def final_outputs_exist(out_dir: Path) -> bool:
    required = [
        out_dir / "best_model.pkl",
        out_dir / "best_params.json",
        out_dir / "coefficients.csv",
        out_dir / "search_results.csv",
        out_dir / "split_manifest.json",
    ]
    return all(p.exists() for p in required)


def load_checkpoint(
    checkpoint_path: Path,
    partial_search_path: Path,
) -> Tuple[int, List[Dict[str, Any]], Optional[Dict[str, Any]]]:
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
    d: int,
    D: int,
    s: int,
    exog_cols: List[str],
    manifest: Dict[str, Any],
    cv_origins: List[pd.Timestamp],
    records: List[Dict[str, Any]],
) -> None:
    pd.DataFrame(records).to_csv(partial_search_path, index=False)

    checkpoint = {
        "appliance": appliance,
        "last_completed_combo_idx": int(i),
        "total_combos": int(total_combos),
        "best_so_far": strip_result_obj(best_so_far),
        "d": int(d),
        "D": int(D),
        "s": int(s),
        "exog_columns": exog_cols,
        "manifest": manifest,
        "cv_origins": [str(x) for x in cv_origins],
        "updated_at": datetime.now().isoformat(),
    }
    checkpoint_path.write_text(json.dumps(checkpoint, indent=2), encoding="utf-8")


def cleanup_checkpoint_files(checkpoint_path: Path, partial_search_path: Path) -> None:
    if checkpoint_path.exists():
        checkpoint_path.unlink()
    if partial_search_path.exists():
        partial_search_path.unlink()


# =============================================================================
# Per-appliance pipeline
# =============================================================================

def run_for_appliance(csv_path: Path, cfg: FitConfig) -> Dict[str, Any]:
    appliance = csv_path.stem
    log(f"--- START appliance: {appliance} ---")

    # Output folder and paths created EARLY for resume support
    out_dir = DEFAULT_OUT_ROOT / appliance
    out_dir.mkdir(parents=True, exist_ok=True)

    model_path = out_dir / "best_model.pkl"
    coef_path = out_dir / "coefficients.csv"
    search_path = out_dir / "search_results.csv"
    params_path = out_dir / "best_params.json"
    split_path = out_dir / "split_manifest.json"

    checkpoint_path = out_dir / "checkpoint.json"
    partial_search_path = out_dir / "search_results.partial.csv"

    # Skip already completed appliances
    if final_outputs_exist(out_dir):
        log(f"Appliance {appliance} already completed. Skipping.")
        return {
            "appliance": appliance,
            "status": "skipped_already_done",
            "out_dir": str(out_dir),
        }

    df = load_model_ready_csv(csv_path)
    report = load_premodel_report(appliance)

    # Derive differencing from Stage 3.5.1
    suggested = report.get("suggested_differencing", {})
    d = int(suggested.get("rule_based_d", 0))
    D = int(suggested.get("rule_based_D", 0))
    s = int(report.get("config", {}).get("seasonal_period", cfg.default_seasonal_period))
    log(f"Derived from Stage 3.5.1: d={d}, D={D}, s={s}")

    # Build data with exog
    y, X, exog_cols = build_y_exog(df)
    data = pd.concat([y.rename("energy"), X], axis=1) if X is not None else y.to_frame("energy")

    # Drop NA due to lag features etc.
    if cfg.dropna:
        before = len(data)
        data = data.dropna()
        dropped = before - len(data)
        log(f"Drop-NA: dropped={dropped:,} | remaining={len(data):,}")

    if len(data) < cfg.min_rows_required:
        raise RuntimeError(f"Too few rows after dropna: n={len(data)} < {cfg.min_rows_required}")

    # Hybrid split: synthetic + first part real => train; rest real => test reserved
    train_df, test_df, manifest = hybrid_split(data, cfg)
    log("Hybrid split manifest (counts): " + json.dumps(manifest["counts"]))

    if len(test_df) == 0:
        warn("TEST set is empty after hybrid split. Stage 3.5.3 will have nothing to evaluate.")
    if len(train_df) < cfg.min_rows_required:
        warn(f"TRAIN set is small (n={len(train_df)}). Fits may be unstable.")

    y_train = train_df["energy"].astype(float)
    X_train = train_df.drop(columns=["energy"]) if len(train_df.columns) > 1 else None

    # CV folds inside TRAIN only
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

    # Systematic bounded search
    combos = iter_orders(cfg, d=d, D=D)
    total_combos = len(combos)
    log(f"Search space size (bounded): {total_combos:,} models")

    # Resume state
    start_idx, records, best_so_far = load_checkpoint(checkpoint_path, partial_search_path)

    if start_idx > 0:
        log(f"Resuming appliance {appliance} from combo index {start_idx + 1}/{total_combos}")
        if len(records) != start_idx:
            warn(
                f"Checkpoint mismatch: partial rows={len(records)} but "
                f"last_completed_combo_idx={start_idx}. Will proceed using checkpoint index."
            )

    last_ckpt_time = time.time()

    for i, (order, seas_template) in enumerate(combos, start=1):
        if i <= start_idx:
            continue

        seasonal_order = (seas_template[0], seas_template[1], seas_template[2], s)

        if i == 1 or i % cfg.cv_progress_every == 0 or i == total_combos:
            log(f"[{i}/{total_combos}] Trying order={order}, seasonal={seasonal_order}")

        # Keep original full-train fit for AIC/BIC
        rec = fit_one_model(y_train, X_train, order, seasonal_order, cfg)

        # Add expanding-window CV metrics
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

        # live best tracker
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
                prev_best = pick_best(
                    [strip_result_obj(best_so_far), strip_result_obj(rec)],
                    cfg
                )
                is_new_best = (
                    prev_best is not None and
                    prev_best["p"] == rec["p"] and
                    prev_best["q"] == rec["q"] and
                    prev_best["P"] == rec["P"] and
                    prev_best["Q"] == rec["Q"] and
                    prev_best["d"] == rec["d"] and
                    prev_best["D"] == rec["D"] and
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
                d=d,
                D=D,
                s=s,
                exog_cols=exog_cols,
                manifest=manifest,
                cv_origins=cv_origins,
                records=records,
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

    # Refit best model cleanly for saving
    best_order = (int(best["p"]), d, int(best["q"]))
    best_seasonal = (int(best["P"]), D, int(best["Q"]), s)
    log(f"Refitting BEST for saving: order={best_order}, seasonal={best_seasonal}")

    best_model = SARIMAX(
        endog=y_train,
        exog=X_train,
        order=best_order,
        seasonal_order=best_seasonal,
        enforce_stationarity=cfg.enforce_stationarity,
        enforce_invertibility=cfg.enforce_invertibility
    )
    best_res = best_model.fit(disp=cfg.disp, maxiter=cfg.maxiter)

    # Save final artifacts
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
            "d": d,
            "D": D,
            "s": s,
            "premodel_report": str(DEFAULT_PREMODEL_DIR / f"{appliance}_premodel_report.json")
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
        },
        "best": {
            "order": {"p": int(best["p"]), "d": int(d), "q": int(best["q"])},
            "seasonal_order": {"P": int(best["P"]), "D": int(D), "Q": int(best["Q"]), "s": int(s)},
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
        }
    }

    log(f"Saving best params: {params_path}")
    params_path.write_text(json.dumps(params, indent=2), encoding="utf-8")

    # remove temporary checkpoint files after successful finish
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
# Main (NO ARGS)
# =============================================================================

def main() -> None:
    t_all = time.perf_counter()

    log("==============================================")
    log("Stage 3.5.2 — SARIMAX Model Estimation & Fitting (Hybrid Training + CV Selection + Resume)")
    log(f"Input dir   : {DEFAULT_INPUT_DIR}")
    log(f"Premodel dir: {DEFAULT_PREMODEL_DIR}")
    log(f"Output root : {DEFAULT_OUT_ROOT}")
    log(f"Glob        : {DEFAULT_GLOB}")
    log(f"FitConfig   : {asdict(CFG)}")
    log("==============================================")

    if not DEFAULT_INPUT_DIR.exists():
        raise FileNotFoundError(f"DEFAULT_INPUT_DIR not found: {DEFAULT_INPUT_DIR}")
    if not DEFAULT_PREMODEL_DIR.exists():
        raise FileNotFoundError(f"DEFAULT_PREMODEL_DIR not found: {DEFAULT_PREMODEL_DIR}")

    files = sorted(DEFAULT_INPUT_DIR.glob(DEFAULT_GLOB))
    if not files:
        raise FileNotFoundError(f"No CSV files found in {DEFAULT_INPUT_DIR} with pattern {DEFAULT_GLOB}")

    log(f"Discovered {len(files)} appliance CSV files.")

    summary: Dict[str, Any] = {
        "timestamp": datetime.now().isoformat(),
        "config": asdict(CFG),
        "input_dir": str(DEFAULT_INPUT_DIR),
        "premodel_dir": str(DEFAULT_PREMODEL_DIR),
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

    DEFAULT_OUT_ROOT.mkdir(parents=True, exist_ok=True)
    summary_path = DEFAULT_OUT_ROOT / "_fit_summary.json"
    log(f"Writing batch summary: {summary_path}")
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    log("==============================================")
    log(f"[DONE] Stage 3.5.2 complete | elapsed={time.perf_counter() - t_all:.2f}s")
    log(f"OK={summary['ok']} | FAILED={summary['failed']}")
    log(f"Summary: {summary_path}")
    log("==============================================")


if __name__ == "__main__":
    main()