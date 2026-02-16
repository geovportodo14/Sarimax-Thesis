# Stage 3.3.4 — Final Data Transformation (Modeling-Ready Dataset)

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

@dataclass
class Stage334Config:
    timezone: str = "Asia/Manila"
    drop_rows_with_missing_target: bool = True
    min_history_hours_required: int = 168
    enforce_full_features: bool = False 

    ts_col_hour: str = "hour_ts"
    device_col: str = "device_id"
    target_col_hour: str = "e_hour_kwh"  
    weather_cols: List[str] = None

    def __post_init__(self):
        if self.weather_cols is None:
            self.weather_cols = ["temperature", "humidity", "pressure"] # Changed 'rainfall' to 'pressure'

def _ensure_datetime_tz(df: pd.DataFrame, col: str, tz: str) -> pd.DataFrame:
    df = df.copy()
    df[col] = pd.to_datetime(df[col], format="ISO8601", errors="coerce")
    if getattr(df[col].dt, "tz", None) is None:
        df[col] = df[col].dt.tz_localize(tz, nonexistent="shift_forward", ambiguous="NaT")
    else:
        df[col] = df[col].dt.tz_convert(tz)
    return df


def _standardize_day_of_week_1_to_7(df: pd.DataFrame, ts_col: str) -> pd.Series:
    return df[ts_col].dt.dayofweek + 1

# A. Weather Synchronization

def synchronize_energy_weather(hourly_features_df: pd.DataFrame, cfg: Stage334Config) -> pd.DataFrame:

    df = hourly_features_df.copy()
    df = _ensure_datetime_tz(df, cfg.ts_col_hour, cfg.timezone)

    required = [
        cfg.device_col, cfg.ts_col_hour, cfg.target_col_hour,
        "hour_of_day", "day_of_week", "is_weekend", "is_holiday",
        "lag_24", "lag_168", "rolling_mean_24", "rolling_mean_168"
    ] + cfg.weather_cols

    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Stage 3.3.3 hourly_features_df missing required columns: {missing}")

    for c in cfg.weather_cols:
        if df[c].isna().any():
            tmp = df[[cfg.ts_col_hour, c]].drop_duplicates(subset=[cfg.ts_col_hour]).sort_values(cfg.ts_col_hour)
            tmp = tmp.set_index(cfg.ts_col_hour)
            tmp[c] = tmp[c].interpolate(method="time")
            tmp = tmp.reset_index()

            df = df.drop(columns=[c]).merge(tmp, on=cfg.ts_col_hour, how="left")

    return df

# B. Final Variable Structure for Modeling

def check_daily_completeness(df: pd.DataFrame, cfg: Stage334Config, expected_hourly: int = 24) -> pd.DataFrame:
    """
    Check daily data completeness and return a report.
    
    Args:
        df: DataFrame with hourly data (must have cfg.ts_col_hour column)
        cfg: Stage334Config with device_col and timezone settings
        expected_hourly: Expected number of hourly readings per day (default: 24)
    
    Returns:
        DataFrame with daily completeness report
    """
    d = df.copy()
    
    # Ensure timezone-aware timestamps using the correct column name
    d = _ensure_datetime_tz(d, cfg.ts_col_hour, cfg.timezone)
    
    # Extract date in PH timezone
    d["date"] = d[cfg.ts_col_hour].dt.tz_convert(cfg.timezone).dt.date
    
    # Count readings per day per device
    daily_counts = d.groupby([cfg.device_col, "date"]).size().reset_index(name="count")
    daily_counts["expected"] = expected_hourly
    daily_counts["complete"] = daily_counts["count"] >= expected_hourly
    daily_counts["completeness_pct"] = (daily_counts["count"] / daily_counts["expected"] * 100).round(2)
    daily_counts["status"] = daily_counts.apply(
        lambda r: "Complete" if r["complete"] else f"Incomplete ({r['count']}/{r['expected']})",
        axis=1
    )
    
    return daily_counts


