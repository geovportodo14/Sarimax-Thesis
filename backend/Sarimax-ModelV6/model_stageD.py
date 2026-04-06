#!/usr/bin/env python3
"""
Stage 3.5.4 - Evaluation Plot Exporter

Summary:
This script reads the saved evaluation outputs for each appliance SARIMAX model
and exports a compact set of diagnostic plots together with a rounded
predictions CSV for easier review, interpretation, and reporting.

Input flow:
model/
  -> sarimax/
     -> <appliance_csv_stem>/
        -> evaluation/
           -> eval_predictions.csv
           -> eval_residual_heatmap.csv
           -> eval_hourly_error.csv      
           -> eval_dayofweek_error.csv         
           -> eval_weekend_error.csv           
           -> eval_peak_vs_nonpeak.json           
           -> eval_zero_vs_nonzero.json              
           -> eval_residual_vs_weather.csv      

Processing flow:
per-appliance evaluation outputs
  -> load scored prediction results
  -> validate required columns
  -> export rounded prediction CSV
  -> plot actual vs predicted line chart
  -> plot residuals over time
  -> plot residual histogram
  -> plot residual heatmap from saved heatmap CSV
  -> plot hourly error profile
  -> plot day-of-week error profile
  -> plot weekend vs weekday comparison
  -> plot peak vs non-peak comparison
  -> plot zero vs non-zero comparison
  -> plot residual vs temperature / humidity / rainfall if available

Output flow:
model/
  -> sarimax/
     -> <appliance_csv_stem>/
        -> plots/
           -> eval_predictions_rounded.csv
           -> plot_actual_vs_pred.png
           -> plot_residuals_over_time.png
           -> plot_residual_hist.png
           -> plot_residual_heatmap.png
           -> plot_daily_mae.png
           -> plot_daily_rmse.png
           -> plot_hourly_error_mae.png             
           -> plot_dayofweek_error_mae.png     
           -> plot_weekend_error_mae.png        
           -> plot_peak_vs_nonpeak_rmse.png          
           -> plot_zero_vs_nonzero_mae.png          
           -> plot_residual_vs_temperature.png       
           -> plot_residual_vs_humidity.png          
           -> plot_residual_vs_rainfall.png         
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import matplotlib.pyplot as plt
import pandas as pd


# =============================================================================
# Defaults
# =============================================================================

MODELS_ROOT = Path("model/sarimax")


# =============================================================================
# IO helpers
# =============================================================================

def read_eval_predictions(path: Path) -> pd.DataFrame:
    """
    Load the scored evaluation predictions for one appliance.
    """
    df = pd.read_csv(path)

    if "timestamp" not in df.columns:
        raise ValueError(f"{path}: missing timestamp")

    for col in ["actual_energy", "pred_energy"]:
        if col not in df.columns:
            raise ValueError(f"{path}: missing {col}")

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"]).sort_values("timestamp")
    return df


def read_csv_if_exists(path: Path) -> pd.DataFrame | None:
    """
    Load a CSV if it exists, otherwise return None.
    """
    if not path.exists():
        return None
    return pd.read_csv(path)


def read_json_if_exists(path: Path) -> Dict[str, Any] | None:
    """
    Load a JSON file if it exists, otherwise return None.
    """
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def save_plot(fig, outpath: Path) -> None:
    """
    Save one matplotlib figure and close it.
    """
    outpath.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(outpath, dpi=150)
    plt.close(fig)


def export_rounded_csv(df: pd.DataFrame, outpath: Path) -> None:
    """
    Export a rounded prediction CSV for easier viewing.
    """
    out = df[["timestamp", "actual_energy", "pred_energy"]].copy()
    out["actual_energy"] = out["actual_energy"].astype(float).round(4)
    out["pred_energy"] = out["pred_energy"].astype(float).round(4)
    out.to_csv(outpath, index=False)


# =============================================================================
# Plot helpers
# =============================================================================

def plot_actual_vs_pred(df: pd.DataFrame, outpath: Path) -> None:
    """
    Plot actual and predicted energy over time.
    """
    fig = plt.figure()
    plt.plot(df["timestamp"], df["actual_energy"], label="Actual")
    plt.plot(df["timestamp"], df["pred_energy"], label="Predicted")
    plt.title("Actual vs Predicted Energy (24h-ahead)")
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.legend()
    save_plot(fig, outpath)


def plot_residuals_over_time(df: pd.DataFrame, outpath: Path) -> None:
    """
    Plot residuals over time.
    """
    plot_df = df.copy()
    if "residual" not in plot_df.columns:
        plot_df["residual"] = plot_df["actual_energy"] - plot_df["pred_energy"]

    fig = plt.figure()
    plt.plot(plot_df["timestamp"], plot_df["residual"])
    plt.axhline(0.0)
    plt.title("Residuals Over Time (Actual - Predicted)")
    plt.xlabel("Timestamp")
    plt.ylabel("Residual (kWh)")
    save_plot(fig, outpath)


def plot_residual_hist(df: pd.DataFrame, outpath: Path) -> None:
    """
    Plot the residual distribution.
    """
    plot_df = df.copy()
    if "residual" not in plot_df.columns:
        plot_df["residual"] = plot_df["actual_energy"] - plot_df["pred_energy"]

    fig = plt.figure()
    plt.hist(plot_df["residual"].values, bins=40)
    plt.title("Residual Distribution")
    plt.xlabel("Residual (kWh)")
    plt.ylabel("Count")
    save_plot(fig, outpath)


def plot_residual_heatmap(heat_csv: Path, outpath: Path) -> None:
    """
    Plot the saved residual heatmap table.
    """
    heat = pd.read_csv(heat_csv, index_col=0)
    mat = heat.values.astype(float)

    fig = plt.figure()
    plt.imshow(mat, aspect="auto")
    plt.title("Residual Heatmap (date x hour_of_day)")
    plt.xlabel("Hour of Day")
    plt.ylabel("Date index")
    plt.colorbar(label="Mean residual (kWh)")
    save_plot(fig, outpath)


def plot_hourly_error(df: pd.DataFrame, outpath: Path) -> None:
    """
    Plot MAE by hour of day.
    """
    required = {"hour", "MAE"}
    if not required.issubset(df.columns):
        return

    fig = plt.figure()
    plt.plot(df["hour"], df["MAE"], marker="o")
    plt.title("Hourly Error Profile (MAE)")
    plt.xlabel("Hour of Day")
    plt.ylabel("MAE")
    plt.xticks(range(24))
    save_plot(fig, outpath)


def plot_dayofweek_error(df: pd.DataFrame, outpath: Path) -> None:
    """
    Plot MAE by day of week.
    """
    required = {"day_of_week", "MAE"}
    if not required.issubset(df.columns):
        return

    labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    fig = plt.figure()
    plt.plot(df["day_of_week"], df["MAE"], marker="o")
    plt.title("Day-of-Week Error Profile (MAE)")
    plt.xlabel("Day of Week")
    plt.ylabel("MAE")
    plt.xticks(range(7), labels)
    save_plot(fig, outpath)


def plot_weekend_error(df: pd.DataFrame, outpath: Path) -> None:
    """
    Plot MAE for weekday vs weekend.
    """
    required = {"is_weekend", "MAE"}
    if not required.issubset(df.columns):
        return

    plot_df = df.sort_values("is_weekend").copy()
    labels = ["Weekday" if int(x) == 0 else "Weekend" for x in plot_df["is_weekend"]]

    fig = plt.figure()
    plt.bar(labels, plot_df["MAE"])
    plt.title("Weekday vs Weekend Error (MAE)")
    plt.xlabel("Group")
    plt.ylabel("MAE")
    save_plot(fig, outpath)


def plot_peak_vs_nonpeak(metrics: Dict[str, Any], outpath: Path) -> None:
    """
    Plot RMSE for peak vs non-peak hours.
    """
    groups = metrics.get("groups", {})
    if not groups:
        return

    labels = []
    values = []

    for key in ["non_peak", "peak"]:
        if key in groups and "RMSE" in groups[key]:
            labels.append("Non-Peak" if key == "non_peak" else "Peak")
            values.append(groups[key]["RMSE"])

    if not labels:
        return

    fig = plt.figure()
    plt.bar(labels, values)
    plt.title("Peak vs Non-Peak Performance (RMSE)")
    plt.xlabel("Group")
    plt.ylabel("RMSE")
    save_plot(fig, outpath)


def plot_zero_vs_nonzero(metrics: Dict[str, Any], outpath: Path) -> None:
    """
    Plot MAE for zero-actual vs nonzero-actual hours.
    """
    groups = metrics.get("groups", {})
    if not groups:
        return

    labels = []
    values = []

    for key in ["zero_actual", "nonzero_actual"]:
        if key in groups and "MAE" in groups[key]:
            labels.append("Zero Actual" if key == "zero_actual" else "Nonzero Actual")
            values.append(groups[key]["MAE"])

    if not labels:
        return

    fig = plt.figure()
    plt.bar(labels, values)
    plt.title("Zero vs Nonzero Actual Performance (MAE)")
    plt.xlabel("Group")
    plt.ylabel("MAE")
    save_plot(fig, outpath)


def plot_residual_vs_weather(weather_csv: Path, weather_col: str, outpath: Path) -> None:
    """
    Plot residual against one weather variable if available.
    """
    df = pd.read_csv(weather_csv)
    if not {weather_col, "residual"}.issubset(df.columns):
        return

    fig = plt.figure()
    plt.scatter(df[weather_col].values, df["residual"].values, s=10)
    plt.title(f"Residual vs {weather_col.capitalize()}")
    plt.xlabel(weather_col.capitalize())
    plt.ylabel("Residual (kWh)")
    save_plot(fig, outpath)

def plot_daily_mae(df: pd.DataFrame, outpath: Path) -> None:
    """
    Plot daily MAE across the test period.
    Each point represents one 24-hour forecast block (per refit origin).
    """
    if not {"date", "MAE"}.issubset(df.columns):
        return

    plot_df = df.copy()
    plot_df["date"] = pd.to_datetime(plot_df["date"], errors="coerce")

    fig = plt.figure()
    plt.plot(plot_df["date"], plot_df["MAE"], marker="o")
    plt.title("Daily Forecast Error (MAE per 24h block)")
    plt.xlabel("Date")
    plt.ylabel("MAE")
    plt.xticks(rotation=45)
    save_plot(fig, outpath)

def plot_daily_rmse(df: pd.DataFrame, outpath: Path) -> None:
    if not {"date", "RMSE"}.issubset(df.columns):
        return

    plot_df = df.copy()
    plot_df["date"] = pd.to_datetime(plot_df["date"], errors="coerce")

    fig = plt.figure()
    plt.plot(plot_df["date"], plot_df["RMSE"], marker="o")
    plt.title("Daily Forecast Error (RMSE per 24h block)")
    plt.xlabel("Date")
    plt.ylabel("RMSE")
    plt.xticks(rotation=45)
    save_plot(fig, outpath)


# =============================================================================
# Main
# =============================================================================

def main() -> None:
    if not MODELS_ROOT.exists():
        raise FileNotFoundError(f"Models root not found: {MODELS_ROOT}")

    model_dirs = [
        path for path in MODELS_ROOT.iterdir()
        if path.is_dir() and not path.name.startswith("_")
    ]
    if not model_dirs:
        raise RuntimeError(f"No appliance model dirs found in {MODELS_ROOT}")

    for model_dir in sorted(model_dirs):
        eval_dir = model_dir / "evaluation"
        plots_dir = model_dir / "plots"
        plots_dir.mkdir(parents=True, exist_ok=True)

        pred_csv = eval_dir / "eval_predictions.csv"
        if not pred_csv.exists():
            print(f"[SKIP] Missing: {pred_csv}")
            continue

        print(f"[OK] Processing: {model_dir.name}")

        df = read_eval_predictions(pred_csv)

        export_rounded_csv(df, plots_dir / "eval_predictions_rounded.csv")
        plot_actual_vs_pred(df, plots_dir / "plot_actual_vs_pred.png")
        plot_residuals_over_time(df, plots_dir / "plot_residuals_over_time.png")
        plot_residual_hist(df, plots_dir / "plot_residual_hist.png")

        daily_metrics_csv = eval_dir / "eval_daily_metrics.csv"
        daily_metrics_df = read_csv_if_exists(daily_metrics_csv)
        if daily_metrics_df is not None:
            plot_daily_mae(
                daily_metrics_df,
                plots_dir / "plot_daily_mae.png",
            )
            plot_daily_rmse(
                daily_metrics_df,
                plots_dir / "plot_daily_rmse.png",
            )

        heat_csv = eval_dir / "eval_residual_heatmap.csv"
        if heat_csv.exists():
            plot_residual_heatmap(heat_csv, plots_dir / "plot_residual_heatmap.png")
        else:
            print(f"[WARN] Missing heatmap CSV: {heat_csv}")

        hourly_error_csv = eval_dir / "eval_hourly_error.csv"
        hourly_error_df = read_csv_if_exists(hourly_error_csv)
        if hourly_error_df is not None:
            plot_hourly_error(hourly_error_df, plots_dir / "plot_hourly_error_mae.png")

        dayofweek_error_csv = eval_dir / "eval_dayofweek_error.csv"
        dayofweek_error_df = read_csv_if_exists(dayofweek_error_csv)
        if dayofweek_error_df is not None:
            plot_dayofweek_error(dayofweek_error_df, plots_dir / "plot_dayofweek_error_mae.png")

        weekend_error_csv = eval_dir / "eval_weekend_error.csv"
        weekend_error_df = read_csv_if_exists(weekend_error_csv)
        if weekend_error_df is not None:
            plot_weekend_error(weekend_error_df, plots_dir / "plot_weekend_error_mae.png")

        peak_vs_nonpeak_json = eval_dir / "eval_peak_vs_nonpeak.json"
        peak_vs_nonpeak = read_json_if_exists(peak_vs_nonpeak_json)
        if peak_vs_nonpeak is not None:
            plot_peak_vs_nonpeak(
                peak_vs_nonpeak,
                plots_dir / "plot_peak_vs_nonpeak_rmse.png",
            )

        zero_vs_nonzero_json = eval_dir / "eval_zero_vs_nonzero.json"
        zero_vs_nonzero = read_json_if_exists(zero_vs_nonzero_json)
        if zero_vs_nonzero is not None:
            plot_zero_vs_nonzero(
                zero_vs_nonzero,
                plots_dir / "plot_zero_vs_nonzero_mae.png",
            )

        weather_csv = eval_dir / "eval_residual_vs_weather.csv"
        if weather_csv.exists():
            plot_residual_vs_weather(
                weather_csv,
                "temperature",
                plots_dir / "plot_residual_vs_temperature.png",
            )
            plot_residual_vs_weather(
                weather_csv,
                "humidity",
                plots_dir / "plot_residual_vs_humidity.png",
            )
            plot_residual_vs_weather(
                weather_csv,
                "rainfall",
                plots_dir / "plot_residual_vs_rainfall.png",
            )

    print("[DONE] Plots and rounded CSVs created.")


if __name__ == "__main__":
    main()