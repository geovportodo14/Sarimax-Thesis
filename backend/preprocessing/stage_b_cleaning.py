# Stage 3.3.2 — Data Cleaning and Energy Derivation

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple, List

import numpy as np
import pandas as pd

@dataclass
class Stage332Config:
    interval_seconds_expected: int = 600           
    minor_gap_max_seconds: int = 1200           
    hybrid_diff_tol_pct: float = 10.0          
    daily_consistency_tol_pct: float = 5.0        

    power_spike_z: float = 5.0                 
    rolling_window: int = 3                

def _ensure_datetime_tz(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="ISO8601", errors="coerce")
    
    # Debug: Check for NaTs immediately after parsing
    nat_count = df["timestamp"].isna().sum()
    if nat_count > 0:
        print(f"WARNING: _ensure_datetime_tz generated {nat_count} NaT values!")
        print("Sample NaT rows:", df[df["timestamp"].isna()].head())

    if getattr(df["timestamp"].dt, "tz", None) is None:
        df["timestamp"] = df["timestamp"].dt.tz_localize("Asia/Manila", nonexistent="shift_forward", ambiguous="NaT")
    else:
        df["timestamp"] = df["timestamp"].dt.tz_convert("Asia/Manila")
    return df


def _tag_append(existing: str, new_tag: str) -> str:
    if not existing:
        return new_tag
    if new_tag in existing.split("|"):
        return existing
    return existing + "|" + new_tag


def _pct_diff(a: float, b: float) -> float:
    if a is None or pd.isna(a) or abs(a) < 1e-12:
        return np.inf
    return abs(a - b) / abs(a) * 100.0

# A. Interval Energy Computation

def compute_interval_and_fallback_energy(df: pd.DataFrame, cfg: Stage332Config) -> pd.DataFrame:
    d = df.copy()
    d["tags"] = ""

    d = d.sort_values(["device_id", "timestamp"]).reset_index(drop=True)

    d["dt_seconds"] = d.groupby("device_id")["timestamp"].diff().dt.total_seconds()

    d["e_interval_kwh"] = d.groupby("device_id")["kwh_total"].diff()
    neg_mask = d["e_interval_kwh"].notna() & (d["e_interval_kwh"] < 0)
    d.loc[neg_mask, "tags"] = d.loc[neg_mask, "tags"].apply(lambda x: _tag_append(x, "RESET_OR_NEG_KWH"))
    d["e_interval_kwh"] = d["e_interval_kwh"].clip(lower=0)

    d["p_prev_w"] = d.groupby("device_id")["power_w_corrected"].shift(1)
    d["p_avg_w"] = (d["power_w_corrected"] + d["p_prev_w"]) / 2.0

    d["e_fallback_kwh"] = (d["p_avg_w"] * d["dt_seconds"]) / 3_600_000

    off_mask = (d["switch"] == False)
    d.loc[off_mask, "e_fallback_kwh"] = 0.0

    return d


def apply_hybrid_energy_rule(df: pd.DataFrame, cfg: Stage332Config) -> pd.DataFrame:
    d = df.copy()

    d["e_final_kwh"] = np.nan

    off_mask = (d["switch"] == False)
    d.loc[off_mask, "e_final_kwh"] = 0.0
    d.loc[off_mask, "tags"] = d.loc[off_mask, "tags"].apply(lambda x: _tag_append(x, "SWITCH_OFF"))

    on_mask = (d["switch"] == True)

    interval_ok = on_mask & d["e_interval_kwh"].notna() & d["e_fallback_kwh"].notna()

    diff_pct = np.where(
        interval_ok,
        np.abs(d["e_interval_kwh"] - d["e_fallback_kwh"]) / np.where(d["e_interval_kwh"].abs() > 1e-12, d["e_interval_kwh"].abs(), np.nan) * 100.0,
        np.nan
    )
    d["hybrid_diff_pct"] = diff_pct

    keep_interval = interval_ok & (d["hybrid_diff_pct"] <= cfg.hybrid_diff_tol_pct)

    d.loc[keep_interval, "e_final_kwh"] = d.loc[keep_interval, "e_interval_kwh"]
    d.loc[keep_interval, "tags"] = d.loc[keep_interval, "tags"].apply(lambda x: _tag_append(x, "USE_INTERVAL"))

    use_fallback = on_mask & (~keep_interval)
    d.loc[use_fallback, "e_final_kwh"] = d.loc[use_fallback, "e_fallback_kwh"]
    d.loc[use_fallback, "tags"] = d.loc[use_fallback, "tags"].apply(lambda x: _tag_append(x, "USE_FALLBACK"))

    first_mask = on_mask & d["dt_seconds"].isna()
    d.loc[first_mask, "e_final_kwh"] = 0.0
    d.loc[first_mask, "tags"] = d.loc[first_mask, "tags"].apply(lambda x: _tag_append(x, "FIRST_RECORD_ZERO"))

    return d

