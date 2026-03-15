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
_FORECAST_URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude={lat}&longitude={lon}"
    "&hourly=temperature_2m,relativehumidity_2m,precipitation"
    "&timezone=Asia%2FManila"
    "&forecast_days=2"
)

_ARCHIVE_URL = (
    "https://archive-api.open-meteo.com/v1/archive"
    "?latitude={lat}&longitude={lon}"
    "&start_date={date}&end_date={date}"
    "&hourly=temperature_2m,relative_humidity_2m,precipitation"
    "&timezone=Asia%2FManila"
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
    today = date.today()
    
    if target_date < today:
        log.info("Target date %s is in the past; fetching from Archive API.", target_date)
        url = _ARCHIVE_URL.format(lat=lat, lon=lon, date=target_date)
    else:
        log.info("Target date %s is today/future; fetching from Forecast API.", target_date)
        url = _FORECAST_URL.format(lat=lat, lon=lon)

    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as exc:
        log.error("Weather API request failed: %s", exc)
        return None

    try:
        hourly = data["hourly"]
        # Archive API uses 'relative_humidity_2m', Forecast API uses 'relativehumidity_2m'
        hum_key = "relative_humidity_2m" if "relative_humidity_2m" in hourly else "relativehumidity_2m"
        
        df = pd.DataFrame({
            "timestamp":   pd.to_datetime(hourly["time"]),
            "temperature": hourly["temperature_2m"],
            "humidity":    hourly[hum_key],
            "rainfall":    hourly["precipitation"],
        })
        df = df.set_index("timestamp")

        # Slice to target date only (24 rows: 00:00 → 23:00)
        start = pd.Timestamp(target_date)
        end   = start + pd.Timedelta(hours=23)
        df    = df.loc[start:end]

        if len(df) != 24:
            log.warning(
                "Expected 24 weather rows for %s, got %d.",
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
