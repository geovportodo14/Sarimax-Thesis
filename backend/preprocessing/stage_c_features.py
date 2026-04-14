# Stage 3.3.3 — Data Aggregation and Feature Construction

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple, Dict

import numpy as np
import pandas as pd

@dataclass
class Stage333Config:
    hourly_recon_tol_pct: float = 5.0

    temp_min_c: float = -10.0
    temp_max_c: float = 45.0
    humidity_min: float = 0.0 
    humidity_max: float = 100.0
    rainfall_min_mm: float = 0.0 # Changed from pressure
    rainfall_max_mm: float = 500.0 # Added max for rainfall

    temp_jump_c: float = 5.0
    humidity_jump_pct: float = 20.0

    lag_24: int = 24
    lag_168: int = 168
    roll_24: int = 24
    roll_168: int = 168

def _ensure_datetime_tz(df: pd.DataFrame, col: str = "timestamp") -> pd.DataFrame:
    df = df.copy()
    df[col] = pd.to_datetime(df[col], format="ISO8601", errors="coerce")
    if getattr(df[col].dt, "tz", None) is None:
        df[col] = df[col].dt.tz_localize("Asia/Manila", nonexistent="shift_forward", ambiguous="NaT")
    else:
        df[col] = df[col].dt.tz_convert("Asia/Manila")
    return df


def _tag_append(existing: str, new_tag: str) -> str:
    if not existing:
        return new_tag
    if new_tag in existing.split("|"):
        return existing
    return existing + "|" + new_tag


def _safe_pct_dev(numer: float, denom: float) -> float:
    """|numer-denom| / denom * 100; returns NaN if denom is 0/NaN."""
    if denom is None or pd.isna(denom) or abs(denom) < 1e-12:
        return np.nan
    return abs(numer - denom) / abs(denom) * 100.0

# A. Hourly Resampling 

def hourly_resample_energy(df_10min: pd.DataFrame, cfg: Stage333Config) -> pd.DataFrame:

    d = df_10min.copy()
    if "e_final_kwh" not in d.columns:
        raise ValueError("Stage 3.3.2 output must include 'e_final_kwh'.")

    d = d.sort_values(["device_id", "timestamp"]).reset_index(drop=True)

    d["hour_ts"] = d["timestamp"].dt.floor("h")

    hourly_sum = d.groupby(["device_id", "hour_ts"], as_index=False)["e_final_kwh"].sum()
    hourly_sum = hourly_sum.rename(columns={"e_final_kwh": "e_hour_kwh"})

    cum = d.groupby(["device_id", "hour_ts"]).agg(
        kwh_start=("kwh_total", "first"),
        kwh_end=("kwh_total", "last")
    ).reset_index()
    cum["kwh_net"] = (cum["kwh_end"] - cum["kwh_start"]).clip(lower=0)

    hourly = hourly_sum.merge(cum, on=["device_id", "hour_ts"], how="left")

    hourly["recon_dev_pct"] = hourly.apply(lambda r: _safe_pct_dev(r["e_hour_kwh"], r["kwh_net"]), axis=1)
    hourly["hour_tags"] = ""

    bad = hourly["recon_dev_pct"].notna() & (hourly["recon_dev_pct"] > cfg.hourly_recon_tol_pct)
    hourly.loc[bad, "hour_tags"] = hourly.loc[bad, "hour_tags"].apply(lambda x: _tag_append(x, "HOURLY_RECON_GT_5PCT"))

    return hourly

# B. Weather validation

