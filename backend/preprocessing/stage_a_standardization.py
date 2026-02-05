# Stage 3.3.1 — Data Integrity Verification and Standardization

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

import numpy as np
import pandas as pd

SMARTPLUG_REQUIRED_COLS = [
    "timestamp", "device_id", "switch",
    "voltage_raw", "current_raw", "power_raw", "kwh_raw",
    "voltage_v", "current_a", "power_w", "kwh_total", "pf"
]

WEATHER_REQUIRED_COLS = ["timestamp", "temperature", "humidity", "rainfall"]


@dataclass
class IntegrityThresholds:
    smartplug_interval_s: int = 600    
    weather_interval_s: int = 3600     

    power_dev_tol_pct: float = 5.0     
    pf_dev_tol_abs: float = 0.10        

    v_min: float = 220.0
    v_max: float = 240.0
    i_min: float = 0.0
    i_max: float = 15.0
    p_min: float = 0.0
    p_max: float = 3000.0
    pf_min: float = 0.85
    pf_max: float = 1.00

def _assert_required_columns(df: pd.DataFrame, required: List[str], name: str) -> List[str]:
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"[{name}] Missing required columns: {missing}")
    return missing


def _coerce_types_smartplug(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    if df["switch"].dtype == object:
        df["switch"] = df["switch"].astype(str).str.lower().map({"true": True, "false": False})
    df["switch"] = df["switch"].astype("boolean")

    num_cols = [
        "voltage_raw", "current_raw", "power_raw", "kwh_raw",
        "voltage_v", "current_a", "power_w", "kwh_total", "pf"
    ]
    for c in num_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df["device_id"] = df["device_id"].astype(str)
    return df


def _coerce_types_weather(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    for c in ["temperature", "humidity", "rainfall"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def _standardize_to_utc_plus_8(df: pd.DataFrame, ts_col: str = "timestamp") -> pd.DataFrame:

    df = df.copy()
    ts = df[ts_col]

    if getattr(ts.dt, "tz", None) is None:
        df[ts_col] = ts.dt.tz_localize("Asia/Manila", nonexistent="shift_forward", ambiguous="NaT")
    else:
        df[ts_col] = ts.dt.tz_convert("Asia/Manila")
    return df


def _sort_by_device_and_time(df: pd.DataFrame) -> pd.DataFrame:
    return df.sort_values(["device_id", "timestamp"]).reset_index(drop=True)


def _compute_time_deltas_seconds(df: pd.DataFrame, group_col: str = "device_id") -> pd.Series:
    return df.groupby(group_col)["timestamp"].diff().dt.total_seconds()

# A. Schema Alignment & Unit Validation

def verify_schema_and_units(
    smartplug_df: pd.DataFrame,
    weather_df: pd.DataFrame
) -> Dict[str, List[str]]:
    
    _assert_required_columns(smartplug_df, SMARTPLUG_REQUIRED_COLS, "smartplug")
    _assert_required_columns(weather_df, WEATHER_REQUIRED_COLS, "weather")

    issues = {"smartplug": [], "weather": []}

    if smartplug_df["timestamp"].isna().any():
        issues["smartplug"].append("Some smartplug timestamps failed to parse (NaT).")
    if weather_df["timestamp"].isna().any():
        issues["weather"].append("Some weather timestamps failed to parse (NaT).")

    sp_num = ["voltage_v", "current_a", "power_w", "kwh_total", "pf"]
    for c in sp_num:
        if smartplug_df[c].isna().any():
            issues["smartplug"].append(f"Some values in {c} failed numeric coercion (NaN).")

    wx_num = ["temperature", "humidity", "rainfall"]
    for c in wx_num:
        if weather_df[c].isna().any():
            issues["weather"].append(f"Some values in {c} failed numeric coercion (NaN).")

    return issues

# B. Time Standardization & Ordering

def standardize_and_check_time(
    smartplug_df: pd.DataFrame,
    weather_df: pd.DataFrame,
    thr: IntegrityThresholds = IntegrityThresholds()
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:

    sp = _standardize_to_utc_plus_8(smartplug_df)
    wx = _standardize_to_utc_plus_8(weather_df)

    sp = _sort_by_device_and_time(sp)
    wx = wx.sort_values("timestamp").reset_index(drop=True)

    sp_delta = _compute_time_deltas_seconds(sp, "device_id")
    wx_delta = wx["timestamp"].diff().dt.total_seconds()

    time_flags = []

    sp_bad = sp_delta.notna() & (sp_delta != thr.smartplug_interval_s)
    if sp_bad.any():
        bad_rows = sp.loc[sp_bad, ["device_id", "timestamp"]].copy()
        bad_rows["dataset"] = "smartplug"
        bad_rows["delta_seconds"] = sp_delta[sp_bad].values
        time_flags.append(bad_rows)

    wx_bad = wx_delta.notna() & (wx_delta != thr.weather_interval_s)
    if wx_bad.any():
        bad_rows = wx.loc[wx_bad, ["timestamp"]].copy()
        bad_rows["dataset"] = "weather"
        bad_rows["delta_seconds"] = wx_delta[wx_bad].values
        time_flags.append(bad_rows)

    time_flags_df = pd.concat(time_flags, ignore_index=True) if time_flags else pd.DataFrame(
        columns=["dataset", "device_id", "timestamp", "delta_seconds"]
    )

    return sp, wx, time_flags_df

# C. Physics Consistency & Scaling Verification

def recompute_power_and_pf_checks(
    sp: pd.DataFrame,
    thr: IntegrityThresholds = IntegrityThresholds()
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    df = sp.copy()

    vi = df["voltage_v"] * df["current_a"]
    df["p_calc"] = df["voltage_v"] * df["current_a"] * df["pf"]

    df["p_dev_pct"] = np.where(
        df["p_calc"].abs() > 1e-9,
        ((df["power_w"] - df["p_calc"]) / df["p_calc"]).abs() * 100.0,
        np.nan
    )

    replace_mask = (df["switch"] == True) & (df["p_dev_pct"] > thr.power_dev_tol_pct)
    df["power_w_corrected"] = df["power_w"]
    df.loc[replace_mask, "power_w_corrected"] = df.loc[replace_mask, "p_calc"]

    df["pf_calc"] = np.where(vi.abs() > 1e-9, df["power_w_corrected"] / vi, np.nan)

    flags = []

    def _flag(mask: pd.Series, code: str, detail: str):
        if mask.any():
            tmp = df.loc[mask, ["device_id", "timestamp"]].copy()
            tmp["flag"] = code
            tmp["detail"] = detail
            flags.append(tmp)

    on_mask = (df["switch"] == True)

    _flag(on_mask & ((df["voltage_v"] < thr.v_min) | (df["voltage_v"] > thr.v_max)),
          "V_RANGE", f"Voltage out of [{thr.v_min},{thr.v_max}] V while ON.")
    _flag(on_mask & ((df["current_a"] <= thr.i_min) | (df["current_a"] > thr.i_max)),
          "I_RANGE", f"Current out of (>{thr.i_min}, <= {thr.i_max}] A while ON.")
    _flag(on_mask & ((df["power_w_corrected"] <= thr.p_min) | (df["power_w_corrected"] > thr.p_max)),
          "P_RANGE", f"Power out of (>{thr.p_min}, <= {thr.p_max}] W while ON.")
    _flag(on_mask & ((df["pf"] < thr.pf_min) | (df["pf"] > thr.pf_max)),
          "PF_RANGE", f"pf out of [{thr.pf_min},{thr.pf_max}].")

    pf_diverge = (df["pf_calc"].notna()) & (df["pf"].notna()) & ((df["pf_calc"] - df["pf"]).abs() > thr.pf_dev_tol_abs)
    _flag(pf_diverge, "PF_MISMATCH", f"|pf_calc - pf| > {thr.pf_dev_tol_abs}")

    physics_flags = pd.concat(flags, ignore_index=True) if flags else pd.DataFrame(
        columns=["device_id", "timestamp", "flag", "detail"]
    )

    return df, physics_flags


def check_cumulative_monotonicity(sp: pd.DataFrame) -> pd.DataFrame:
    df = sp.copy()
    df["kwh_delta"] = df.groupby("device_id")["kwh_total"].diff()
    reset_mask = df["kwh_delta"].notna() & (df["kwh_delta"] < 0)

    flags = df.loc[reset_mask, ["device_id", "timestamp", "kwh_total", "kwh_delta"]].copy()
    flags["flag"] = "KWH_RESET"
    flags["detail"] = "kwh_total decreased (possible reset/restart)."
    return flags.reset_index(drop=True)


# Stage Runner

def stage_331_integrity_verification(
    smartplug_csv_path: str,
    weather_csv_path: str,
    thr: IntegrityThresholds = IntegrityThresholds()
) -> Dict[str, object]:

    sp_raw = pd.read_csv(smartplug_csv_path)
    wx_raw = pd.read_csv(weather_csv_path)

    sp = _coerce_types_smartplug(sp_raw)
    wx = _coerce_types_weather(wx_raw)

    # A. Schema + unit validation
    schema_issues = verify_schema_and_units(sp, wx)

    # B. Time standardization + ordering + interval checks
    sp_std, wx_std, time_flags = standardize_and_check_time(sp, wx, thr)

    # C. Physics checks
    sp_phys, physics_flags = recompute_power_and_pf_checks(sp_std, thr)

    # C.2 partial: cumulative monotonicity check 
    kwh_reset_flags = check_cumulative_monotonicity(sp_phys)

    return {
        "smartplug_std": sp_phys,
        "weather_std": wx_std,
        "schema_issues": schema_issues,
        "time_flags": time_flags,
        "physics_flags": physics_flags,
        "kwh_reset_flags": kwh_reset_flags,
    }


# Example usage
# if __name__ == "__main__":
#     result = stage_331_integrity_verification(
#         smartplug_csv_path="data/smartplug_raw.csv",
#         weather_csv_path="data/weather_raw.csv"
#     )

#     print("Schema issues:", result["schema_issues"])
#     print("Time flags:", len(result["time_flags"]))
#     print("Physics flags:", len(result["physics_flags"]))
#     print("kWh reset flags:", len(result["kwh_reset_flags"]))

#     # Optionally save standardized outputs
#     result["smartplug_std"].to_csv("out/smartplug_stage331.csv", index=False)
#     result["weather_std"].to_csv("out/weather_stage331.csv", index=False)
#     result["time_flags"].to_csv("out/flags_time_stage331.csv", index=False)
#     result["physics_flags"].to_csv("out/flags_physics_stage331.csv", index=False)
#     result["kwh_reset_flags"].to_csv("out/flags_kwh_reset_stage331.csv", index=False)
