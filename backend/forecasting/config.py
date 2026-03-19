"""
forecasting/config.py
=====================
Central configuration for the SARIMAX daily forecasting pipeline.
All environment-sensitive values are read from environment variables
with sensible defaults so the pipeline can run locally without any setup.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Base paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]       # …/Sarimax-Thesis

BACKEND_ROOT = REPO_ROOT / "backend"

try:
    from dotenv import load_dotenv
    # Load from root first, then backend as fallback
    load_dotenv(REPO_ROOT / ".env", override=True)
    load_dotenv(BACKEND_ROOT / ".env", override=True)
except ImportError:
    pass

# Where the trained model artefacts live (one sub-folder per appliance).
# V3 model root (hyphenated path is kept for runtime consistency).
MODELS_ROOT = BACKEND_ROOT / "Sarimax-ModelV3"

# Historical hourly CSVs produced by the daily ingestion job
HISTORY_DIR = BACKEND_ROOT / "forecasting" / "history"

# Where pipeline outputs (forecasts, logs, run manifests) are stored
OUTPUTS_DIR = BACKEND_ROOT / "forecasting" / "outputs"

LOGS_DIR = BACKEND_ROOT / "forecasting" / "logs"

# ---------------------------------------------------------------------------
# Appliance registry
# ---------------------------------------------------------------------------
APPLIANCES = ["aircon", "electric_fan", "refrigerator"]

# Maps the appliance key to the full relative path from MODELS_ROOT
# to the folder containing best_model.pkl
APPLIANCE_MODEL_DIR: dict[str, str] = {
    "aircon":       "Final_Aircon/model/sarimax/aircon_model_ready",
    "electric_fan": "Final_electricfan/sarimax/electric_fan_model_ready",
    "refrigerator": "Final_Ref/model/sarimax/refrigerator_model_ready",
}

# ---------------------------------------------------------------------------
# Forecast settings
# ---------------------------------------------------------------------------
FORECAST_HORIZON: int = 24          # hours
FORECAST_START_HOUR: int = 0        # next-day starts at 00:00
FORECAST_END_HOUR: int = 23         # next-day ends at 23:00

# ---------------------------------------------------------------------------
# Electricity tariff (PHP per kWh)
# ---------------------------------------------------------------------------
TARIFF_PHP_PER_KWH: float = float(os.getenv("TARIFF_PHP_PER_KWH", "11.5"))

# ---------------------------------------------------------------------------
# Daily budget per user (PHP) – can be overridden per household at runtime
# ---------------------------------------------------------------------------
DEFAULT_DAILY_BUDGET_PHP: float = float(os.getenv("DEFAULT_DAILY_BUDGET_PHP", "200.0"))

# ---------------------------------------------------------------------------
# Scheduler (MILP) settings
# ---------------------------------------------------------------------------
SCHEDULER_ENABLED: bool = os.getenv("SCHEDULER_ENABLED", "true").lower() == "true"
SCHEDULER_TIME_STEP_HOURS: int = int(os.getenv("SCHEDULER_TIME_STEP_HOURS", "1"))
SCHEDULER_PEAK_PENALTY_PHP_PER_KWH: float = float(os.getenv("SCHEDULER_PEAK_PENALTY_PHP_PER_KWH", "1.0"))
SCHEDULER_MAX_SHIFT_HOURS: int = int(os.getenv("SCHEDULER_MAX_SHIFT_HOURS", "3"))

# Binary ON/OFF mode (as described in MILP.md)
# True  → binary b_vars with hard budget constraint (recommended)
# False → legacy continuous load-shifting mode
SCHEDULER_BINARY_MODE: bool = os.getenv("SCHEDULER_BINARY_MODE", "true").lower() == "true"

# TOU tariff profile (household usage is concentrated at night)
# night  18:00-05:59  → off-peak discount (when aircon/fan actually run)
# mid    06:00-12:59  → normal rate
# peak   13:00-17:59  → peak surcharge (appliances NOT scheduled here)
SCHEDULER_TARIFF_MULTIPLIERS: dict[str, float] = {
    "night": float(os.getenv("SCHEDULER_NIGHT_MULTIPLIER", "0.85")),   # 18:00-05:59
    "mid":   float(os.getenv("SCHEDULER_MID_MULTIPLIER",   "1.00")),   # 06:00-12:59
    "peak":  float(os.getenv("SCHEDULER_PEAK_MULTIPLIER",  "1.25")),   # 13:00-17:59
}

SCHEDULER_COMFORT_PENALTY: dict[str, float] = {
    "aircon":       float(os.getenv("SCHEDULER_COMFORT_AIRCON", "0.80")),
    "electric_fan": float(os.getenv("SCHEDULER_COMFORT_FAN", "0.40")),
    "refrigerator": float(os.getenv("SCHEDULER_COMFORT_REFRIGERATOR", "0.0")),
}

# Appliance scheduling policy:
# - refrigerator: non-schedulable, runs 24/7 continuously
# - aircon / electric_fan: NIGHT-ONLY use (household pattern)
#   Allowed window: 18:00-23:59 (same day) and 00:00-05:59 (next day)
_NIGHT_HOURS: list[int] = list(range(18, 24)) + list(range(0, 6))  # 6 PM – 5 AM

SCHEDULER_APPLIANCE_RULES: dict[str, dict[str, Any]] = {
    "aircon": {
        "schedulable": True,
        "allowed_hours": _NIGHT_HOURS,   # night-only: 6 PM – 5 AM
        "max_shift_hours": SCHEDULER_MAX_SHIFT_HOURS,
    },
    "electric_fan": {
        "schedulable": True,
        "allowed_hours": _NIGHT_HOURS,   # night-only: 6 PM – 5 AM
        "max_shift_hours": SCHEDULER_MAX_SHIFT_HOURS,
    },
    "refrigerator": {
        "schedulable": False,
        "allowed_hours": list(range(24)),  # continuous 24/7
        "max_shift_hours": 0,
    },
}

# ---------------------------------------------------------------------------
# Weather API (Open-Meteo – free, no key required)
# ---------------------------------------------------------------------------
WEATHER_API_URL: str = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude={lat}&longitude={lon}"
    "&hourly=temperature_2m,relativehumidity_2m,precipitation"
    "&timezone=Asia%2FManila"
    "&forecast_days=2"
)

# Huang's Home location (Manila area) – override via env
LOCATION_LAT: float = float(os.getenv("LOCATION_LAT", "14.5995"))
LOCATION_LON: float = float(os.getenv("LOCATION_LON", "120.9842"))

# ---------------------------------------------------------------------------
# MongoDB (optional – used when saving outputs to the database)
# ---------------------------------------------------------------------------
MONGO_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGO_DB: str = os.getenv("MONGO_DB", "Sarimax-Thesis")
HISTORY_COLLECTION: str = "energybuckets"
FORECAST_COLLECTION: str = "daily_forecasts"

# Maps pipeline appliance keys ('electric_fan') to MongoDB enum values ('electricfan')
APPLIANCE_MAP_MONGO: dict[str, str] = {
    "aircon":       "aircon",
    "electric_fan": "electricfan",
    "refrigerator": "refrigerator",
}

# ---------------------------------------------------------------------------
# Runtime flags
# ---------------------------------------------------------------------------
DRY_RUN: bool = os.getenv("DRY_RUN", "false").lower() == "true"
SAVE_CSV: bool = os.getenv("SAVE_CSV", "true").lower() == "true"
SAVE_MONGO: bool = os.getenv("SAVE_MONGO", "true").lower() == "true"


@dataclass
class PipelineConfig:
    """Runtime configuration bag passed through the pipeline."""
    models_root: Path = field(default_factory=lambda: MODELS_ROOT)
    history_dir: Path = field(default_factory=lambda: HISTORY_DIR)
    outputs_dir: Path = field(default_factory=lambda: OUTPUTS_DIR)
    appliances: list[str] = field(default_factory=lambda: list(APPLIANCES))
    horizon: int = FORECAST_HORIZON
    tariff: float = TARIFF_PHP_PER_KWH
    daily_budget: float = DEFAULT_DAILY_BUDGET_PHP
    lat: float = LOCATION_LAT
    lon: float = LOCATION_LON
    dry_run: bool = DRY_RUN
    save_csv: bool = SAVE_CSV
    save_mongo: bool = SAVE_MONGO
    scheduler_enabled: bool = SCHEDULER_ENABLED
    scheduler_binary_mode: bool = SCHEDULER_BINARY_MODE
    scheduler_time_step_hours: int = SCHEDULER_TIME_STEP_HOURS
    scheduler_peak_penalty: float = SCHEDULER_PEAK_PENALTY_PHP_PER_KWH
    scheduler_max_shift_hours: int = SCHEDULER_MAX_SHIFT_HOURS
    scheduler_tariff_multipliers: dict[str, float] = field(default_factory=lambda: dict(SCHEDULER_TARIFF_MULTIPLIERS))
    scheduler_comfort_penalty: dict[str, float] = field(default_factory=lambda: dict(SCHEDULER_COMFORT_PENALTY))
    scheduler_appliance_rules: dict[str, dict[str, Any]] = field(
        default_factory=lambda: {k: dict(v) for k, v in SCHEDULER_APPLIANCE_RULES.items()}
    )
