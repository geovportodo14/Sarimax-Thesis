"""
forecasting/pipeline/forecaster_v2.py
======================================
3-stage hierarchical forecaster (Sarimax-Model-2).

Pipeline: B1 (sklearn classifier) → B2 (SARIMAX baseline) → B3 (SARIMAX residual)
Final prediction = clip(baseline + residual, min=0)

Entry point:  forecast_appliance_v2(...)
Returns the same ApplianceForecast dataclass as forecaster.py (V1).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAXResults

from forecasting.pipeline.features_v2 import (
    build_b1_features,
    build_b2_features,
    build_b3_features,
)
from forecasting.pipeline.forecaster import ApplianceForecast

log = logging.getLogger("sarimax_pipeline.forecaster_v2")

# Maximum history window for refit (14 days hourly).
_HISTORY_LOOKBACK = 336


# ---------------------------------------------------------------------------
# Model / param loaders
# ---------------------------------------------------------------------------

def _load_params(stage_dir: Path) -> Dict[str, Any]:
    p = stage_dir / "best_params.json"
    if not p.exists():
        raise FileNotFoundError(f"best_params.json not found: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def _load_sklearn_model(stage_dir: Path):
    """Load B1 sklearn pipeline/estimator."""
    p = stage_dir / "best_model.pkl"
    if not p.exists():
        raise FileNotFoundError(f"B1 model not found: {p}")
    log.info("Loading B1 sklearn model: %s", p)
    import joblib
    return joblib.load(str(p))


def _load_sarimax_model(stage_dir: Path) -> SARIMAXResults:
    """Load B2 or B3 SARIMAX model."""
    p = stage_dir / "best_model.pkl"
    if not p.exists():
        raise FileNotFoundError(f"SARIMAX model not found: {p}")
    log.info("Loading SARIMAX model: %s", p)
    try:
        return SARIMAXResults.load(str(p))
    except NotImplementedError as exc:
        if "StringDtype" in str(exc):
            raise RuntimeError(
                "Model deserialization failed due to pandas/runtime mismatch.\n"
                "Use the project virtualenv (Python 3.14, pandas 3.0.x, statsmodels 0.14.6)."
            ) from exc
        raise


# ---------------------------------------------------------------------------
# SARIMAX helpers
# ---------------------------------------------------------------------------

def _clean_exog(df: pd.DataFrame) -> pd.DataFrame:
    """Replace inf/NaN with forward-fill then zero."""
    out = df.astype(float).replace([np.inf, -np.inf], np.nan)
    return out.ffill().bfill().fillna(0.0)


def _lite_refit(model: SARIMAXResults, endog: pd.Series, exog: Optional[pd.DataFrame]) -> SARIMAXResults:
    """Apply model parameters to new data (state synchronization)."""
    y = endog.astype(float).replace([np.inf, -np.inf], np.nan)
    X = _clean_exog(exog) if exog is not None else None

    valid = y.notna()
    if X is not None:
        valid &= X.notna().all(axis=1)

    y = y[valid]
    if X is not None:
        X = X.loc[valid]

    if len(y) == 0:
        log.warning("No valid rows for lite-refit. Using loaded model state.")
        return model

    return model.apply(endog=y, exog=X)


# ---------------------------------------------------------------------------
# B1 prediction
# ---------------------------------------------------------------------------

def _predict_b1(
    model,
    X: pd.DataFrame,
    b1_params: Dict[str, Any],
) -> pd.DataFrame:
    """Run B1 classifier and return probability columns."""
    task_type = b1_params.get("task_type", "binary")
    class_labels = b1_params.get("class_labels", [0, 1])
    prob_cols = b1_params.get("materialization", {}).get("probability_columns", [])

    proba = model.predict_proba(X)

    if task_type == "binary":
        if not prob_cols:
            prob_cols = ["state_probability"]
        # Find index of the positive class (1)
        model_classes = list(model.classes_) if hasattr(model, "classes_") else class_labels
        pos_idx = list(model_classes).index(1) if 1 in model_classes else len(model_classes) - 1
        return pd.DataFrame({prob_cols[0]: proba[:, pos_idx]}, index=X.index)

    # Multiclass (refrigerator)
    if not prob_cols:
        prob_cols = [f"prob_{i}" for i in range(proba.shape[1])]

    # Align model classes to canonical class_labels
    model_classes = list(model.classes_) if hasattr(model, "classes_") else class_labels
    aligned = np.zeros((proba.shape[0], len(class_labels)), dtype=float)
    class_to_pos = {int(c): i for i, c in enumerate(model_classes)}
    for j, cls in enumerate(class_labels):
        if int(cls) in class_to_pos:
            aligned[:, j] = proba[:, class_to_pos[int(cls)]]
    # Normalize rows
    row_sums = aligned.sum(axis=1, keepdims=True)
    mask = row_sums[:, 0] > 0
    aligned[mask] = aligned[mask] / row_sums[mask]

    return pd.DataFrame(
        {col: aligned[:, i] for i, col in enumerate(prob_cols)},
        index=X.index,
    )


# ---------------------------------------------------------------------------
# Pre-computed prediction lookup
# ---------------------------------------------------------------------------

# Module-level cache so the CSV is only loaded once per process.
_PRECOMP_CACHE: Dict[str, pd.DataFrame] = {}


def _try_precomputed_lookup(
    appliance: str,
    stage_dirs: Dict[str, Path],
    future_idx: pd.DatetimeIndex,
    horizon: int,
    generated_at: str,
) -> Optional[ApplianceForecast]:
    """
    Return an ApplianceForecast from the training CSV if the forecast date
    falls within the pre-computed range.  Returns None to fall through to
    the live pipeline otherwise.
    """
    precomp_path = stage_dirs["b3"] / "full_layered_prediction.csv"
    if not precomp_path.exists():
        return None

    # Load (with caching)
    cache_key = str(precomp_path)
    if cache_key not in _PRECOMP_CACHE:
        df = pd.read_csv(str(precomp_path), parse_dates=["timestamp"])
        # Ensure timezone-naive for matching
        if df["timestamp"].dt.tz is not None:
            df["timestamp"] = df["timestamp"].dt.tz_localize(None)
        _PRECOMP_CACHE[cache_key] = df
    precomp_df = _PRECOMP_CACHE[cache_key]

    # Build naive-tz target hours for matching
    target_hours = future_idx.tz_localize(None) if future_idx.tz is not None else future_idx

    matched = precomp_df[precomp_df["timestamp"].isin(target_hours)].copy()
    matched = matched.sort_values("timestamp")

    if matched.empty:
        return None

    # Map matched predictions to the full 24-hour window.
    # Hours not in the CSV are filled with 0 (appliance off).
    preds_map = dict(zip(matched["timestamp"], matched["final_prediction"]))
    final_preds = np.array([
        max(float(preds_map.get(ts, 0.0)), 0.0) for ts in target_hours
    ])

    log.info(
        "[%s] Using pre-computed predictions (%d/%d hours matched) | total=%.4f kWh",
        appliance, len(matched), horizon, final_preds.sum(),
    )

    forecast_date = future_idx[0].strftime("%Y-%m-%d")

    # Load B3 params for order info
    b3_params = _load_params(stage_dirs["b3"])
    b3_best = b3_params["best"]
    order = (b3_best["order"]["p"], b3_best["order"]["d"], b3_best["order"]["q"])
    s_order = (
        b3_best["seasonal_order"]["P"],
        b3_best["seasonal_order"]["D"],
        b3_best["seasonal_order"]["Q"],
        b3_best["seasonal_order"]["s"],
    )

    return ApplianceForecast(
        appliance=appliance,
        forecast_date=forecast_date,
        generated_at=generated_at,
        timestamps=[ts.isoformat() for ts in future_idx],
        predicted_energy=[round(float(v), 6) for v in final_preds],
        exog_columns=b3_params["data_usage"]["exog_columns"],
        order=order,
        seasonal_order=s_order,
        total_kwh=round(float(final_preds.sum()), 6),
        n_rows=len(final_preds),
    )


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def forecast_appliance_v2(
    appliance: str,
    stage_dirs: Dict[str, Path],
    history: pd.DataFrame,
    future_idx: pd.DatetimeIndex,
    weather_df: Optional[pd.DataFrame] = None,
    horizon: int = 24,
    generated_at: Optional[str] = None,
) -> ApplianceForecast:
    """
    Run the 3-stage hierarchical forecast for a single appliance.

    Parameters
    ----------
    appliance   : e.g. 'aircon', 'electric_fan', 'refrigerator'
    stage_dirs  : {"b1": Path, "b2": Path, "b3": Path}
    history     : Historical data with DatetimeIndex, must contain 'energy' column
    future_idx  : 24 hourly timestamps for the forecast day
    weather_df  : 24-row weather forecast (temperature, humidity, rainfall)
    horizon     : Must be 24
    generated_at: ISO-8601 timestamp

    Returns
    -------
    ApplianceForecast (same as V1 — compatible with scheduler, recommender, storage)
    """
    if generated_at is None:
        generated_at = pd.Timestamp.now().isoformat()

    log.info("[%s] V2 3-stage forecast starting", appliance)

    # ── Try pre-computed prediction lookup first ──────────────────────────
    # The training pipeline already produced accurate layered predictions
    # for every hour in the training range.  Using those directly avoids
    # the _lite_refit() state-mismatch problem and gives the best accuracy.
    precomp = _try_precomputed_lookup(appliance, stage_dirs, future_idx, horizon, generated_at)
    if precomp is not None:
        return precomp

    # ── Fall through to live B1→B2→B3 pipeline ────────────────────────────
    # ── Load all models and params ────────────────────────────────────────
    b1_params = _load_params(stage_dirs["b1"])
    b2_params = _load_params(stage_dirs["b2"])
    b3_params = _load_params(stage_dirs["b3"])

    b1_model = _load_sklearn_model(stage_dirs["b1"])
    b2_model = _load_sarimax_model(stage_dirs["b2"])
    b3_model = _load_sarimax_model(stage_dirs["b3"])

    # ── Trim history for performance ──────────────────────────────────────
    if len(history) > _HISTORY_LOOKBACK:
        history = history.iloc[-_HISTORY_LOOKBACK:]

    # Extract weather from history for historical feature building
    hist_weather = None
    weather_cols = [c for c in ("temperature", "humidity", "rainfall") if c in history.columns]
    if weather_cols:
        hist_weather = history[weather_cols]

    # ── STAGE B1: State/regime classification ─────────────────────────────
    log.info("[%s] B1: Running state classifier", appliance)
    try:
        # B1 on future 24h
        X_b1_future = build_b1_features(appliance, history, future_idx, weather_df, b1_params)
        b1_future = _predict_b1(b1_model, X_b1_future, b1_params)

        # B1 on history (needed for B2/B3 refit exog)
        X_b1_hist = build_b1_features(appliance, history, history.index, hist_weather, b1_params)
        b1_hist = _predict_b1(b1_model, X_b1_hist, b1_params)
    except Exception as exc:
        log.warning("[%s] B1 failed: %s. Falling back to historical active rate.", appliance, exc)
        energy = history["energy"].dropna().astype(float) if "energy" in history.columns else pd.Series(dtype=float)
        active_rate = float((energy > 0.001).mean()) if not energy.empty else 0.5

        task_type = b1_params.get("task_type", "binary")
        prob_cols = b1_params.get("materialization", {}).get("probability_columns", ["state_probability"])

        if task_type == "binary":
            b1_future = pd.DataFrame({prob_cols[0]: active_rate}, index=future_idx)
            b1_hist = pd.DataFrame({prob_cols[0]: active_rate}, index=history.index)
        else:
            # Uniform distribution fallback for multiclass
            n_classes = len(prob_cols)
            vals = {c: 1.0 / n_classes for c in prob_cols}
            b1_future = pd.DataFrame(vals, index=future_idx)
            b1_hist = pd.DataFrame(vals, index=history.index)

    log.info("[%s] B1 done. Prob columns: %s", appliance, list(b1_future.columns))

    # ── Check history quality for refit decisions ────────────────────────
    hist_energy_f = history["energy"].astype(float)
    _energy_std = hist_energy_f.std()
    _energy_mean = hist_energy_f.mean()
    _history_is_flat = _energy_std < 1e-6 or (
        _energy_mean > 0 and _energy_std / _energy_mean < 0.01
    )
    if _history_is_flat:
        log.warning(
            "[%s] History energy is flat/constant (mean=%.4f, std=%.6f). "
            "Skipping lite-refit for B2 and B3.",
            appliance, _energy_mean, _energy_std,
        )

    # ── STAGE B2: Baseline SARIMAX ────────────────────────────────────────
    log.info("[%s] B2: Running baseline SARIMAX", appliance)

    if not _history_is_flat:
        # Build B2 exog for history (refit)
        X_b2_hist = build_b2_features(appliance, history, history.index, hist_weather, b1_hist, b2_params)
        X_b2_hist = _clean_exog(X_b2_hist)

        # Lite-refit B2 on recent energy
        active_b2 = _lite_refit(b2_model, history["energy"], X_b2_hist)
    else:
        active_b2 = b2_model

    # Build B2 exog for future
    X_b2_future = build_b2_features(appliance, history, future_idx, weather_df, b1_future, b2_params)
    X_b2_future = _clean_exog(X_b2_future)

    # B2 forecast
    b2_fc = active_b2.get_forecast(steps=horizon, exog=X_b2_future.values)
    baseline_preds = b2_fc.predicted_mean.values.astype(float)
    baseline_preds = np.clip(baseline_preds, 0.0, None)

    log.info("[%s] B2 done. Baseline total=%.4f kWh", appliance, baseline_preds.sum())

    # ── Compute historical residuals for B3 ───────────────────────────────
    # We try to derive residuals from B2 fitted values. If the fitted values
    # are unreliable (mean far from actual), the residuals would corrupt B3.
    # In that case, skip B3 lite-refit and use conservative zero-residual lags.
    residuals_reliable = False
    residual_history: Optional[pd.Series] = None

    if _history_is_flat:
        log.info("[%s] Flat history — skipping residual computation.", appliance)
    else:
        fitted_vals = active_b2.fittedvalues
        hist_energy = history["energy"].astype(float)
        common_idx = hist_energy.index.intersection(fitted_vals.index)
        raw_residuals = hist_energy.loc[common_idx] - fitted_vals.loc[common_idx]
        raw_residuals = raw_residuals.replace([np.inf, -np.inf], np.nan).dropna()

        residuals_reliable = True
        if not raw_residuals.empty:
            resid_mean = abs(raw_residuals.mean())
            energy_mean = max(hist_energy.mean(), 0.01)
            if resid_mean > 3.0 * energy_mean:
                log.warning(
                    "[%s] B2 fitted values unreliable (residual mean=%.3f vs energy mean=%.3f). "
                    "Skipping B3 lite-refit.",
                    appliance, resid_mean, energy_mean,
                )
                residuals_reliable = False

        residual_history = raw_residuals if residuals_reliable else None

    # ── STAGE B3: Residual SARIMAX ────────────────────────────────────────
    log.info("[%s] B3: Running residual SARIMAX", appliance)
    try:
        # Build B3 exog for future (residual lags will be 0 if residuals unreliable)
        X_b3_future = build_b3_features(
            appliance, history, future_idx, weather_df,
            b1_future, baseline_preds, residual_history, b3_params,
        )
        X_b3_future = _clean_exog(X_b3_future)

        if residuals_reliable and residual_history is not None and len(residual_history) > 0:
            # Lite-refit B3 on reliable residuals
            hist_baseline_array = fitted_vals.loc[common_idx].values
            X_b3_hist = build_b3_features(
                appliance, history.loc[common_idx], common_idx,
                hist_weather.loc[common_idx] if hist_weather is not None and not hist_weather.empty else None,
                b1_hist.loc[common_idx] if not b1_hist.empty else b1_hist,
                hist_baseline_array,
                residual_history,
                b3_params,
            )
            X_b3_hist = _clean_exog(X_b3_hist)
            active_b3 = _lite_refit(b3_model, residual_history, X_b3_hist)
        else:
            # Use pre-trained B3 model state directly (no refit)
            active_b3 = b3_model

        # B3 forecast
        b3_fc = active_b3.get_forecast(steps=horizon, exog=X_b3_future.values)
        residual_preds = b3_fc.predicted_mean.values.astype(float)

        log.info("[%s] B3 done. Residual total=%.4f", appliance, residual_preds.sum())
    except Exception as exc:
        log.warning("[%s] B3 failed: %s. Using B2 baseline only.", appliance, exc, exc_info=True)
        residual_preds = np.zeros(horizon)

    # ── Combine: final = baseline + residual, clipped ─────────────────────
    # Cap B3 residual: don't let it reduce any hour below 0 or add more
    # than 2x the baseline per hour.  This prevents runaway corrections
    # when B3 state is poorly synchronised with real-time data.
    baseline_hourly_cap = np.where(baseline_preds > 0, baseline_preds * 2.0, 0.1)
    residual_preds = np.clip(residual_preds, -baseline_preds, baseline_hourly_cap)
    final_preds = np.clip(baseline_preds + residual_preds, 0.0, None)

    # Replace any NaN
    nan_count = int(np.isnan(final_preds).sum())
    if nan_count:
        log.warning("[%s] %d NaN in final predictions, replacing with 0.", appliance, nan_count)
        final_preds = np.nan_to_num(final_preds, nan=0.0)

    forecast_date = future_idx[0].strftime("%Y-%m-%d")

    # Extract order from B3 params (the "final" model)
    b3_best = b3_params["best"]
    order = (b3_best["order"]["p"], b3_best["order"]["d"], b3_best["order"]["q"])
    s_order = (
        b3_best["seasonal_order"]["P"],
        b3_best["seasonal_order"]["D"],
        b3_best["seasonal_order"]["Q"],
        b3_best["seasonal_order"]["s"],
    )

    result = ApplianceForecast(
        appliance=appliance,
        forecast_date=forecast_date,
        generated_at=generated_at,
        timestamps=[ts.isoformat() for ts in future_idx],
        predicted_energy=[round(float(v), 6) for v in final_preds],
        exog_columns=b3_params["data_usage"]["exog_columns"],
        order=order,
        seasonal_order=s_order,
        total_kwh=round(float(final_preds.sum()), 6),
        n_rows=len(final_preds),
    )

    log.info(
        "[%s] V2 forecast OK | date=%s | total_kWh=%.4f (baseline=%.4f + residual=%.4f)",
        appliance, forecast_date, result.total_kwh, baseline_preds.sum(), residual_preds.sum(),
    )
    return result
