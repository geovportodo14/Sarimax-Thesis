"""
forecasting/pipeline/viz.py
=============================
Automated visualization for SARIMAX forecasts.
"""

from __future__ import annotations

import logging
import os
from datetime import timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import matplotlib.pyplot as plt
import pandas as pd

log = logging.getLogger("sarimax_pipeline.viz")
MANILA_TZ = ZoneInfo("Asia/Manila")


def _to_manila_timestamp(value: object) -> pd.Timestamp:
    """Parse any value to a Manila-localized timestamp."""
    ts = pd.to_datetime(value, errors="coerce")
    if pd.isna(ts):
        return pd.NaT
    if ts.tzinfo is None:
        # Keep parity with pipeline history loader behavior.
        ts = ts.tz_localize("UTC")
    return ts.tz_convert(MANILA_TZ)


def _infer_step_hours(local_ts: list[pd.Timestamp]) -> float:
    """
    Infer sampling interval in hours using median timestamp delta.
    Falls back to 10-minute cadence when insufficient data is present.
    """
    if len(local_ts) < 2:
        return 1.0 / 6.0

    ordered = sorted(local_ts)
    deltas = []
    for prev, curr in zip(ordered, ordered[1:]):
        dt_h = (curr - prev).total_seconds() / 3600.0
        if dt_h > 0:
            deltas.append(dt_h)

    if not deltas:
        return 1.0 / 6.0

    step = float(pd.Series(deltas).median())
    # Prevent malformed timestamps from exploding energy conversion.
    return min(max(step, 1.0 / 60.0), 1.0)


def _load_actual_series(col, forecast_date: str) -> tuple[pd.Series | None, int]:
    """
    Build hourly aggregated actual energy (kWh) for forecast_date.
    Missing hours are returned as NaN (not forced to zero).
    """
    target_day = pd.Timestamp(forecast_date).date()
    prev_day = (pd.Timestamp(forecast_date) - timedelta(days=1)).strftime("%Y-%m-%d")
    next_day = (pd.Timestamp(forecast_date) + timedelta(days=1)).strftime("%Y-%m-%d")

    # Query neighboring dates to absorb timezone/date-field edge cases.
    docs = list(col.find({"date": {"$gte": prev_day, "$lte": next_day}}, {"readings": 1}))
    if not docs:
        return None, 0

    hourly_actuals = {h: 0.0 for h in range(24)}
    hourly_counts = {h: 0 for h in range(24)}

    for doc in docs:
        readings = doc.get("readings", [])
        local_ts = []
        valid_rows: list[tuple[pd.Timestamp, float]] = []

        for r in readings:
            ts_local = _to_manila_timestamp(r.get("timestamp"))
            if pd.isna(ts_local) or ts_local.date() != target_day:
                continue

            power_w = r.get("processed_data", {}).get("power_w")
            try:
                power_w = float(power_w)
            except (TypeError, ValueError):
                continue

            local_ts.append(ts_local)
            valid_rows.append((ts_local, power_w))

        if not valid_rows:
            continue

        step_h = _infer_step_hours(local_ts)
        for ts_local, power_w in valid_rows:
            h = int(ts_local.hour)
            hourly_actuals[h] += (power_w / 1000.0) * step_h
            hourly_counts[h] += 1

    values = {
        h: (hourly_actuals[h] if hourly_counts[h] > 0 else float("nan"))
        for h in range(24)
    }
    series = pd.Series(values, dtype=float)
    covered = int(series.notna().sum())
    return series, covered