def build_modeling_ready_dataset(df_sync: pd.DataFrame, cfg: Stage334Config) -> pd.DataFrame:
    df = df_sync.copy()

    df = df.rename(columns={
        cfg.ts_col_hour: "timestamp",
        cfg.target_col_hour: "kWh"
    })

    df = _ensure_datetime_tz(df, "timestamp", cfg.timezone)
    df = df.sort_values([cfg.device_col, "timestamp"]).reset_index(drop=True)

    if df["day_of_week"].dropna().between(0, 6).all():
        df["day_of_week"] = _standardize_day_of_week_1_to_7(df, "timestamp")

    final_cols = [
        cfg.device_col,
        "timestamp",
        "kWh",
        "temperature", "humidity", "pressure", # Changed 'rainfall' to 'pressure'
        "hour_of_day", "day_of_week", "is_weekend", "is_holiday",
        "lag_24", "lag_168",
        "rolling_mean_24", "rolling_mean_168"
    ]
    out = df[final_cols].copy()

    if cfg.drop_rows_with_missing_target:
        out = out.dropna(subset=["kWh"])

    if cfg.enforce_full_features:
        out = out.dropna(subset=[
            "temperature", "humidity", "pressure", # Changed 'rainfall' to 'pressure'
            "lag_24", "lag_168", "rolling_mean_24", "rolling_mean_168"
        ])

    if cfg.min_history_hours_required is not None and cfg.min_history_hours_required > 0:
        gated = []
        for dev, g in out.groupby(cfg.device_col):
            g = g.sort_values("timestamp")
            first_valid = g["lag_168"].first_valid_index()
            if first_valid is None:
                gated.append(g)
                continue
            start_ts = g.loc[first_valid, "timestamp"]
            gated.append(g[g["timestamp"] >= start_ts])
        out = pd.concat(gated, ignore_index=True)

    # Normalize timezone display: keep PH time values but remove timezone suffix for cleaner CSV
    # This makes timestamps display as "2026-01-03 15:56:00" instead of "2026-01-03 15:56:00+08:00"
    out["timestamp"] = out["timestamp"].dt.tz_convert(cfg.timezone).dt.tz_localize(None)

    return out


def export_per_appliance(df_model: pd.DataFrame, output_dir: str, cfg: Stage334Config) -> Dict[str, str]:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    paths = {}
    for dev, g in df_model.groupby(cfg.device_col):
        g = g.sort_values("timestamp").reset_index(drop=True)
        path = out_dir / f"model_ready_{dev}.csv"
        g.to_csv(path, index=False)
        paths[str(dev)] = str(path)
    return paths

# Stage Runner

def stage_334_final_transformation(
    hourly_features_stage333_path: str,
    output_dir: str = "out/model_ready",
    cfg: Stage334Config = Stage334Config()
) -> Dict[str, object]:
    df = pd.read_csv(hourly_features_stage333_path)

    if cfg.ts_col_hour not in df.columns:
        raise ValueError(f"Expected '{cfg.ts_col_hour}' in hourly features file.")

    df_sync = synchronize_energy_weather(df, cfg)
    
    # Generate daily completeness report before final transformation
    completeness_report = check_daily_completeness(df_sync, cfg, expected_hourly=24)
    
    df_model = build_modeling_ready_dataset(df_sync, cfg)
    per_device_paths = export_per_appliance(df_model, output_dir, cfg)
    
    # Save completeness report
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    completeness_path = out_dir / "daily_completeness_report.csv"
    completeness_report.to_csv(completeness_path, index=False)
    
    print(f"\n📊 Daily Completeness Report:")
    print(f"   Saved to: {completeness_path}")
    print(f"\n   Summary:")
    complete_days = completeness_report["complete"].sum()
    total_days = len(completeness_report)
    print(f"   - Complete days: {complete_days}/{total_days} ({complete_days/total_days*100:.1f}%)")
    
    incomplete = completeness_report[~completeness_report["complete"]]
    if not incomplete.empty:
        print(f"   - Incomplete days: {len(incomplete)}")
        print(f"\n   ⚠️  Incomplete days details:")
        for _, row in incomplete.head(10).iterrows():
            print(f"      {row['device_id']} on {row['date']}: {row['count']}/{row['expected']} readings ({row['completeness_pct']:.1f}%)")
        if len(incomplete) > 10:
            print(f"      ... and {len(incomplete) - 10} more incomplete days")

    return {
        "df_model_ready": df_model, 
        "per_device_paths": per_device_paths,
        "completeness_report": completeness_report,
        "completeness_path": str(completeness_path)
    }

# Example usage
# if __name__ == "__main__":
#     result = stage_334_final_transformation(
#         hourly_features_stage333_path="out/hourly_features_stage333.csv",
#         output_dir="out/model_ready"
#     )

#     print("Created modeling-ready datasets:")
#     for dev, path in result["per_device_paths"].items():
#         print(f"- {dev}: {path}")
