"""
forecasting/pipeline/features.py
=================================
Builds the `future_exog` DataFrame that SARIMAX requires for the 24-step
forecast window.

Design rules:
  * Calendar features   → computed deterministically from future timestamps
  * Lag features        → taken from *actual* historical observations only
  * Rolling means       → computed from *actual* historical observations only
  * Weather features    → supplied by the caller (from weather API)
  * Column alignment    → enforced by reindexing to exog_columns from best_params.json
  * dtype safety        → all columns cast to float64 before returning
"""

from __future__ import annotations

import logging
import math
from typing import Optional, Sequence

import numpy as np
import pandas as pd

log = logging.getLogger("sarimax_pipeline.features")

# ---------------------------------------------------------------------------
# Calendar features
# ---------------------------------------------------------------------------

def add_calendar_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add all deterministic calendar columns to *df* in-place.

    Input *df* must have a DatetimeIndex.
    """
    idx = df.index
    df["sin_hour"]        = np.sin(2 * math.pi * idx.hour / 24)
    df["cos_hour"]        = np.cos(2 * math.pi * idx.hour / 24)
    df["sin_day_of_week"] = np.sin(2 * math.pi * idx.dayofweek / 7)
    df["cos_day_of_week"] = np.cos(2 * math.pi * idx.dayofweek / 7)
    df["is_weekend"]      = (idx.dayofweek >= 5).astype(float)
    df["hour_of_day"]     = idx.hour.astype(float)
    df["day_of_week"]     = idx.dayofweek.astype(float)
    df["month"]           = idx.month.astype(float)
    return df


# ---------------------------------------------------------------------------
# Lag features
# ---------------------------------------------------------------------------

def compute_lag_features(
    history: pd.DataFrame,
    future_idx: pd.DatetimeIndex,
    energy_col: str = "energy",
) -> pd.DataFrame:
    """
    Compute lag_24 and lag_168 for each future timestamp using *only* past
    actual observations.

    Parameters
    ----------
    history   : DataFrame with DatetimeIndex containing column *energy_col*.
    future_idx: DatetimeIndex of the 24 forecast hours (next-day).

    Returns
    -------
    DataFrame indexed by *future_idx* with columns lag_24, lag_168.
    """
    out = pd.DataFrame(index=future_idx, dtype=float)

    for ts in future_idx:
        lag24  = ts - pd.Timedelta(hours=24)
        lag168 = ts - pd.Timedelta(hours=168)

        out.loc[ts, "lag_24"] = (
            history.loc[lag24, energy_col]
            if lag24 in history.index else np.nan
        )
        out.loc[ts, "lag_168"] = (
            history.loc[lag168, energy_col]
            if lag168 in history.index else np.nan
        )

    missing_24  = out["lag_24"].isna().sum()
    missing_168 = out["lag_168"].isna().sum()

    if missing_24:
        log.warning("lag_24: %d NaN values. Forward-filling from history.", missing_24)
        # Fill from latest available energy value, or 0 if history is empty
        fallback = history[energy_col].iloc[-24:].mean() if len(history) >= 24 else history[energy_col].mean()
        if pd.isna(fallback): fallback = 0.0
        out["lag_24"] = out["lag_24"].fillna(fallback)

    if missing_168:
        log.warning("lag_168: %d NaN values. Forward-filling from history.", missing_168)
        fallback = history[energy_col].iloc[-168:].mean() if len(history) >= 168 else history[energy_col].mean()
        if pd.isna(fallback): fallback = 0.0
        out["lag_168"] = out["lag_168"].fillna(fallback)

    return out.astype(float)


# ---------------------------------------------------------------------------
# Rolling mean features
# ---------------------------------------------------------------------------

def compute_rolling_features(
    history: pd.DataFrame,
    future_idx: pd.DatetimeIndex,
    energy_col: str = "energy",
) -> pd.DataFrame:
    """
    Compute rolling_mean_24 and rolling_mean_168 anchored at the last
    observed timestamp (no data leakage – uses only past actuals).

    rolling_mean_24  = mean of the last 24 actual hourly readings
    rolling_mean_168 = mean of the last 168 actual hourly readings

    Because these values are the same for all 24 future hours (the window
    does not slide into unobserved territory), we broadcast the scalar.
    """
    energy = history[energy_col].dropna()

    rm24  = float(energy.iloc[-24:].mean())   if len(energy) >= 24  else float(energy.mean())
    rm168 = float(energy.iloc[-168:].mean())  if len(energy) >= 168 else float(energy.mean())

    out = pd.DataFrame(
        {"rolling_mean_24": rm24, "rolling_mean_168": rm168},
        index=future_idx,
        dtype=float,
    )

    log.debug("rolling_mean_24=%.4f  rolling_mean_168=%.4f", rm24, rm168)
    return out


# ---------------------------------------------------------------------------
# Power (load proxy) feature
# ---------------------------------------------------------------------------

def compute_power_feature(
    history: pd.DataFrame,
    future_idx: pd.DatetimeIndex,
    power_col: str = "power",
) -> pd.DataFrame:
    """
    Computes expected power (kW) by taking the historic average for each hour
    of the day over the last 30 days. This mimics Time-of-Use behavior so the
    model doesn't flatline. If no prior hourly data, falls back to flat mean.
    """
    out = pd.DataFrame(index=future_idx, dtype=float)

    # Use the last 30 days of data to establish the daily time-of-use profile
    if len(history) > 0:
        cutoff = history.index[-1] - pd.Timedelta(days=30)
        recent_history = history.loc[cutoff:]
    else:
        recent_history = history

    if power_col in recent_history.columns and not recent_history[power_col].dropna().empty:
        # Calculate the mean power usage per hour-of-use (0-23)
        hourly_profile = recent_history.groupby(recent_history.index.hour)[power_col].mean()
        
        # Map this profile to the future 24 hours
        out["power"] = future_idx.hour.map(hourly_profile).values
        
        # If any specific hour has missing data in the profile, fill with the overall mean
        if out["power"].isna().any():
            overall_mean = float(recent_history[power_col].mean())
            out["power"] = out["power"].fillna(overall_mean)
            
        log.debug("Built dynamic Time-of-Use power profile.")
    else:
        # Fallback to older flat-fill if `power` column is entirely missing
        log.warning("No power column or history found; falling back to flat prediction.")
        last_power = float(history["energy"].iloc[-24:].mean()) if len(history) >= 24 else 0.0
        out["power"] = last_power

    return out


# ---------------------------------------------------------------------------
# Appliance-specific features (mirrors preprocessing/stage_c_features.py)
# ---------------------------------------------------------------------------

def add_appliance_specific_features(
    Xf: pd.DataFrame,
    history: pd.DataFrame,
    energy_col: str = "energy",
) -> pd.DataFrame:
    """
    Add appliance-specific columns so column alignment can pick them up.
    All columns are added unconditionally; the final alignment step keeps
    only the ones the model was trained with.
    """
    idx = Xf.index

    # --- Refrigerator features ---
    # Short lags: look back 1-3 hours into history
    energy = history[energy_col].dropna()
    for lag_h in [1, 2, 3]:
        col_name = f"lag_{lag_h}"
        vals = []
        for ts in idx:
            lookup = ts - pd.Timedelta(hours=lag_h)
            vals.append(
                energy.loc[lookup] if lookup in energy.index else
                (float(energy.iloc[-1]) if len(energy) > 0 else 0.0)
            )
        Xf[col_name] = vals

    # Rolling std from last 24 hours of history (scalar broadcast)
    if len(energy) >= 24:
        Xf["rolling_std_24"] = float(energy.iloc[-24:].std())
    else:
        Xf["rolling_std_24"] = float(energy.std()) if len(energy) > 1 else 0.0

    # Temperature × humidity interaction
    if "temperature" in Xf.columns and "humidity" in Xf.columns:
        Xf["temp_humidity_interaction"] = Xf["temperature"] * Xf["humidity"]

    # --- Electric fan features ---
    if "temperature" in Xf.columns:
        Xf["temperature_sq"] = Xf["temperature"] ** 2

    if "temperature" in Xf.columns and "humidity" in Xf.columns:
        Xf["heat_index"] = Xf["temperature"] + 0.33 * Xf["humidity"] - 4.0

    Xf["is_sleeping"] = idx.hour.isin(
        list(range(22, 24)) + list(range(0, 7))
    ).astype(float)

    return Xf


# ---------------------------------------------------------------------------
# Main builder
# ---------------------------------------------------------------------------

def build_future_exog(
    history: pd.DataFrame,
    future_idx: pd.DatetimeIndex,
    exog_columns: Sequence[str],
    weather_df: Optional[pd.DataFrame] = None,
    energy_col: str = "energy",
) -> pd.DataFrame:
    """
    Build the `future_exog` DataFrame (24 rows × len(exog_columns) columns)
    required by SARIMAX's `get_forecast(exog=...)`.

    Parameters
    ----------
    history      : Full historical DataFrame (energy + all exog cols) with DatetimeIndex.
    future_idx   : Exactly 24 hourly timestamps for the next day.
    exog_columns : List of column names from best_params.json (defines order).
    weather_df   : 24-row DataFrame from weather API (temperature, humidity, rainfall).
                   If None and weather cols are needed, falls back to last observed values.
    energy_col   : Name of the target energy column in *history*.

    Returns
    -------
    DataFrame with shape (24, len(exog_columns)), ready for SARIMAX.
    """
    assert len(future_idx) == 24, f"future_idx must have exactly 24 periods, got {len(future_idx)}"

    # ── Start with an empty frame ────────────────────────────────────────────
    Xf = pd.DataFrame(index=future_idx, dtype=float)

    # ── Calendar features ────────────────────────────────────────────────────
    Xf = add_calendar_features(Xf)

    # ── Lag features ─────────────────────────────────────────────────────────
    lags = compute_lag_features(history, future_idx, energy_col)
    Xf   = Xf.join(lags, how="left")

    # ── Rolling mean features ─────────────────────────────────────────────────
    rolls = compute_rolling_features(history, future_idx, energy_col)
    Xf    = Xf.join(rolls, how="left")

    # ── Power feature ─────────────────────────────────────────────────────────
    if "power" in exog_columns:
        pwr = compute_power_feature(history, future_idx)
        Xf  = Xf.join(pwr, how="left")

    # ── Weather features ──────────────────────────────────────────────────────
    weather_cols = [c for c in exog_columns if c in ("temperature", "humidity", "rainfall")]
    if weather_cols:
        if weather_df is not None and len(weather_df) == 24:
            for c in weather_cols:
                if c in weather_df.columns:
                    Xf[c] = weather_df[c].values
                else:
                    log.warning("Weather col '%s' missing from API data; forward-filling.", c)
                    Xf[c] = float(history[c].iloc[-1]) if c in history.columns else 0.0
        else:
            log.warning("Weather forecast unavailable; forward-filling from history.")
            for c in weather_cols:
                Xf[c] = float(history[c].iloc[-1]) if c in history.columns else 0.0

    # ── Appliance-specific features ──────────────────────────────────────────
    appliance_cols = {"lag_1", "lag_2", "lag_3", "rolling_std_24",
                      "temp_humidity_interaction", "temperature_sq",
                      "heat_index", "is_sleeping"}
    if appliance_cols & set(exog_columns):
        Xf = add_appliance_specific_features(Xf, history, energy_col)

    # ── Align to training column order ────────────────────────────────────────
    missing = [c for c in exog_columns if c not in Xf.columns]
    if missing:
        log.warning("Columns not yet populated, forward-filling from history: %s", missing)
        for c in missing:
            if c in history.columns:
                Xf[c] = float(history[c].dropna().iloc[-1])
            else:
                log.error("Column '%s' is required but cannot be constructed. Setting to 0.", c)
                Xf[c] = 0.0

    # Enforce exact column order from best_params.json
    Xf = Xf[list(exog_columns)]

    # ── Final dtype and NaN check ─────────────────────────────────────────────
    Xf = Xf.astype(float)
    nans = Xf.isna().sum()
    if nans.any():
        bad = nans[nans > 0].to_dict()
        raise RuntimeError(
            f"future_exog still has NaN values after all filling steps: {bad}. "
            "Check that history contains sufficient data and all required columns."
        )

    log.info("future_exog built: shape=%s, cols=%s", Xf.shape, list(Xf.columns))
    return Xf