# B. Handling gaps, resets, and outliers

def handle_gaps_and_interpolation(df: pd.DataFrame, cfg: Stage332Config) -> pd.DataFrame:
    d = df.copy()

    d["gap_type"] = ""
    minor_gap = d["dt_seconds"].notna() & (d["dt_seconds"] > cfg.interval_seconds_expected) & (d["dt_seconds"] <= cfg.minor_gap_max_seconds)
    long_gap = d["dt_seconds"].notna() & (d["dt_seconds"] > cfg.minor_gap_max_seconds)

    d.loc[minor_gap, "gap_type"] = "MINOR_GAP"
    d.loc[minor_gap, "tags"] = d.loc[minor_gap, "tags"].apply(lambda x: _tag_append(x, "MINOR_GAP_DETECTED"))

    d.loc[long_gap, "gap_type"] = "LONG_GAP"
    d.loc[long_gap, "tags"] = d.loc[long_gap, "tags"].apply(lambda x: _tag_append(x, "LONG_GAP_DETECTED"))

    # Time-weighted interpolation requires a DatetimeIndex AND no NaNs in the index.
    # We drop any rows with NaT timestamps and set the index temporarily.
    d_clean = d.dropna(subset=["timestamp"]).copy()
    
    # Set index to timestamp to allow time-based interpolation
    d_clean = d_clean.set_index("timestamp")

    for col in ["voltage_v", "current_a", "power_w_corrected"]:
        # Group by device and interpolate
        # d_clean has DatetimeIndex. Groupby 'device_id' (column) preserves this for the group.
        interp_series = d_clean.groupby("device_id")[col].apply(lambda s: s.interpolate(method="time"))
        
        # interp_series has MultiIndex (device_id, timestamp).
        # Convert to DF for merging.
        interp_df = interp_series.to_frame(name=col + "_interp").reset_index()
        
        # Merge back to d
        # d has 'timestamp' column (from original d, not d_clean)
        # We merge on device_id and timestamp.
        if col + "_interp" in d.columns:
            d = d.drop(columns=[col + "_interp"])
        
        # Ensure timestamp types match for merge (both are datetime-like or compatible)
        # d["timestamp"] is already datetime from _ensure_datetime_tz
        d = d.merge(interp_df, on=["device_id", "timestamp"], how="left")

    use_fb = d["tags"].str.contains("USE_FALLBACK", na=False)
    has_interp = d["power_w_corrected_interp"].notna() & d["p_prev_w"].notna() & d["dt_seconds"].notna()

    d.loc[use_fb & has_interp, "p_avg_w"] = (d.loc[use_fb & has_interp, "power_w_corrected_interp"] + d.loc[use_fb & has_interp, "p_prev_w"]) / 2.0
    d.loc[use_fb & has_interp, "e_fallback_kwh"] = (d.loc[use_fb & has_interp, "p_avg_w"] * d.loc[use_fb & has_interp, "dt_seconds"]) / 3_600_000
    d.loc[use_fb & has_interp, "tags"] = d.loc[use_fb & has_interp, "tags"].apply(lambda x: _tag_append(x, "FALLBACK_USING_INTERP_P"))

    long_gap_rows = long_gap & (d["switch"] == True)
    d.loc[long_gap_rows, "e_final_kwh"] = 0.0
    d.loc[long_gap_rows, "tags"] = d.loc[long_gap_rows, "tags"].apply(lambda x: _tag_append(x, "ZEROED_LONG_GAP"))

    return d

