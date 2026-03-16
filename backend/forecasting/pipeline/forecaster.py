"""
forecasting/pipeline/forecaster.py
====================================
Loads a trained SARIMAX model + best_params.json and produces a 24-step
hourly forecast for a single appliance.

Entry point:  forecast_appliance(...)
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAXResults

log = logging.getLogger("sarimax_pipeline.forecaster")


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class ApplianceForecast:
    """Validated result for a single appliance."""
    appliance:      str
    forecast_date:  str              # YYYY-MM-DD (next day)
    generated_at:   str              # ISO-8601
    timestamps:     List[str]
    predicted_energy: List[float]    # hourly kWh predictions, ≥ 0
    exog_columns:   List[str]
    order:          tuple
    seasonal_order: tuple
    total_kwh:      float            # sum of 24 hourly values
    n_rows:         int

    def to_records(self, tariff: float) -> List[Dict[str, Any]]:
        """Expand into one dict per hour for database/CSV storage."""
        records = []
        for ts, energy in zip(self.timestamps, self.predicted_energy):
            records.append({
                "appliance":        self.appliance,
                "timestamp":        ts,
                "predicted_energy": round(energy, 6),
                "predicted_cost":   round(energy * tariff, 4),
                "forecast_date":    self.forecast_date,
                "generated_at":     self.generated_at,
            })
        return records


# ---------------------------------------------------------------------------
# Model loading helpers
# ---------------------------------------------------------------------------

def load_best_params(model_dir: Path) -> Dict[str, Any]:
    p = model_dir / "best_params.json"
    if not p.exists():
        raise FileNotFoundError(f"best_params.json not found: {p}")
    params = json.loads(p.read_text(encoding="utf-8"))
    log.debug("Loaded best_params.json from %s", p)
    return params


def load_best_model(model_dir: Path) -> SARIMAXResults:
    p = model_dir / "best_model.pkl"
    if not p.exists():
        raise FileNotFoundError(f"best_model.pkl not found: {p}")
    log.info("Loading model: %s", p)
    try:
        return SARIMAXResults.load(str(p))
    except NotImplementedError as exc:
        # Common compatibility issue: model pickles serialized with newer pandas
        # StringDtype internals cannot be restored in older runtimes.
        if "StringDtype" in str(exc):
            raise RuntimeError(
                "Model deserialization failed due to pandas/runtime mismatch.\n"
                "Use the project virtualenv/interpreter that matches model training.\n"
                "Recommended: backend/venv/bin/python3 (Python 3.14, pandas 3.0.x, statsmodels 0.14.6).\n"
                "Do not run the pipeline with legacy Python 3.9 site-packages."
            ) from exc
        raise


# ---------------------------------------------------------------------------
# Forecast timestamps
# ---------------------------------------------------------------------------

def build_forecast_index(last_actual_ts: pd.Timestamp, horizon: int = 24) -> pd.DatetimeIndex:
    """
    Given the last *actual* data timestamp (ideally 23:00 of today),
    return exactly `horizon` hourly timestamps starting at 00:00 next day.

    Example:
        last_actual_ts = 2026-03-13 23:00
        returns  DatetimeIndex(['2026-03-14 00:00', ..., '2026-03-14 23:00'])
    """
    # Ensure we start at 00:00 of the day FOLLOWING the last actual timestamp
    next_day = (last_actual_ts + pd.Timedelta(days=1)).normalize()
    idx = pd.date_range(start=next_day, periods=horizon, freq="h")
    log.info("Forecast window: %s → %s (%d steps)", idx[0], idx[-1], len(idx))
    return idx


# ---------------------------------------------------------------------------
# Core forecast function
# ---------------------------------------------------------------------------

def forecast_appliance(
    appliance: str,
    model_dir: Path,
    future_exog: pd.DataFrame,
    future_idx: pd.DatetimeIndex,
    history: Optional[pd.DataFrame] = None,
    horizon: int = 24,
    generated_at: Optional[str] = None,
) -> ApplianceForecast:
    """
    Run SARIMAX forecast for a single appliance.

    Parameters
    ----------
    appliance    : Friendly name (e.g. 'aircon').
    model_dir    : Path to folder containing best_model.pkl + best_params.json.
    future_exog  : DataFrame (shape: 24 × exog_cols) built by features.build_future_exog.
    future_idx   : DatetimeIndex of the 24 forecast timestamps.
    horizon      : Must be 24.
    generated_at : ISO-8601 string; injected at runtime.

    Returns
    -------
    ApplianceForecast (validated, non-negative predictions, ready for storage)
    """
    if generated_at is None:
        generated_at = pd.Timestamp.now().isoformat()

    params         = load_best_params(model_dir)
    model_result   = load_best_model(model_dir)

    best       = params["best"]
    order      = (best["order"]["p"], best["order"]["d"], best["order"]["q"])
    s_order    = (
        best["seasonal_order"]["P"],
        best["seasonal_order"]["D"],
        best["seasonal_order"]["Q"],
        best["seasonal_order"]["s"],
    )
    exog_cols  = params.get("exog_columns", [])

    # Validate future_exog alignment
    if exog_cols and list(future_exog.columns) != exog_cols:
        raise ValueError(
            f"[{appliance}] future_exog column mismatch.\n"
            f"  Expected : {exog_cols}\n"
            f"  Got      : {list(future_exog.columns)}"
        )

    if len(future_exog) != horizon:
        raise ValueError(
            f"[{appliance}] future_exog must have {horizon} rows, got {len(future_exog)}"
        )

    log.info("[%s] Running get_forecast(steps=%d)", appliance, horizon)
    try:
        # ── Lite Refit (State Update) ────────────────────────────────────────
        # We 'apply' the model to the recent history to synchronize internal
        # states (filters) with actual observations before forecasting.
        active_model = model_result
        if history is not None and not history.empty:
            log.info("[%s] Applying 'Lite Refit' (State Update) using %d history rows.", appliance, len(history))
            
            # Align history columns with exog_cols
            y_hist = history["energy"].astype(float)
            X_hist = None
            if exog_cols:
                # Ensure all required columns exist in history
                missing = [c for c in exog_cols if c not in history.columns]
                if missing:
                    log.warning("[%s] History missing exog cols for Lite-Refit: %s. Filling with 0.", appliance, missing)
                    for c in missing: history[c] = 0.0
                X_hist = history[exog_cols].astype(float)

            # Apply parameters to the new data window
            active_model = model_result.apply(endog=y_hist, exog=X_hist)

        fc = active_model.get_forecast(
            steps=horizon,
            exog=future_exog.values if exog_cols else None,
        )
        preds = fc.predicted_mean.values
    except Exception as exc:
        raise RuntimeError(f"[{appliance}] SARIMAX get_forecast failed: {exc}") from exc

    # ── Post-process ─────────────────────────────────────────────────────────
    preds = preds.clip(min=0.0)      # energy cannot be negative

    n_nan = int(pd.isna(preds).sum())
    if n_nan:
        log.warning("[%s] %d NaN predictions replaced with 0.", appliance, n_nan)
        preds = pd.Series(preds).fillna(0.0).values

    forecast_date = future_idx[0].strftime("%Y-%m-%d")

    result = ApplianceForecast(
        appliance       = appliance,
        forecast_date   = forecast_date,
        generated_at    = generated_at,
        timestamps      = [ts.isoformat() for ts in future_idx],
        predicted_energy= [round(float(v), 6) for v in preds],
        exog_columns    = exog_cols,
        order           = order,
        seasonal_order  = s_order,
        total_kwh       = round(float(preds.sum()), 6),
        n_rows          = len(preds),
    )

    log.info(
        "[%s] Forecast OK | date=%s | total_kWh=%.4f",
        appliance, forecast_date, result.total_kwh,
    )
    return result
