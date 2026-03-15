"""
forecasting/pipeline/weather.py
================================
Fetches 48-h hourly weather forecast from Open-Meteo (free, no API key).
Returns only the 24 rows matching the target forecast date (next day).
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Optional

import pandas as pd
import requests

log = logging.getLogger("sarimax_pipeline.weather")

# Open-Meteo free endpoint (no API key required)
_OPEN_METEO_URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude={lat}&longitude={lon}"
    "&hourly=temperature_2m,relativehumidity_2m,precipitation"
    "&timezone=Asia%2FManila"
    "&forecast_days=2"
)


def fetch_weather_forecast(
    lat: float,
    lon: float,
    target_date: date,
    timeout: int = 15,
) -> Optional[pd.DataFrame]:
    """
    Fetch 24-row hourly weather forecast for *target_date*.

    Returns a DataFrame indexed by hourly timestamp with columns:
        temperature, humidity, rainfall

    Returns None on any network/parse error (caller must handle gracefully).
    """
    url = _OPEN_METEO_URL.format(lat=lat, lon=lon)
    log.info("Fetching weather from Open-Meteo: lat=%s lon=%s", lat, lon)

    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as exc:
        log.error("Weather API request failed: %s", exc)
        return None

    try:
        hourly = data["hourly"]
        df = pd.DataFrame({
            "timestamp":   pd.to_datetime(hourly["time"]),
            "temperature": hourly["temperature_2m"],
            "humidity":    hourly["relativehumidity_2m"],
            "rainfall":    hourly["precipitation"],
        })
        df = df.set_index("timestamp")

        # Slice to target date only (24 rows: 00:00 → 23:00)
        start = pd.Timestamp(target_date)
        end   = start + pd.Timedelta(hours=23)
        df    = df.loc[start:end]

        if len(df) != 24:
            log.warning(
                "Expected 24 weather rows for %s, got %d. "
                "Rows outside the target date will be forward-filled.",
                target_date, len(df),
            )

        log.info(
            "Weather fetched: %d rows | temp range %.1f–%.1f°C",
            len(df), df["temperature"].min(), df["temperature"].max(),
        )
        return df.astype(float)

    except (KeyError, ValueError) as exc:
        log.error("Weather API response parsing failed: %s", exc)
        return None


def fallback_weather(
    future_idx: pd.DatetimeIndex,
    history: pd.DataFrame,
    cols: list[str],
) -> pd.DataFrame:
    """
    When the weather API is unavailable, forward-fill from the last observed
    weather row.  This is a last-resort fallback only.
    """
    log.warning("Using forward-fill fallback for weather features: %s", cols)
    last = history[cols].dropna().iloc[-1]
    df = pd.DataFrame(
        {c: last[c] for c in cols},
        index=future_idx,
    )
    return df.astype(float)
