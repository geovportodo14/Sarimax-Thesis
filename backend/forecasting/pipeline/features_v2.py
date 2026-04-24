"""
forecasting/pipeline/features_v2.py
====================================
Feature builders for the 3-stage hierarchical model (Sarimax-Model-2).

Each stage has its own feature set per appliance. Feature lists are read from
best_params.json so this module is data-driven — no hard-coded column lists.

Public API:
    build_b1_features(...)  -> DataFrame for sklearn classifier
    build_b2_features(...)  -> DataFrame for SARIMAX baseline
    build_b3_features(...)  -> DataFrame for SARIMAX residual
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Sequence

import numpy as np
import pandas as pd

log = logging.getLogger("sarimax_pipeline.features_v2")

# Energy threshold (kWh) below which an appliance is considered "off".
_ACTIVE_THRESHOLD = 0.001

# Refrigerator regime boundaries (kWh). Derived from training data quantiles.
_REGIME_THRESHOLDS = {"low": 0.03, "high": 0.08}


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _safe_scalar(series: pd.Series, default: float = 0.0) -> float:
    val = series.dropna()
    if val.empty:
        return default
    return float(val.iloc[-1])


def _classify_regime(energy: float) -> int:
    """Map a single energy reading to regime code: 0=low, 1=normal, 2=high."""
    if energy <= _REGIME_THRESHOLDS["low"]:
        return 0
    elif energy >= _REGIME_THRESHOLDS["high"]:
        return 2
    return 1


def _classify_regime_series(energy: pd.Series) -> pd.Series:
    """Classify an energy series into regime codes."""
    codes = pd.Series(1, index=energy.index, dtype=int)
    codes[energy <= _REGIME_THRESHOLDS["low"]] = 0
    codes[energy >= _REGIME_THRESHOLDS["high"]] = 2
    return codes


def _fill_and_reindex(df: pd.DataFrame, columns: Sequence[str], history: pd.DataFrame) -> pd.DataFrame:
    """Ensure all required columns exist, fill missing from history or 0."""
    missing = [c for c in columns if c not in df.columns]
    for c in missing:
        if c in history.columns:
            df[c] = _safe_scalar(history[c])
        else:
            log.warning("Column '%s' required but not computable. Setting to 0.", c)
            df[c] = 0.0

    df = df[list(columns)]
    df = df.astype(float)
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.ffill().bfill().fillna(0.0)
    return df


# ---------------------------------------------------------------------------
# Calendar features
# ---------------------------------------------------------------------------

def _add_calendar(df: pd.DataFrame) -> pd.DataFrame:
    idx = df.index
    df["hour"] = idx.hour.astype(float)
    df["is_weekend"] = (idx.dayofweek >= 5).astype(float)
    return df


# ---------------------------------------------------------------------------
# Weather features
# ---------------------------------------------------------------------------

def _add_weather(
    df: pd.DataFrame,
    weather_df: Optional[pd.DataFrame],
    history: pd.DataFrame,
    needed_cols: Sequence[str],
) -> pd.DataFrame:
    raw_weather = ["temperature", "humidity", "rainfall"]
    raw_needed = [c for c in needed_cols if c in raw_weather]

    if raw_needed:
        if weather_df is not None and len(weather_df) >= len(df):
            for c in raw_needed:
                if c in weather_df.columns:
                    df[c] = weather_df[c].values[: len(df)]
                else:
                    df[c] = _safe_scalar(history[c]) if c in history.columns else 0.0
        else:
            for c in raw_needed:
                df[c] = _safe_scalar(history[c]) if c in history.columns else 0.0

    if "heat_index" in needed_cols:
        temp = df["temperature"] if "temperature" in df.columns else 0.0
        hum = df["humidity"] if "humidity" in df.columns else 0.0
        df["heat_index"] = temp + 0.33 * hum - 4.0

    if "temp_change_1h" in needed_cols:
        if "temperature" in df.columns:
            df["temp_change_1h"] = df["temperature"].diff().fillna(0.0)
        else:
            df["temp_change_1h"] = 0.0

    if "humidity_change_1h" in needed_cols:
        if "humidity" in df.columns:
            df["humidity_change_1h"] = df["humidity"].diff().fillna(0.0)
        else:
            df["humidity_change_1h"] = 0.0

    return df


# ---------------------------------------------------------------------------
# Energy lag features (from history only)
# ---------------------------------------------------------------------------

def _add_energy_lags(
    df: pd.DataFrame,
    history: pd.DataFrame,
    needed_cols: Sequence[str],
) -> pd.DataFrame:
    energy = history["energy"].dropna().astype(float) if "energy" in history.columns else pd.Series(dtype=float)

    lag_map = {
        "lag_1_energy": 1,
        "lag_2_energy": 2,
        "lag_24_energy": 24,
        "lag_48_energy": 48,
        "lag_168_energy": 168,
    }

    for col_name, hours in lag_map.items():
        if col_name not in needed_cols:
            continue
        vals = []
        for ts in df.index:
            lookup = ts - pd.Timedelta(hours=hours)
            if lookup in energy.index:
                vals.append(float(energy.loc[lookup]))
            else:
                # Fallback: mean of last `hours` readings, or last value
                window = energy.iloc[-hours:] if len(energy) >= hours else energy
                fallback = float(window.mean()) if not window.empty else 0.0
                vals.append(fallback)
        df[col_name] = vals

    return df


# ---------------------------------------------------------------------------
# B1-specific features
# ---------------------------------------------------------------------------

def _add_state_lags(df: pd.DataFrame, history: pd.DataFrame, needed_cols: Sequence[str]) -> pd.DataFrame:
    energy = history["energy"].dropna().astype(float) if "energy" in history.columns else pd.Series(dtype=float)

    if "lag_1_state" in needed_cols:
        last_energy = float(energy.iloc[-1]) if not energy.empty else 0.0
        df["lag_1_state"] = float(last_energy > _ACTIVE_THRESHOLD)

    if "lag_1_regime" in needed_cols:
        last_energy = float(energy.iloc[-1]) if not energy.empty else 0.0
        df["lag_1_regime"] = float(_classify_regime(last_energy))

    return df


def _add_rolling_active_shares(df: pd.DataFrame, history: pd.DataFrame, needed_cols: Sequence[str]) -> pd.DataFrame:
    energy = history["energy"].dropna().astype(float) if "energy" in history.columns else pd.Series(dtype=float)
    active = (energy > _ACTIVE_THRESHOLD).astype(float)

    if "rolling_active_share_6h" in needed_cols:
        window = active.iloc[-6:] if len(active) >= 6 else active
        df["rolling_active_share_6h"] = float(window.mean()) if not window.empty else 0.0

    if "rolling_active_share_24h" in needed_cols:
        window = active.iloc[-24:] if len(active) >= 24 else active
        df["rolling_active_share_24h"] = float(window.mean()) if not window.empty else 0.0

    return df


def _add_hours_since_last_active(df: pd.DataFrame, history: pd.DataFrame, needed_cols: Sequence[str]) -> pd.DataFrame:
    if "hours_since_last_active" not in needed_cols:
        return df
    energy = history["energy"].dropna().astype(float) if "energy" in history.columns else pd.Series(dtype=float)
    active_mask = energy > _ACTIVE_THRESHOLD
    if active_mask.any():
        last_active_idx = energy.index[active_mask][-1]
        hours = (df.index[0] - last_active_idx).total_seconds() / 3600.0
        df["hours_since_last_active"] = max(0.0, hours)
    else:
        df["hours_since_last_active"] = float(len(energy))
    return df


def _add_previous_day_features(df: pd.DataFrame, history: pd.DataFrame, needed_cols: Sequence[str]) -> pd.DataFrame:
    energy = history["energy"].dropna().astype(float) if "energy" in history.columns else pd.Series(dtype=float)

    # Get yesterday's data
    yesterday = (df.index[0] - pd.Timedelta(days=1)).normalize()
    today = df.index[0].normalize()
    mask = (energy.index >= yesterday) & (energy.index < today)
    yesterday_energy = energy[mask]

    if "previous_day_used" in needed_cols:
        df["previous_day_used"] = float((yesterday_energy > _ACTIVE_THRESHOLD).any()) if not yesterday_energy.empty else 0.0

    if "previous_day_total" in needed_cols:
        df["previous_day_total"] = float(yesterday_energy.sum()) if not yesterday_energy.empty else 0.0

    if "prev_day_total" in needed_cols:
        df["prev_day_total"] = float(yesterday_energy.sum()) if not yesterday_energy.empty else 0.0

    if "previous_day_night_active_flag" in needed_cols:
        if not yesterday_energy.empty:
            night_hours = set(range(18, 24)) | set(range(0, 6))
            night_mask = yesterday_energy.index.hour.isin(night_hours)
            df["previous_day_night_active_flag"] = float((yesterday_energy[night_mask] > _ACTIVE_THRESHOLD).any())
        else:
            df["previous_day_night_active_flag"] = 0.0

    if "previous_day_active_hours" in needed_cols:
        df["previous_day_active_hours"] = float((yesterday_energy > _ACTIVE_THRESHOLD).sum()) if not yesterday_energy.empty else 0.0

    if "previous_day_num_runs" in needed_cols:
        if not yesterday_energy.empty:
            active = (yesterday_energy > _ACTIVE_THRESHOLD).astype(int)
            transitions = active.diff().fillna(0)
            df["previous_day_num_runs"] = float((transitions == 1).sum())
        else:
            df["previous_day_num_runs"] = 0.0

    if "prev_day_late_evening_share" in needed_cols:
        if not yesterday_energy.empty and yesterday_energy.sum() > 0:
            late_mask = yesterday_energy.index.hour.isin([20, 21, 22, 23])
            df["prev_day_late_evening_share"] = float(yesterday_energy[late_mask].sum() / yesterday_energy.sum())
        else:
            df["prev_day_late_evening_share"] = 0.0

    return df


# ---------------------------------------------------------------------------
# Refrigerator B1-specific features
# ---------------------------------------------------------------------------

def _add_ref_b1_features(df: pd.DataFrame, history: pd.DataFrame, needed_cols: Sequence[str]) -> pd.DataFrame:
    energy = history["energy"].dropna().astype(float) if "energy" in history.columns else pd.Series(dtype=float)

    if "rolling_mean_6" in needed_cols:
        w = energy.iloc[-6:] if len(energy) >= 6 else energy
        df["rolling_mean_6"] = float(w.mean()) if not w.empty else 0.0

    if "rolling_std_6" in needed_cols:
        w = energy.iloc[-6:] if len(energy) >= 6 else energy
        df["rolling_std_6"] = float(w.std()) if len(w) > 1 else 0.0

    regimes = _classify_regime_series(energy) if not energy.empty else pd.Series(dtype=int)

    if "high_regime_share_6" in needed_cols:
        w = regimes.iloc[-6:] if len(regimes) >= 6 else regimes
        df["high_regime_share_6"] = float((w == 2).mean()) if not w.empty else 0.0

    if "high_regime_share_24" in needed_cols:
        w = regimes.iloc[-24:] if len(regimes) >= 24 else regimes
        df["high_regime_share_24"] = float((w == 2).mean()) if not w.empty else 0.0

    if "switch_count_6h" in needed_cols:
        w = regimes.iloc[-6:] if len(regimes) >= 6 else regimes
        df["switch_count_6h"] = float(w.diff().abs().sum()) if len(w) > 1 else 0.0

    if "rolling_range_6h" in needed_cols:
        w = energy.iloc[-6:] if len(energy) >= 6 else energy
        df["rolling_range_6h"] = float(w.max() - w.min()) if not w.empty else 0.0

    if "hours_since_high_cycle" in needed_cols:
        if not regimes.empty and (regimes == 2).any():
            last_high = regimes.index[regimes == 2][-1]
            hours = (df.index[0] - last_high).total_seconds() / 3600.0
            df["hours_since_high_cycle"] = max(0.0, hours)
        else:
            df["hours_since_high_cycle"] = float(len(regimes)) if not regimes.empty else 0.0

    if "trailing_same_regime_hours" in needed_cols:
        if not regimes.empty:
            last_regime = int(regimes.iloc[-1])
            count = 0
            for v in reversed(regimes.values):
                if int(v) == last_regime:
                    count += 1
                else:
                    break
            df["trailing_same_regime_hours"] = float(count)
        else:
            df["trailing_same_regime_hours"] = 0.0

    return df


# ---------------------------------------------------------------------------
# B2-specific features (rolling means, B1 probabilities)
# ---------------------------------------------------------------------------

def _add_rolling_energy_means(df: pd.DataFrame, history: pd.DataFrame, needed_cols: Sequence[str]) -> pd.DataFrame:
    energy = history["energy"].dropna().astype(float) if "energy" in history.columns else pd.Series(dtype=float)

    # Various naming conventions across appliances
    rm24_names = ["rolling_mean_energy_24h", "rolling_mean_24h", "rolling_mean_24"]
    rm168_names = ["rolling_mean_energy_168h", "rolling_mean_168h", "rolling_mean_168"]

    for name in rm24_names:
        if name in needed_cols:
            w = energy.iloc[-24:] if len(energy) >= 24 else energy
            df[name] = float(w.mean()) if not w.empty else 0.0

    for name in rm168_names:
        if name in needed_cols:
            w = energy.iloc[-168:] if len(energy) >= 168 else energy
            df[name] = float(w.mean()) if not w.empty else 0.0

    if "rolling_std_24" in needed_cols:
        w = energy.iloc[-24:] if len(energy) >= 24 else energy
        df["rolling_std_24"] = float(w.std()) if len(w) > 1 else 0.0

    return df


def _add_b1_probabilities(df: pd.DataFrame, b1_output: pd.DataFrame, needed_cols: Sequence[str]) -> pd.DataFrame:
    prob_cols = [c for c in b1_output.columns if c in needed_cols]
    for c in prob_cols:
        if c in b1_output.columns:
            df[c] = b1_output[c].values[: len(df)]
    return df


# ---------------------------------------------------------------------------
# B3-specific features (baseline, residual lags, domain)
# ---------------------------------------------------------------------------

def _add_baseline(
    df: pd.DataFrame,
    baseline_preds: np.ndarray,
    needed_cols: Sequence[str],
) -> pd.DataFrame:
    for name in ["baseline_prediction", "baseline_pred"]:
        if name in needed_cols:
            df[name] = baseline_preds[: len(df)]
    return df


def _add_residual_lags(
    df: pd.DataFrame,
    residual_history: pd.Series,
    needed_cols: Sequence[str],
) -> pd.DataFrame:
    if residual_history is None or residual_history.empty:
        for c in ["lag_1_residual", "lag_24_residual"]:
            if c in needed_cols:
                df[c] = 0.0
        return df

    if "lag_1_residual" in needed_cols:
        df["lag_1_residual"] = float(residual_history.iloc[-1])

    if "lag_24_residual" in needed_cols:
        vals = []
        for ts in df.index:
            lookup = ts - pd.Timedelta(hours=24)
            if lookup in residual_history.index:
                vals.append(float(residual_history.loc[lookup]))
            else:
                vals.append(float(residual_history.iloc[-1]))
        df["lag_24_residual"] = vals

    return df


def _add_rolling_residual_stats(
    df: pd.DataFrame,
    residual_history: pd.Series,
    needed_cols: Sequence[str],
) -> pd.DataFrame:
    if residual_history is None or residual_history.empty:
        for c in ["rolling_mean_residual_6h", "rolling_max_residual_6h",
                   "rolling_mean_resid_6", "rolling_absmax_resid_6"]:
            if c in needed_cols:
                df[c] = 0.0
        return df

    w = residual_history.iloc[-6:] if len(residual_history) >= 6 else residual_history

    if "rolling_mean_residual_6h" in needed_cols:
        df["rolling_mean_residual_6h"] = float(w.mean())

    if "rolling_max_residual_6h" in needed_cols:
        df["rolling_max_residual_6h"] = float(w.max())

    if "rolling_mean_resid_6" in needed_cols:
        df["rolling_mean_resid_6"] = float(w.mean())

    if "rolling_absmax_resid_6" in needed_cols:
        df["rolling_absmax_resid_6"] = float(w.abs().max())

    return df


def _add_domain_features(
    df: pd.DataFrame,
    history: pd.DataFrame,
    needed_cols: Sequence[str],
) -> pd.DataFrame:
    energy = history["energy"].dropna().astype(float) if "energy" in history.columns else pd.Series(dtype=float)

    # Peak window flags (various names): 13:00-17:59 is peak
    for name in ["active_peak_window_flag", "peak_window_flag", "is_peak_window"]:
        if name in needed_cols:
            df[name] = df.index.hour.isin(range(13, 18)).astype(float)

    if "run_length_so_far" in needed_cols:
        if not energy.empty:
            active = energy > _ACTIVE_THRESHOLD
            count = 0
            for v in reversed(active.values):
                if v:
                    count += 1
                else:
                    break
            df["run_length_so_far"] = float(count)
        else:
            df["run_length_so_far"] = 0.0

    if "recent_switch_flag" in needed_cols:
        if not energy.empty:
            regimes = _classify_regime_series(energy)
            w = regimes.iloc[-3:] if len(regimes) >= 3 else regimes
            df["recent_switch_flag"] = float(w.diff().abs().sum() > 0) if len(w) > 1 else 0.0
        else:
            df["recent_switch_flag"] = 0.0

    if "energy_change_lag1" in needed_cols:
        if len(energy) >= 2:
            df["energy_change_lag1"] = float(energy.iloc[-1] - energy.iloc[-2])
        else:
            df["energy_change_lag1"] = 0.0

    if "energy_vs_lag24" in needed_cols:
        if len(energy) >= 25:
            df["energy_vs_lag24"] = float(energy.iloc[-1] - energy.iloc[-25])
        else:
            df["energy_vs_lag24"] = 0.0

    if "hours_since_low_recovery" in needed_cols:
        if not energy.empty:
            regimes = _classify_regime_series(energy)
            # Find last transition from low (0) to normal/high (1 or 2)
            diffs = regimes.diff()
            recovery_mask = (diffs > 0) & (regimes.shift(1) == 0)
            if recovery_mask.any():
                last_recovery = regimes.index[recovery_mask][-1]
                hours = (df.index[0] - last_recovery).total_seconds() / 3600.0
                df["hours_since_low_recovery"] = max(0.0, hours)
            else:
                df["hours_since_low_recovery"] = float(len(regimes))
        else:
            df["hours_since_low_recovery"] = 0.0

    if "current_regime_run_length" in needed_cols:
        if not energy.empty:
            regimes = _classify_regime_series(energy)
            last_regime = int(regimes.iloc[-1])
            count = 0
            for v in reversed(regimes.values):
                if int(v) == last_regime:
                    count += 1
                else:
                    break
            df["current_regime_run_length"] = float(count)
        else:
            df["current_regime_run_length"] = 0.0

    return df


# ===========================================================================
# Public API
# ===========================================================================

def build_b1_features(
    appliance: str,
    history: pd.DataFrame,
    future_idx: pd.DatetimeIndex,
    weather_df: Optional[pd.DataFrame],
    b1_params: Dict[str, Any],
) -> pd.DataFrame:
    """Build feature matrix for B1 stage (sklearn classifier)."""
    cols = list(b1_params["feature_usage"]["used_feature_columns"])
    df = pd.DataFrame(index=future_idx, dtype=float)

    df = _add_calendar(df)
    df = _add_weather(df, weather_df, history, cols)
    df = _add_energy_lags(df, history, cols)
    df = _add_state_lags(df, history, cols)
    df = _add_rolling_active_shares(df, history, cols)
    df = _add_hours_since_last_active(df, history, cols)
    df = _add_previous_day_features(df, history, cols)
    df = _add_ref_b1_features(df, history, cols)

    return _fill_and_reindex(df, cols, history)


def build_b2_features(
    appliance: str,
    history: pd.DataFrame,
    future_idx: pd.DatetimeIndex,
    weather_df: Optional[pd.DataFrame],
    b1_output: pd.DataFrame,
    b2_params: Dict[str, Any],
) -> pd.DataFrame:
    """Build exogenous feature matrix for B2 stage (SARIMAX baseline)."""
    cols = list(b2_params["data_usage"]["exog_columns"])
    df = pd.DataFrame(index=future_idx, dtype=float)

    df = _add_calendar(df)
    df = _add_weather(df, weather_df, history, cols)
    df = _add_b1_probabilities(df, b1_output, cols)
    df = _add_energy_lags(df, history, cols)
    df = _add_rolling_energy_means(df, history, cols)
    df = _add_previous_day_features(df, history, cols)

    return _fill_and_reindex(df, cols, history)


def build_b3_features(
    appliance: str,
    history: pd.DataFrame,
    future_idx: pd.DatetimeIndex,
    weather_df: Optional[pd.DataFrame],
    b1_output: pd.DataFrame,
    baseline_preds: np.ndarray,
    residual_history: Optional[pd.Series],
    b3_params: Dict[str, Any],
) -> pd.DataFrame:
    """Build exogenous feature matrix for B3 stage (SARIMAX residual)."""
    cols = list(b3_params["data_usage"]["exog_columns"])
    df = pd.DataFrame(index=future_idx, dtype=float)

    df = _add_calendar(df)
    df = _add_weather(df, weather_df, history, cols)
    df = _add_b1_probabilities(df, b1_output, cols)
    df = _add_baseline(df, baseline_preds, cols)
    df = _add_residual_lags(df, residual_history, cols)
    df = _add_rolling_residual_stats(df, residual_history, cols)
    df = _add_domain_features(df, history, cols)

    return _fill_and_reindex(df, cols, history)
