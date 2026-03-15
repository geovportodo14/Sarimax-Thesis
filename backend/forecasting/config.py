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

# Where the trained model artefacts live (one sub-folder per appliance)
# Where the trained model artefacts live
# (This points to the root of the ModelV2 folder provided by the user)
MODELS_ROOT = BACKEND_ROOT / "Sarimax-ModelV2"

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
    "aircon":       "Model_aircon/model/sarimax/aircon_final_hourly_with_weather",
    "electric_fan": "Model_efan/model/sarimax/electric_fan_final_hourly_with_weather",
    "refrigerator": "Refrigerator_Model/model/sarimax/refrigerator_final_hourly_with_weather",
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