def validate_and_clean_weather(weather_df: pd.DataFrame, cfg: Stage333Config) -> Tuple[pd.DataFrame, pd.DataFrame]:
    wx = weather_df.copy()
    wx = _ensure_datetime_tz(wx, "timestamp")
    wx = wx.sort_values("timestamp").reset_index(drop=True)

    wx["hour_ts"] = wx["timestamp"].dt.floor("h")

    wx_h = wx.groupby("hour_ts", as_index=False).agg(
        temperature=("temperature", "mean"),
        humidity=("humidity", "mean"),
        rainfall=("rainfall", "mean") # Changed from 'pressure'
    )

    wx_h["wx_tags"] = ""
    flags = []

    t_bad = (wx_h["temperature"] < cfg.temp_min_c) | (wx_h["temperature"] > cfg.temp_max_c)
    h_bad = (wx_h["humidity"] <= cfg.humidity_min) | (wx_h["humidity"] > cfg.humidity_max)
    r_bad = (wx_h["rainfall"] < cfg.rainfall_min_mm) | (wx_h["rainfall"] > cfg.rainfall_max_mm) # Changed from p_bad

    def _flag(mask: pd.Series, code: str, col: str):
        if mask.any():
            tmp = wx_h.loc[mask, ["hour_ts", col]].copy()
            tmp["flag"] = code
            tmp["variable"] = col
            flags.append(tmp)

    _flag(t_bad, "WX_RANGE_TEMP", "temperature")
    _flag(h_bad, "WX_RANGE_HUM", "humidity")
    _flag(r_bad, "WX_RANGE_RAIN", "rainfall") # Changed from WX_RANGE_PRES

    wx_h.loc[t_bad, "temperature"] = np.nan
    wx_h.loc[h_bad, "humidity"] = np.nan
    wx_h.loc[r_bad, "rainfall"] = np.nan # Changed from pressure

    wx_h = wx_h.set_index("hour_ts")
    wx_h[["temperature", "humidity", "rainfall"]] = wx_h[["temperature", "humidity", "rainfall"]].interpolate(method="time") # Changed from pressure
    wx_h = wx_h.reset_index()

    wx_h = wx_h.sort_values("hour_ts").reset_index(drop=True)
    wx_h["temp_delta"] = wx_h["temperature"].diff()
    wx_h["hum_delta"] = wx_h["humidity"].diff()
    wx_h["rain_delta"] = wx_h["rainfall"].diff() # Added for rainfall

    temp_jump = wx_h["temp_delta"].abs() > cfg.temp_jump_c
    hum_jump = wx_h["hum_delta"].abs() > cfg.humidity_jump_pct
    # No jump check for pressure, typically not as erratic

    _flag(temp_jump, "WX_JUMP_TEMP", "temperature")
    _flag(hum_jump, "WX_JUMP_HUM", "humidity")

    wx_h.loc[temp_jump, "temperature"] = np.nan
    wx_h.loc[hum_jump, "humidity"] = np.nan

    wx_h = wx_h.set_index("hour_ts")
    wx_h[["temperature", "humidity", "rainfall"]] = wx_h[["temperature", "humidity", "rainfall"]].interpolate(method="time") # Changed from pressure
    wx_h = wx_h.reset_index()

    if len(flags) > 0:
        wx_h["wx_tags"] = "WX_CLEANED"

    weather_flags = pd.concat(flags, ignore_index=True) if flags else pd.DataFrame(
        columns=["hour_ts", "variable", "flag"]
    )

    return wx_h, weather_flags

# C. Time & historical features

# ---------------------------------------------------------------------------
# Appliance-type classifier (maps device_id to appliance category)
# ---------------------------------------------------------------------------
_APPLIANCE_KEYWORDS = {
    "refrigerator": ["refrigerator", "ref", "fridge"],
    "electric_fan": ["electric_fan", "efan", "fan"],
    "aircon":       ["aircon", "ac", "air_con"],
}


def _classify_appliance(device_id: str) -> str:
    """Map a device_id string to an appliance category."""
    lower = str(device_id).lower()
    for appliance, keywords in _APPLIANCE_KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            return appliance
    return "unknown"


def _add_appliance_specific_features(
    group: pd.DataFrame,
    appliance: str,
) -> pd.DataFrame:
    """
    Add features tuned for a specific appliance's energy signature.

    Refrigerator: short-memory lags (1-3h), rolling volatility, temp×humidity
                  interaction to capture compressor cycling patterns.
    Electric fan: quadratic temperature, simplified heat index, sleeping-hours
                  indicator for sustained overnight usage blocks.
    Aircon:       no extra features — baseline feature set is already effective.
    """
    g = group.copy()

    if appliance == "refrigerator":
        # Short-memory lags: compressor state has very short autocorrelation
        g["lag_1"] = g["e_hour_kwh"].shift(1)
        g["lag_2"] = g["e_hour_kwh"].shift(2)
        g["lag_3"] = g["e_hour_kwh"].shift(3)

        # Rolling volatility: high std signals active compressor cycling
        g["rolling_std_24"] = g["e_hour_kwh"].rolling(
            window=24, min_periods=1
        ).std()

        # Temperature × humidity interaction: compressor load proxy
        if "temperature" in g.columns and "humidity" in g.columns:
            g["temp_humidity_interaction"] = g["temperature"] * g["humidity"]

    elif appliance == "electric_fan":
        # Quadratic temperature: fan usage spikes non-linearly above ~28°C
        if "temperature" in g.columns:
            g["temperature_sq"] = g["temperature"] ** 2

        # Simplified heat index proxy: better predictor than temp alone
        if "temperature" in g.columns and "humidity" in g.columns:
            g["heat_index"] = g["temperature"] + 0.33 * g["humidity"] - 4.0

        # Sleeping hours indicator: fans often run continuously overnight
        g["is_sleeping"] = g["hour_ts"].dt.hour.isin(
            list(range(22, 24)) + list(range(0, 7))
        ).astype(int)

    # aircon and unknown: no extra features needed
    return g


