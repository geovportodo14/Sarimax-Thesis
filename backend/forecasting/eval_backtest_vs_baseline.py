#!/usr/bin/env python3
"""
Evaluate saved SARIMAX backtest outputs against simple baselines.

Usage:
  python3 backend/forecasting/eval_backtest_vs_baseline.py
  python3 backend/forecasting/eval_backtest_vs_baseline.py --min-r2 0.0
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

# Allow running as a script from repo root.
_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))

from forecasting.config import APPLIANCE_MODEL_DIR, APPLIANCES, MODELS_ROOT  # noqa: E402


def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(np.abs(y_true - y_pred)))


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def r2(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    ss_res = float(np.sum((y_true - y_pred) ** 2))
    ss_tot = float(np.sum((y_true - np.mean(y_true)) ** 2))
    return float(1.0 - ss_res / ss_tot) if ss_tot > 0 else float("nan")


def pct_improvement(model_val: float, baseline_val: float) -> float:
    if baseline_val == 0:
        return float("nan")
    return float((baseline_val - model_val) / baseline_val * 100.0)


def evaluate_appliance(appliance: str, min_r2: float) -> Dict[str, Any]:
    model_rel = APPLIANCE_MODEL_DIR[appliance]
    model_dir = MODELS_ROOT / model_rel
    eval_dir = model_dir / "evaluation"

    pred_path = eval_dir / "eval_predictions.csv"
    metrics_path = eval_dir / "eval_metrics.json"

    if not pred_path.exists():
        raise FileNotFoundError(f"Missing eval predictions: {pred_path}")

    df = pd.read_csv(pred_path, parse_dates=["timestamp"]).sort_values("timestamp")
    if "actual_energy" not in df.columns or "pred_energy" not in df.columns:
        raise ValueError(f"{pred_path} missing required columns")

    y = df["actual_energy"].astype(float)
    yhat = df["pred_energy"].astype(float)

    y_mean = pd.Series(y.mean(), index=y.index)
    model_mae = mae(y.values, yhat.values)
    model_rmse = rmse(y.values, yhat.values)
    model_r2 = r2(y.values, yhat.values)
    mean_mae = mae(y.values, y_mean.values)
    mean_rmse = rmse(y.values, y_mean.values)

    lag24 = y.shift(24)
    df_lag = pd.DataFrame({"actual": y, "pred": yhat, "lag24": lag24}).dropna()
    lag24_rows = int(len(df_lag))
    lag24_mae = mae(df_lag["actual"].values, df_lag["lag24"].values) if lag24_rows else float("nan")
    lag24_rmse = rmse(df_lag["actual"].values, df_lag["lag24"].values) if lag24_rows else float("nan")

    beats_mean = bool(model_mae < mean_mae and model_rmse < mean_rmse)
    beats_lag24_rmse = bool(np.isfinite(lag24_rmse) and model_rmse < lag24_rmse)
    pass_r2 = bool(np.isfinite(model_r2) and model_r2 >= min_r2)
    status = "PASS" if beats_mean and beats_lag24_rmse and pass_r2 else "CHECK"

    source_metrics = None
    if metrics_path.exists():
        source_metrics = json.loads(metrics_path.read_text(encoding="utf-8"))

    return {
        "appliance": appliance,
        "status": status,
        "model_dir": str(model_dir),
        "rows_scored": int(len(df)),
        "rows_lag24_comp": lag24_rows,
        "model": {
            "MAE": model_mae,
            "RMSE": model_rmse,
            "R2": model_r2,
        },
        "baselines": {
            "mean": {"MAE": mean_mae, "RMSE": mean_rmse},
            "lag24": {"MAE": lag24_mae, "RMSE": lag24_rmse},
        },
        "improvement_pct": {
            "vs_mean_MAE": pct_improvement(model_mae, mean_mae),
            "vs_mean_RMSE": pct_improvement(model_rmse, mean_rmse),
            "vs_lag24_MAE": pct_improvement(model_mae, lag24_mae) if np.isfinite(lag24_mae) else float("nan"),
            "vs_lag24_RMSE": pct_improvement(model_rmse, lag24_rmse) if np.isfinite(lag24_rmse) else float("nan"),
        },
        "checks": {
            "beats_mean": beats_mean,
            "beats_lag24_rmse": beats_lag24_rmse,
            "r2_gte_threshold": pass_r2,
            "min_r2_threshold": min_r2,
        },
        "eval_metrics_json": source_metrics,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare SARIMAX backtests vs simple baselines.")
    parser.add_argument("--min-r2", type=float, default=0.0, help="Minimum acceptable R2 for PASS.")
    parser.add_argument("--json-out", type=str, default="", help="Optional path to save full JSON report.")
    args = parser.parse_args()

    report = []
    ok = 0
    check = 0

    for appliance in APPLIANCES:
        result = evaluate_appliance(appliance, min_r2=args.min_r2)
        report.append(result)
        if result["status"] == "PASS":
            ok += 1
        else:
            check += 1

        model = result["model"]
        impr = result["improvement_pct"]
        print(
            f"{appliance:12s} {result['status']:5s} | "
            f"MAE={model['MAE']:.6f} RMSE={model['RMSE']:.6f} R2={model['R2']:.4f} | "
            f"vs_mean(MAE/RMSE)={impr['vs_mean_MAE']:.2f}%/{impr['vs_mean_RMSE']:.2f}% | "
            f"vs_lag24(MAE/RMSE)={impr['vs_lag24_MAE']:.2f}%/{impr['vs_lag24_RMSE']:.2f}%"
        )

    summary = {
        "models_root": str(MODELS_ROOT),
        "min_r2_threshold": args.min_r2,
        "pass_count": ok,
        "check_count": check,
        "results": report,
    }

    if args.json_out:
        out_path = Path(args.json_out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print(f"\nSaved JSON report: {out_path}")

    print(f"\nSummary: PASS={ok}, CHECK={check}")


if __name__ == "__main__":
    main()
