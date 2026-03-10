#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

MODELS_ROOT = Path("model/stageB/sarimax")  


def _read_eval_predictions(p: Path) -> pd.DataFrame:
    df = pd.read_csv(p)
    # expected columns: timestamp, actual_energy, pred_energy, residual
    if "timestamp" not in df.columns:
        raise ValueError(f"{p}: missing timestamp")
    for c in ["actual_energy", "pred_energy"]:
        if c not in df.columns:
            raise ValueError(f"{p}: missing {c}")

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"]).sort_values("timestamp")
    return df


def _save_plot(fig, outpath: Path) -> None:
    outpath.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(outpath, dpi=150)
    plt.close(fig)


def plot_actual_vs_pred(df: pd.DataFrame, outpath: Path) -> None:
    fig = plt.figure()
    plt.plot(df["timestamp"], df["actual_energy"], label="Actual")
    plt.plot(df["timestamp"], df["pred_energy"], label="Predicted")
    plt.title("Actual vs Predicted Energy (24h-ahead)")
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.legend()
    _save_plot(fig, outpath)


def plot_residuals_over_time(df: pd.DataFrame, outpath: Path) -> None:
    if "residual" not in df.columns:
        df["residual"] = df["actual_energy"] - df["pred_energy"]

    fig = plt.figure()
    plt.plot(df["timestamp"], df["residual"])
    plt.axhline(0.0)
    plt.title("Residuals Over Time (Actual - Predicted)")
    plt.xlabel("Timestamp")
    plt.ylabel("Residual (kWh)")
    _save_plot(fig, outpath)


def plot_residual_hist(df: pd.DataFrame, outpath: Path) -> None:
    if "residual" not in df.columns:
        df["residual"] = df["actual_energy"] - df["pred_energy"]

    fig = plt.figure()
    plt.hist(df["residual"].values, bins=40)
    plt.title("Residual Distribution")
    plt.xlabel("Residual (kWh)")
    plt.ylabel("Count")
    _save_plot(fig, outpath)


def plot_residual_heatmap(heat_csv: Path, outpath: Path) -> None:
    heat = pd.read_csv(heat_csv, index_col=0)
    # columns are hours 0..23 (as strings), index are dates
    mat = heat.values.astype(float)

    fig = plt.figure()
    plt.imshow(mat, aspect="auto")
    plt.title("Residual Heatmap (date x hour_of_day)")
    plt.xlabel("Hour of Day")
    plt.ylabel("Date index")
    plt.colorbar(label="Mean residual (kWh)")
    _save_plot(fig, outpath)


def plot_residual_vs_temperature(rvst_csv: Path, outpath: Path) -> None:
    df = pd.read_csv(rvst_csv)
    if not {"temperature", "residual"}.issubset(df.columns):
        return

    fig = plt.figure()
    plt.scatter(df["temperature"].values, df["residual"].values, s=10)
    plt.title("Residual vs Temperature")
    plt.xlabel("Temperature")
    plt.ylabel("Residual (kWh)")
    _save_plot(fig, outpath)


def export_rounded_csv(df: pd.DataFrame, outpath: Path) -> None:
    out = df[["timestamp", "actual_energy", "pred_energy"]].copy()
    out["actual_energy"] = out["actual_energy"].astype(float).round(4)
    out["pred_energy"] = out["pred_energy"].astype(float).round(4)
    out.to_csv(outpath, index=False)


def main() -> None:
    if not MODELS_ROOT.exists():
        raise FileNotFoundError(f"Models root not found: {MODELS_ROOT}")

    model_dirs = [p for p in MODELS_ROOT.iterdir() if p.is_dir() and not p.name.startswith("_")]
    if not model_dirs:
        raise RuntimeError(f"No appliance model dirs found in {MODELS_ROOT}")

    for d in sorted(model_dirs):
        eval_dir = d / "evaluation"
        plots_dir = d / "plots"

        plots_dir.mkdir(parents=True, exist_ok=True)

        pred_csv = eval_dir / "eval_predictions.csv"
        if not pred_csv.exists():
            print(f"[SKIP] Missing: {pred_csv}")
            continue

        print(f"[OK] Processing: {d.name}")

        df = _read_eval_predictions(pred_csv)


        export_rounded_csv(df, plots_dir / "eval_predictions_rounded4.csv")

        # 1) Actual vs Predicted curve (line chart)
        plot_actual_vs_pred(df, plots_dir / "plot_actual_vs_pred.png")

        # ++ line charts (residuals over time)
        plot_residuals_over_time(df, plots_dir / "plot_residuals_over_time.png")

        # 2) Residual distribution
        plot_residual_hist(df, plots_dir / "plot_residual_hist.png")

        # 3) Residual heatmap by hour of day
        heat_csv = eval_dir / "eval_residual_heatmap.csv"
        if heat_csv.exists():
            plot_residual_heatmap(heat_csv, plots_dir / "plot_residual_heatmap.png")
        else:
            print(f"[WARN] Missing heatmap CSV: {heat_csv}")

        # residual vs temperature scatter
        rvst_csv = eval_dir / "eval_residual_vs_temperature.csv"
        if rvst_csv.exists():
            plot_residual_vs_temperature(rvst_csv, plots_dir / "plot_residual_vs_temperature.png")

    print("[DONE] Plots + rounded CSVs created.")


if __name__ == "__main__":
    main()