def add_time_lag_rolling_features(hourly_df: pd.DataFrame, cfg: Stage333Config) -> pd.DataFrame:
    h = hourly_df.copy()
    h = h.sort_values(["device_id", "hour_ts"]).reset_index(drop=True)

    h["hour_of_day"] = h["hour_ts"].dt.hour
    h["day_of_week"] = h["hour_ts"].dt.dayofweek
    h["is_weekend"] = h["day_of_week"].isin([5, 6]).astype(int)

    h["is_holiday"] = 0

    h["lag_24"] = h.groupby("device_id")["e_hour_kwh"].shift(cfg.lag_24)
    h["lag_168"] = h.groupby("device_id")["e_hour_kwh"].shift(cfg.lag_168)

    h["rolling_mean_24"] = h.groupby("device_id")["e_hour_kwh"].transform(
        lambda s: s.rolling(window=cfg.roll_24, min_periods=1).mean()
    )
    h["rolling_mean_168"] = h.groupby("device_id")["e_hour_kwh"].transform(
        lambda s: s.rolling(window=cfg.roll_168, min_periods=1).mean()
    )

    # --- Appliance-specific features ---
    enriched_groups = []
    for device_id, group in h.groupby("device_id"):
        appliance = _classify_appliance(device_id)
        enriched = _add_appliance_specific_features(group, appliance)
        enriched_groups.append(enriched)

    h = pd.concat(enriched_groups, ignore_index=True)
    h = h.sort_values(["device_id", "hour_ts"]).reset_index(drop=True)

    return h

# Merge hourly energy with weather

def merge_hourly_with_weather(hourly_energy: pd.DataFrame, weather_hourly: pd.DataFrame) -> pd.DataFrame:
    merged = hourly_energy.merge(
        weather_hourly[["hour_ts", "temperature", "humidity", "rainfall", "wx_tags"]], # Changed from pressure
        on="hour_ts",
        how="left"
    )
    return merged

# Stage Runner

def stage_333_aggregation_and_features(
    smartplug_stage332_path: str,
    weather_path: str,
    cfg: Stage333Config = Stage333Config()
) -> Dict[str, pd.DataFrame]:
    sp = pd.read_csv(smartplug_stage332_path)
    wx = pd.read_csv(weather_path)

    sp = _ensure_datetime_tz(sp, "timestamp")
    wx = _ensure_datetime_tz(wx, "timestamp")

    # A) hourly aggregation + reconciliation flags
    hourly_energy = hourly_resample_energy(sp, cfg)
    hourly_recon_flags = hourly_energy.loc[
        hourly_energy["hour_tags"].str.contains("HOURLY_RECON_GT_5PCT", na=False),
        ["device_id", "hour_ts", "e_hour_kwh", "kwh_net", "recon_dev_pct", "hour_tags"]
    ].reset_index(drop=True)

    # B) weather validation
    weather_hourly, weather_flags = validate_and_clean_weather(wx, cfg)

    # Merge
    merged = merge_hourly_with_weather(hourly_energy, weather_hourly)

    # C) time/lag/rolling features
    hourly_features = add_time_lag_rolling_features(merged, cfg)

    return {
        "hourly_features_df": hourly_features,
        "hourly_recon_flags": hourly_recon_flags,
        "weather_flags": weather_flags
    }

# Example usage
# if __name__ == "__main__":
#     out = stage_333_aggregation_and_features(
#         smartplug_stage332_path="out/smartplug_stage332.csv",
#         weather_path="out/weather_stage331.csv"
#     )

#     out["hourly_features_df"].to_csv("out/hourly_features_stage333.csv", index=False)
#     out["hourly_recon_flags"].to_csv("out/flags_hourly_recon_stage333.csv", index=False)
#     out["weather_flags"].to_csv("out/flags_weather_stage333.csv", index=False)

#     print("Saved Stage 3.3.3 outputs:")
#     print("- out/hourly_features_stage333.csv")
#     print("- out/flags_hourly_recon_stage333.csv")
#     print("- out/flags_weather_stage333.csv")
