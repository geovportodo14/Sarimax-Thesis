import json
import math
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import pytz
import logging
from .model_loader import ModelLoader, _APPLIANCE_PATHS

logger = logging.getLogger(__name__)

# Default exogenous columns (V3 models)
EXPECTED_EXOG = [
    "power",
    "temperature",
    "humidity",
    "rainfall",
    "hour_of_day",
    "day_of_week",
    "is_weekend",
    "lag_24",
    "lag_168",
    "rolling_mean_24",
    "rolling_mean_168"
]


def _load_model_exog_columns(appliance: str) -> list:
    """
    Load the actual exog column list from the model's best_params.json.
    Falls back to EXPECTED_EXOG if the file is unavailable.
    """
    appliance_key = appliance.lower().replace(" ", "_")
    if appliance_key == "electric_fan":
        appliance_key = "electricfan"

    appliance_path = _APPLIANCE_PATHS.get(appliance_key)
    if not appliance_path:
        return list(EXPECTED_EXOG)

    params_path = os.path.join(appliance_path, "best_params.json")
    if not os.path.exists(params_path):
        return list(EXPECTED_EXOG)

    try:
        with open(params_path, "r") as f:
            config = json.load(f)
        cols = config.get("exog_columns", [])
        return cols if cols else list(EXPECTED_EXOG)
    except Exception:
        return list(EXPECTED_EXOG)

class PredictService:
    # Cache for per-appliance exog column lists
    _exog_cache: dict = {}

    @classmethod
    def _get_exog_cols(cls, appliance: str) -> list:
        """Get the exogenous columns this appliance's model expects."""
        if appliance not in cls._exog_cache:
            cls._exog_cache[appliance] = _load_model_exog_columns(appliance)
        return cls._exog_cache[appliance]

    @staticmethod
    def construct_exog_batch(history_len: int, horizon: int, start_time: datetime,
                           watts: list = None, temps: list = None, hums: list = None,
                           history_values: list = None,
                           exog_columns: list = None):
        """
        Constructs exogenous features for a combined period (history + future).
        Dynamically generates all possible features and then filters to the
        columns the specific model was trained with.
        """
        if exog_columns is None:
            exog_columns = list(EXPECTED_EXOG)

        total_steps = history_len + horizon
        history_start = start_time - timedelta(hours=history_len)

        baseline_kwh = 0.25
        avg_kwh = np.mean(history_values) if (history_values and len(history_values) > 0) else baseline_kwh

        last_power = watts[-1] if (watts and len(watts) > 0) else (avg_kwh * 1000.0)
        curr_temp = temps[-1] if (temps and len(temps) > 0) else 30.0
        curr_hum = hums[-1] if (hums and len(hums) > 0) else 70.0

        lookup_values = list(history_values) if history_values else [baseline_kwh] * history_len
        if len(lookup_values) < 168:
             lookup_values = [baseline_kwh] * (168 - len(lookup_values)) + lookup_values

        lookup_series = pd.Series(lookup_values)

        exog_rows = []
        for step in range(total_steps):
            step_time = history_start + timedelta(hours=step)

            hour_of_day = step_time.hour
            day_of_week = step_time.weekday()
            is_weekend = 1 if day_of_week >= 5 else 0

            temperature = curr_temp
            humidity = curr_hum
            rainfall = 0.0

            padding_len = len(lookup_series) - total_steps
            idx = padding_len + step

            lag_24 = lookup_series.iloc[idx - 24] if idx >= 24 else avg_kwh
            lag_168 = lookup_series.iloc[idx - 168] if idx >= 168 else avg_kwh
            rolling_24 = lookup_series.iloc[max(0, idx-24):idx].mean() if idx > 0 else avg_kwh
            rolling_168 = lookup_series.iloc[max(0, idx-168):idx].mean() if idx > 0 else avg_kwh

            # Build the full feature dict — includes all possible features
            row = {
                "power": last_power,
                "temperature": temperature,
                "humidity": humidity,
                "rainfall": rainfall,
                "hour_of_day": hour_of_day,
                "day_of_week": day_of_week,
                "is_weekend": is_weekend,
                "lag_24": lag_24,
                "lag_168": lag_168,
                "rolling_mean_24": rolling_24,
                "rolling_mean_168": rolling_168,
                # Cyclical time encodings (V3/V6 models use these)
                "sin_hour": math.sin(2 * math.pi * hour_of_day / 24),
                "cos_hour": math.cos(2 * math.pi * hour_of_day / 24),
                "sin_day_of_week": math.sin(2 * math.pi * day_of_week / 7),
                "cos_day_of_week": math.cos(2 * math.pi * day_of_week / 7),
                "month": float(step_time.month),
                # Refrigerator-specific features
                "lag_1": lookup_series.iloc[idx - 1] if idx >= 1 else avg_kwh,
                "lag_2": lookup_series.iloc[idx - 2] if idx >= 2 else avg_kwh,
                "lag_3": lookup_series.iloc[idx - 3] if idx >= 3 else avg_kwh,
                "rolling_std_24": float(
                    lookup_series.iloc[max(0, idx-24):idx].std()
                ) if idx > 1 else 0.0,
                "temp_humidity_interaction": temperature * humidity,
                # Electric fan-specific features
                "temperature_sq": temperature ** 2,
                "heat_index": temperature + 0.33 * humidity - 4.0,
                "is_sleeping": 1.0 if hour_of_day >= 22 or hour_of_day < 7 else 0.0,
            }
            exog_rows.append(row)

            if step >= history_len - 1:
                lookup_series = pd.concat([lookup_series, pd.Series([avg_kwh])], ignore_index=True)

        # Build full DataFrame, then select only the columns this model needs
        df = pd.DataFrame(exog_rows)
        df = df[exog_columns].astype(float)
        return df

    @classmethod
    def get_forecast(cls, appliance: str, history: list, horizon: int,
                    watts: list = None, temps: list = None, hums: list = None):
        # 1. Load the model architecture
        model_results = ModelLoader.get_model(appliance)

        # Get the exact exog columns this model expects
        exog_columns = cls._get_exog_cols(appliance)

        mnl_tz = pytz.timezone('Asia/Manila')
        now = datetime.now(mnl_tz)

        # 2. Prepare Exogenous Features for BOTH history and future
        history_len = len(history)
        full_exog = cls.construct_exog_batch(
            history_len, horizon, now, watts, temps, hums, history,
            exog_columns=exog_columns,
        )

        history_exog = full_exog.iloc[:history_len]
        future_exog = full_exog.iloc[history_len:]

        # 3. Apply history to the model to align Kalman filter state
        aligned_model = model_results.apply(history, exog=history_exog)

        # 4. Predict
        logger.info(f"Forecasting {horizon} steps for {appliance} with state alignment...")
        forecast_series = aligned_model.forecast(steps=horizon, exog=future_exog)

        return [max(0.0, float(val)) for val in forecast_series]

