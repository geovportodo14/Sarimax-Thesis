import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import pytz
import logging
from .model_loader import ModelLoader

logger = logging.getLogger(__name__)

# The exact exogenous columns required by all three models based on best_params.json
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

class PredictService:
    @staticmethod
    def construct_exog_batch(history_len: int, horizon: int, start_time: datetime,
                           watts: list = None, temps: list = None, hums: list = None,
                           history_values: list = None):
        """
        Constructs exogenous features for a combined period (history + future).
        """
        total_steps = history_len + horizon
        # The start_time provided is for the forecast (index history_len).
        # We need to calculate the actual start time of the history segment.
        history_start = start_time - timedelta(hours=history_len)
        
        baseline_kwh = 0.25
        avg_kwh = np.mean(history_values) if (history_values and len(history_values) > 0) else baseline_kwh
        
        # Latest known values for forward-filling weather/power
        last_power = watts[-1] if (watts and len(watts) > 0) else (avg_kwh * 1000.0)
        curr_temp = temps[-1] if (temps and len(temps) > 0) else 30.0
        curr_hum = hums[-1] if (hums and len(hums) > 0) else 70.0

        # We need a series that contains enough history for lag/rolling lookups
        # Prepend history if values provided, else dummy baseline
        lookup_values = list(history_values) if history_values else [baseline_kwh] * history_len
        if len(lookup_values) < 168:
             lookup_values = [baseline_kwh] * (168 - len(lookup_values)) + lookup_values
        
        lookup_series = pd.Series(lookup_values)
        
        exog_rows = []
        # We iterate and append predicted average kwh to lookup_series for future steps
        for step in range(total_steps):
            # Calculate time for this specific step (past or future)
            step_time = history_start + timedelta(hours=step)
            
            # 1. Time-based features
            hour_of_day = step_time.hour
            day_of_week = step_time.weekday()
            is_weekend = 1 if day_of_week >= 5 else 0
            
            # 2. Weather features (Static for now, could be improved with forecast API)
            temperature = curr_temp
            humidity = curr_hum
            rainfall = 0.0
            
            # 3. Lag and Rolling features
            # Look up from the current index in lookup_series
            # Index in lookup_series for step i is (padding_len + i)
            padding_len = len(lookup_series) - total_steps
            idx = padding_len + step
            
            lag_24 = lookup_series.iloc[idx - 24] if idx >= 24 else avg_kwh
            lag_168 = lookup_series.iloc[idx - 168] if idx >= 168 else avg_kwh
            rolling_24 = lookup_series.iloc[max(0, idx-24):idx].mean() if idx > 0 else avg_kwh
            rolling_168 = lookup_series.iloc[max(0, idx-168):idx].mean() if idx > 0 else avg_kwh
            
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
                "rolling_mean_168": rolling_168
            }
            exog_rows.append(row)
            
            # For future steps (step >= history_len), we simulate kwh for the lookup series
            if step >= history_len - 1:
                lookup_series = pd.concat([lookup_series, pd.Series([avg_kwh])], ignore_index=True)

        df = pd.DataFrame(exog_rows, columns=EXPECTED_EXOG)
        return df.astype(float)

    @classmethod
    def get_forecast(cls, appliance: str, history: list, horizon: int, 
                    watts: list = None, temps: list = None, hums: list = None):
        # 1. Load the model architecture
        model_results = ModelLoader.get_model(appliance)
        
        mnl_tz = pytz.timezone('Asia/Manila')
        now = datetime.now(mnl_tz)
        
        # 2. Prepare Exogenous Features for BOTH history and future
        # history length is len(history)
        history_len = len(history)
        full_exog = cls.construct_exog_batch(history_len, horizon, now, watts, temps, hums, history)
        
        history_exog = full_exog.iloc[:history_len]
        future_exog = full_exog.iloc[history_len:]
        
        # 3. Apply history to the model to align state
        # This is the "secret sauce" - it updates the internal state (Kalman filter)
        # to match the provided history before we forecast.
        aligned_model = model_results.apply(history, exog=history_exog)
        
        # 4. Predict
        logger.info(f"Forecasting {horizon} steps for {appliance} with state alignment...")
        forecast_series = aligned_model.forecast(steps=horizon, exog=future_exog)
        
        return [max(0.0, float(val)) for val in forecast_series]