def generate_forecast_plot(outputs_dir: Path, forecast_date: str, appliances: list[str]) -> str:
    """
    Generates a combined plot for the given forecast date and appliances.
    Supports 'Actual vs Forecast' comparison if historical data is available.
    """
    from pymongo import MongoClient
    from forecasting.config import HISTORY_COLLECTION, MONGO_DB, MONGO_URI

    date_dir = outputs_dir / forecast_date
    if not date_dir.exists():
        log.warning("Output directory %s does not exist. Skipping plot.", date_dir)
        return ""

    # COLORS matching UI
    color_actual = "#0284C7"
    color_forecast = "#FF6B00"
    colors_sub = ["#10B981", "#6366F1", "#F43F5E"]

    plt.figure(figsize=(12, 7))
    found_any = False

    # 1. Fetch actuals for this date
    actual_series = None
    actual_covered_hours = 0
    fetch_actuals = (
        os.getenv("VIZ_FETCH_ACTUALS", os.getenv("SAVE_MONGO", "true"))
        .strip()
        .lower()
        == "true"
    )

    if fetch_actuals:
        client = None
        try:
            client = MongoClient(
                MONGO_URI,
                serverSelectionTimeoutMS=2000,
                connectTimeoutMS=2000,
                socketTimeoutMS=2000,
            )
            col = client[MONGO_DB][HISTORY_COLLECTION]
            actual_series, actual_covered_hours = _load_actual_series(col, forecast_date)
        except Exception as exc:
            log.warning("Could not fetch actuals for viz: %s", exc)
        finally:
            if client is not None:
                client.close()
    else:
        log.info("Skipping actuals fetch for visualization (VIZ_FETCH_ACTUALS/SAVE_MONGO=false).")

    # 2. Gather forecasts
    all_forecasts = {h: 0.0 for h in range(24)}
    individual_plots: list[tuple[str, pd.DataFrame]] = []

    for i, appliance in enumerate(appliances):
        _ = i
        csv_path = date_dir / f"{appliance}_forecast.csv"
        if not csv_path.exists():
            continue
        try:
            df = pd.read_csv(csv_path)
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
            df = df.dropna(subset=["timestamp"])
            df["hour"] = df["timestamp"].dt.hour
            for _, row in df.iterrows():
                all_forecasts[int(row["hour"])] += float(row["predicted_energy"])
            individual_plots.append((appliance, df))
            found_any = True
        except Exception as exc:
            log.error("Failed to plot %s: %s", appliance, exc)

    if not found_any:
        plt.close()
        return ""

    # 3. Render plot
    ax = plt.gca()
    if actual_series is not None and actual_covered_hours > 0:
        x_actual = actual_series.index.tolist()
        y_actual = actual_series.values
        valid_mask = pd.Series(y_actual).notna().values

        plt.plot(
            x_actual,
            y_actual,
            label="Actual Total",
            color=color_actual,
            linewidth=4,
            marker="o",
            markersize=8,
        )
        plt.plot(
            list(all_forecasts.keys()),
            list(all_forecasts.values()),
            label="Forecast Total",
            color=color_forecast,
            linewidth=4,
            linestyle="--",
            marker="s",
            markersize=8,
        )
        plt.fill_between(
            x_actual,
            y_actual,
            where=valid_mask,
            color=color_actual,
            alpha=0.1,
        )
        plt.fill_between(
            list(all_forecasts.keys()),
            list(all_forecasts.values()),
            color=color_forecast,
            alpha=0.05,
        )

        coverage_note = ""
        if actual_covered_hours < 24:
            coverage_note = f" [Partial Actuals: {actual_covered_hours}/24h]"

        plt.title(
            f"Aggregated Performance: Actual vs Forecast ({forecast_date}){coverage_note}",
            fontsize=18,
            fontweight="bold",
            pad=25,
        )
    else:
        for i, (app, df) in enumerate(individual_plots):
            color = colors_sub[i % len(colors_sub)]
            plt.plot(
                df["hour"],
                df["predicted_energy"],
                label=f"{app.capitalize()} Forecast",
                color=color,
                linewidth=2.5,
                marker="o",
                alpha=0.9,
            )
        plt.title(f"Forecast Breakdown: {forecast_date}", fontsize=18, fontweight="bold", pad=25)

    plt.xlabel("Hour of Day (Local Time)", fontsize=13, labelpad=10)
    plt.ylabel("Energy Usage (kWh)", fontsize=13, labelpad=10)
    plt.xticks(range(0, 24))
    plt.grid(True, linestyle=":", alpha=0.5)
    plt.legend(frameon=True, shadow=True, borderpad=1, fontsize=11)
    ax.set_facecolor("#fefefe")
    plt.tight_layout()

    plot_path = date_dir / "forecast_comparison.png"
    plt.savefig(plot_path, dpi=200, bbox_inches="tight")
    plt.close()

    log.info("Forecast plot updated: %s", plot_path)
    return str(plot_path)