def replace_outliers_with_rolling_mean(df: pd.DataFrame, cfg: Stage332Config) -> pd.DataFrame:

    d = df.copy()

    def _zscore(s: pd.Series) -> pd.Series:
        mu = s.mean()
        sd = s.std(ddof=0)
        if sd == 0 or np.isnan(sd):
            return pd.Series(np.zeros(len(s)), index=s.index)
        return (s - mu) / sd

    d["p_z"] = d.groupby("device_id")["power_w_corrected"].transform(_zscore)
    spike = d["p_z"].abs() > cfg.power_spike_z

    if spike.any():
        d.loc[spike, "tags"] = d.loc[spike, "tags"].apply(lambda x: _tag_append(x, "POWER_OUTLIER"))

        for col in ["voltage_v", "current_a", "power_w_corrected"]:
            roll = d.groupby("device_id")[col].transform(
                lambda s: s.rolling(window=cfg.rolling_window, center=True, min_periods=1).mean()
            )
            d.loc[spike, col] = roll.loc[spike]

        d.loc[spike, "tags"] = d.loc[spike, "tags"].apply(lambda x: _tag_append(x, "REPLACED_ROLLING_MEAN"))

    return d

# C. Daily Consistency Check

def daily_consistency_check(df: pd.DataFrame, cfg: Stage332Config) -> Tuple[pd.DataFrame, pd.DataFrame]:

    d = df.copy()
    d["date"] = d["timestamp"].dt.tz_convert("Asia/Manila").dt.date

    daily_sum = d.groupby(["device_id", "date"], as_index=False)["e_final_kwh"].sum().rename(columns={"e_final_kwh": "total_energy_kwh"})

    first_last = d.sort_values(["device_id", "timestamp"]).groupby(["device_id", "date"]).agg(
        kwh_start=("kwh_total", "first"),
        kwh_end=("kwh_total", "last")
    ).reset_index()
    first_last["cumulative_energy_kwh"] = (first_last["kwh_end"] - first_last["kwh_start"]).clip(lower=0)

    report = daily_sum.merge(first_last[["device_id", "date", "cumulative_energy_kwh"]], on=["device_id", "date"], how="left")

    report["deviation_pct"] = np.where(
        report["cumulative_energy_kwh"].abs() > 1e-12,
        (report["total_energy_kwh"] - report["cumulative_energy_kwh"]) / report["cumulative_energy_kwh"] * 100.0,
        np.nan
    )
    report["deviation_pct_abs"] = report["deviation_pct"].abs()
    report["flag"] = report["deviation_pct_abs"] > cfg.daily_consistency_tol_pct

    bad_days = report.loc[report["flag"], ["device_id", "date"]]
    if not bad_days.empty:
        bad_index = d.merge(bad_days, on=["device_id", "date"], how="inner").index
        d.loc[bad_index, "tags"] = d.loc[bad_index, "tags"].apply(lambda x: _tag_append(x, "DAILY_DEVIATION_GT_5PCT"))

    return d, report

# Stage Runner

def stage_332_cleaning_and_energy_derivation(
    smartplug_stage331_path: str,
    cfg: Stage332Config = Stage332Config()
) -> dict:

    df = pd.read_csv(smartplug_stage331_path)
    df = _ensure_datetime_tz(df)

    needed = ["timestamp", "device_id", "switch", "power_w_corrected", "kwh_total", "voltage_v", "current_a"]
    missing = [c for c in needed if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns for Stage 3.3.2: {missing}")

    # A: energy computations
    df = compute_interval_and_fallback_energy(df, cfg)
    df = apply_hybrid_energy_rule(df, cfg)

    # B: gaps/resets handling
    df = handle_gaps_and_interpolation(df, cfg)

    # B4: outliers/spikes correction
    df = replace_outliers_with_rolling_mean(df, cfg)

    # Recompute fallback + hybrid
    df = compute_interval_and_fallback_energy(df, cfg)
    df = apply_hybrid_energy_rule(df, cfg)

    # C: daily consistency check
    df, daily_report = daily_consistency_check(df, cfg)

    return {"df_stage332": df, "daily_report": daily_report}


# Example usage
# if __name__ == "__main__":
#     out = stage_332_cleaning_and_energy_derivation(
#         smartplug_stage331_path="out/smartplug_stage331.csv"
#     )

#     out["df_stage332"].to_csv("out/smartplug_stage332.csv", index=False)
#     out["daily_report"].to_csv("out/daily_consistency_report_stage332.csv", index=False)

#     print("Saved Stage 3.3.2 outputs:")
#     print("- out/smartplug_stage332.csv")
#     print("- out/daily_consistency_report_stage332.csv")
