"""
forecasting/pipeline/viz.py
=============================
Automated visualization for SARIMAX forecasts.
"""

import pandas as pd
import matplotlib.pyplot as plt
import os
from pathlib import Path
import logging

log = logging.getLogger("sarimax_pipeline.viz")

def generate_forecast_plot(outputs_dir: Path, forecast_date: str, appliances: list) -> str:
    """
    Generates a combined plot for the given forecast date and appliances.
    Supports 'Actual vs Forecast' comparison if historical data is available.
    """
    from pymongo import MongoClient
    from forecasting.config import MONGO_URI, MONGO_DB, HISTORY_COLLECTION
    
    date_dir = outputs_dir / forecast_date
    if not date_dir.exists():
        log.warning(f"Output directory {date_dir} does not exist. Skipping plot.")
        return ""

    # COLORS matching UI
    COLOR_ACTUAL = '#0284C7'
    COLOR_FORECAST = '#FF6B00'
    COLORS_SUB = ['#10B981', '#6366F1', '#F43F5E']

    plt.figure(figsize=(12, 7))
    found_any = False
    
    # 1. Fetch Actuals for this specific date (if they exist)
    actual_series = None
    try:
        client = MongoClient(MONGO_URI)
        col = client[MONGO_DB][HISTORY_COLLECTION]
        
        # Aggregate all appliances for this date
        cursor = col.find({"date": forecast_date}, {"readings": 1})
        docs = list(cursor)
        
        if docs:
            hourly_actuals = {h: 0.0 for h in range(24)}
            for doc in docs:
                for r in doc.get("readings", []):
                    ts = pd.to_datetime(r["timestamp"])
                    if ts.tzinfo:
                        ts = ts.tz_convert("Asia/Manila")
                    h = ts.hour
                    hourly_actuals[h] += (r["processed_data"]["power_w"] / 1000.0) / 6.0
            
            actual_series = pd.Series(hourly_actuals)
    except Exception as e:
        log.warning(f"Could not fetch actuals for viz: {e}")

    # 2. Gather Forecasts
    all_forecasts = {h: 0.0 for h in range(24)}
    individual_plots = []
    
    for i, appliance in enumerate(appliances):
        csv_path = date_dir / f"{appliance}_forecast.csv"
        if csv_path.exists():
            try:
                df = pd.read_csv(csv_path)
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['hour'] = df['timestamp'].dt.hour
                for _, row in df.iterrows():
                    all_forecasts[int(row['hour'])] += row['predicted_energy']
                individual_plots.append((appliance, df))
                found_any = True
            except Exception as e:
                log.error(f"Failed to plot {appliance}: {e}")

    if not found_any:
        plt.close()
        return ""

    # 3. Render Plot
    ax = plt.gca()
    if actual_series is not None and actual_series.sum() > 0:
        plt.plot(actual_series.index, actual_series.values, label='Actual Total', 
                 color=COLOR_ACTUAL, linewidth=4, marker='o', markersize=8)
        plt.plot(list(all_forecasts.keys()), list(all_forecasts.values()), label='Forecast Total', 
                 color=COLOR_FORECAST, linewidth=4, linestyle='--', marker='s', markersize=8)
        plt.fill_between(actual_series.index, actual_series.values, color=COLOR_ACTUAL, alpha=0.1)
        plt.fill_between(list(all_forecasts.keys()), list(all_forecasts.values()), color=COLOR_FORECAST, alpha=0.05)
        plt.title(f"Aggregated Performance: Actual vs Forecast ({forecast_date})", fontsize=18, fontweight='bold', pad=25)
    else:
        for i, (app, df) in enumerate(individual_plots):
            color = COLORS_SUB[i % len(COLORS_SUB)]
            plt.plot(df['hour'], df['predicted_energy'], label=f"{app.capitalize()} Forecast", 
                     color=color, linewidth=2.5, marker='o', alpha=0.9)
        plt.title(f"Forecast Breakdown: {forecast_date}", fontsize=18, fontweight='bold', pad=25)

    plt.xlabel("Hour of Day (Local Time)", fontsize=13, labelpad=10)
    plt.ylabel("Energy Usage (kWh)", fontsize=13, labelpad=10)
    plt.xticks(range(0, 24))
    plt.grid(True, linestyle=':', alpha=0.5)
    plt.legend(frameon=True, shadow=True, borderpad=1, fontsize=11)
    ax.set_facecolor('#fefefe')
    plt.tight_layout()

    plot_path = date_dir / "forecast_comparison.png"
    plt.savefig(plot_path, dpi=200, bbox_inches='tight')
    plt.close()
    
    log.info(f"Forecast plot updated: {plot_path}")
    return str(plot_path)
