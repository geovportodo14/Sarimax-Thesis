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
            self.weather_cols = ["temperature", "humidity", "rainfall"]

def _ensure_datetime_tz(df: pd.DataFrame, col: str, tz: str) -> pd.DataFrame:
    df = df.copy()
    df[col] = pd.to_datetime(df[col], errors="coerce")
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
        "temperature", "humidity", "rainfall",
        "hour_of_day", "day_of_week", "is_weekend", "is_holiday",
        "lag_24", "lag_168",
        "rolling_mean_24", "rolling_mean_168"
    ]
    out = df[final_cols].copy()

    if cfg.drop_rows_with_missing_target:
        out = out.dropna(subset=["kWh"])

    if cfg.enforce_full_features:
        out = out.dropna(subset=[
            "temperature", "humidity", "rainfall",
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
    df_model = build_modeling_ready_dataset(df_sync, cfg)
    per_device_paths = export_per_appliance(df_model, output_dir, cfg)

    return {"df_model_ready": df_model, "per_device_paths": per_device_paths}

# Example usage
# if __name__ == "__main__":
#     result = stage_334_final_transformation(
#         hourly_features_stage333_path="out/hourly_features_stage333.csv",
#         output_dir="out/model_ready"
#     )

#     print("Created modeling-ready datasets:")
#     for dev, path in result["per_device_paths"].items():
#         print(f"- {dev}: {path}")
