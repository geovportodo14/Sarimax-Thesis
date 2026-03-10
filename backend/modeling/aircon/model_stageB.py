"""
Outputs (per appliance):
  models/sarimax/<appliance_stem>/
    - best_model.pkl
    - best_params.json
    - coefficients.csv
    - search_results.csv
    - split_manifest.json 
  models/sarimax/_fit_summary.json

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

DEFAULT_INPUT_DIR = Path("data/")
DEFAULT_PREMODEL_DIR = Path("model/reports/sarimax_premodel")
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
# Config (bounded search; hybrid train/test split)
# =============================================================================

@dataclass
class FitConfig:
    # --- Hybrid split controls (Option C) ---
    # You said: synthetic year is training baseline, real is scarce.
    # We assume synthetic ends at 2026-01-02 23:00:00 and real starts at 2026-01-03 00:00:00.
    # Adjust ONCE here if your boundary differs.
    synthetic_end: str = "2026-01-02 23:00:00"
    real_start: str = "2026-01-03 00:00:00"

    # Portion of REAL data to include in TRAIN (first segment chronologically).
    # Example: 0.50 means first 50% of real window goes to TRAIN; remaining 50% is TEST.
    real_train_ratio: float = 0.50

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


CFG = FitConfig()


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

    TRAIN = synthetic + first part of real (based on real_train_ratio)
    TEST  = remaining part of real
    """
    syn_end = pd.to_datetime(cfg.synthetic_end)
    real_start = pd.to_datetime(cfg.real_start)

    if data.index.min() > syn_end:
        warn("Data starts after synthetic_end; synthetic block may be empty.")
    if data.index.max() < real_start:
        warn("Data ends before real_start; real block may be empty.")

    synthetic = data.loc[data.index <= syn_end].copy()
    real = data.loc[data.index >= real_start].copy()

    if len(real) == 0:
        raise RuntimeError(
            f"Real block is empty using real_start={cfg.real_start}. "
            f"Check your timestamps and update FitConfig.real_start."
        )

    # first part of real goes into train
    real_cut = int(np.floor(len(real) * cfg.real_train_ratio))
    real_train = real.iloc[:real_cut].copy()
    real_test = real.iloc[real_cut:].copy()

    train = pd.concat([synthetic, real_train], axis=0).sort_index()
    test = real_test.sort_index()

    manifest = {
        "synthetic_end": cfg.synthetic_end,
        "real_start": cfg.real_start,
        "real_train_ratio": cfg.real_train_ratio,
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
# Search / Fit
# =============================================================================

def iter_orders(cfg: FitConfig, d: int, D: int) -> List[Tuple[Tuple[int, int, int], Tuple[int, int, int, int]]]:
    combos = []
    for p, q, P, Q in product(range(cfg.max_p + 1), range(cfg.max_q + 1),
                              range(cfg.max_P + 1), range(cfg.max_Q + 1)):
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


def pick_best(records: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    good = [r for r in records if r["aic"] is not None and r["bic"] is not None]
    if not good:
        return None
    converged = [r for r in good if r.get("converged")]
    pool = converged if converged else good
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
# Per-appliance pipeline
# =============================================================================

def run_for_appliance(csv_path: Path, cfg: FitConfig) -> Dict[str, Any]:
    appliance = csv_path.stem
    log(f"--- START appliance: {appliance} ---")

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

    # Systematic bounded search
    combos = iter_orders(cfg, d=d, D=D)
    log(f"Search space size (bounded): {len(combos):,} models")

    records: List[Dict[str, Any]] = []
    best_so_far: Optional[Dict[str, Any]] = None

    for i, (order, seas_template) in enumerate(combos, start=1):
        seasonal_order = (seas_template[0], seas_template[1], seas_template[2], s)

        if i == 1 or i % 10 == 0 or i == len(combos):
            log(f"[{i}/{len(combos)}] Trying order={order}, seasonal={seasonal_order}")

        rec = fit_one_model(y_train, X_train, order, seasonal_order, cfg)
        records.append({k: v for k, v in rec.items() if k != "_result_obj"})

        if rec.get("aic") is not None and rec.get("bic") is not None:
            if best_so_far is None:
                best_so_far = rec
                log(f"  -> current BEST: AIC={rec['aic']:.2f}, BIC={rec['bic']:.2f}, conv={rec.get('converged')}")
            else:
                def score(r): return (0 if r.get("converged") else 1, r["aic"], r["bic"])
                if score(rec) < score(best_so_far):
                    best_so_far = rec
                    log(f"  -> new BEST: AIC={rec['aic']:.2f}, BIC={rec['bic']:.2f}, conv={rec.get('converged')}")

    best = pick_best(records)
    if best is None and best_so_far is not None:
        best = {k: v for k, v in best_so_far.items() if k != "_result_obj"}
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

    # Output folder
    out_dir = DEFAULT_OUT_ROOT / appliance
    out_dir.mkdir(parents=True, exist_ok=True)

    # Save artifacts
    model_path = out_dir / "best_model.pkl"
    coef_path = out_dir / "coefficients.csv"
    search_path = out_dir / "search_results.csv"
    params_path = out_dir / "best_params.json"
    split_path = out_dir / "split_manifest.json"

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
        "best": {
            "order": {"p": int(best["p"]), "d": int(d), "q": int(best["q"])},
            "seasonal_order": {"P": int(best["P"]), "D": int(D), "Q": int(best["Q"]), "s": int(s)},
            "aic": float(best_res.aic),
            "bic": float(best_res.bic),
            "converged": bool(getattr(best_res, "mle_retvals", {}).get("converged", True)),
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

    log(f"--- DONE appliance: {appliance} | AIC={best_res.aic:.2f}, BIC={best_res.bic:.2f} ---")

    return {
        "appliance": appliance,
        "status": "ok",
        "best_aic": float(best_res.aic),
        "best_bic": float(best_res.bic),
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
    log("Stage 3.5.2 — SARIMAX Model Estimation & Fitting (Hybrid Training)")
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