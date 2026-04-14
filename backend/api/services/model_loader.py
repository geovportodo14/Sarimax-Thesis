import os
import json
import logging
import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Model paths — appliance → directory containing best_params.json + coefficients.csv
#
# Routing strategy:
#   aircon       → V3 (stage-based, proven architecture)
#   electricfan  → V4 (current production model)
#   refrigerator → V4 (current production model)
# ---------------------------------------------------------------------------
_BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

_SARIMAX_MODEL_V3_ROOT = os.path.join(_BACKEND_ROOT, "Sarimax-ModelV3")
_SARIMAX_MODEL_V4_ROOT = os.path.join(
    _BACKEND_ROOT, "forecasting", "outputs", "Sarimax-ModelV4"
)

# Maps the API appliance key → directory containing best_params.json + coefficients.csv
_APPLIANCE_PATHS = {
    "aircon": os.path.join(
        _SARIMAX_MODEL_V3_ROOT,
        "Final_Aircon", "model", "sarimax",
        "aircon_model_ready"
    ),
    "electricfan": os.path.join(
        _SARIMAX_MODEL_V4_ROOT,
        "V4-efan", "model", "sarimax",
        "electric_fan_model_ready"
    ),
    "refrigerator": os.path.join(
        _SARIMAX_MODEL_V4_ROOT,
        "V4-ref", "sarimax",
        "refrigerator_model_ready"
    ),
}

# ---------------------------------------------------------------------------
# Model-evaluation constants (from rolling-origin evaluation, horizon=24)
# Used by the Smart Budget Recommendation feature.
#
# Per-appliance:  MAE_day  = hourly MAE × 24  (kWh, daily horizon)
#                 mean_day = mean total daily actual consumption (kWh)
#                 mae_pct  = MAE_day / mean_day
#
#  Aircon:      MAE=0.0221 kWh/h → daily 0.531 kWh, mean 2.631 → 15.1 %
#  Electricfan: MAE=0.0074 kWh/h → daily 0.177 kWh, mean 0.883 →  8.2 %
#  Refrigerator:MAE=0.2731 kWh/h → daily 6.554 kWh, mean 2.867 → R²=−11.9
#               (excluded from budget-range calculation — too uncertain)
#
# Weighted MAE% used in budget range:
#   Weighted by mean daily consumption, aircon + electricfan only.
#   mean_total (ac+ef) = 2.631 + 0.883 = 3.514 kWh
#   weighted_mae = (0.531×2.631 + 0.177×0.883) / (3.514×3.514)
#               → see SmartBudgetCard for JS implementation
# ---------------------------------------------------------------------------
# Metrics sourced from rolling-origin evaluation (horizon=24).
# Updated 2026-04-09 to reflect actual production model versions.
#
# Aircon V3:       MAE=0.0755, MAPE=43.2%, R²=0.689
# Electric fan V4: MAE=0.0110, MAPE=42.3%, R²=0.246
# Refrigerator V4: MAE=0.0290, MAPE=30.3%, R²=0.001
APPLIANCE_EVAL_METRICS = {
    "aircon": {
        "mae_hourly": 0.0755,
        "mae_daily": 0.0755 * 24,      # 1.812
        "mean_daily_kwh": 2.6314,
        "mae_pct": 0.432,               # 43.2 %
        "r2": 0.6888,
        "model_version": "V3",
    },
    "electricfan": {
        "mae_hourly": 0.01097,
        "mae_daily": 0.01097 * 24,     # 0.263
        "mean_daily_kwh": 0.8826,
        "mae_pct": 0.423,               # 42.3 %
        "r2": 0.2458,
        "model_version": "V4",
    },
    "refrigerator": {
        "mae_hourly": 0.02900,
        "mae_daily": 0.02900 * 24,     # 0.696
        "mean_daily_kwh": 2.8667,
        "mae_pct": 0.303,               # 30.3 %
        "r2": 0.0013,
        "model_version": "V4",
    },
}


class ModelLoader:
    _instances = {}

    @classmethod
    def get_model(cls, appliance: str):
        """
        Lazily initialise the SARIMAX model using saved coefficients and
        hyperparameters from the latest Sarimax-Model training run.

        Bypasses fragile pickle loading entirely; reconstructs the
        statsmodels state-space architecture from best_params.json +
        coefficients.csv, which is ~10 GB lighter than loading the pkl.
        """
        appliance = appliance.lower().replace(" ", "_")
        if appliance not in cls._instances:
            logger.info(f"Dynamically loading SARIMAX parameters for {appliance}...")

            appliance_path = _APPLIANCE_PATHS.get(appliance)
            if appliance_path is None:
                raise ValueError(f"Unknown appliance key: '{appliance}'. "
                                 f"Valid keys: {list(_APPLIANCE_PATHS)}")

            coef_path   = os.path.join(appliance_path, "coefficients.csv")
            params_path = os.path.join(appliance_path, "best_params.json")

            if not os.path.exists(coef_path) or not os.path.exists(params_path):
                raise FileNotFoundError(
                    f"Model config files not found for '{appliance}' at:\n"
                    f"  best_params.json → {params_path}\n"
                    f"  coefficients.csv → {coef_path}"
                )

            try:
                with open(params_path, "r") as f:
                    config = json.load(f)

                best_params    = config["best"]
                order          = tuple(best_params["order"].values())
                seasonal_order = tuple(best_params["seasonal_order"].values())
                exog_columns   = config.get("exog_columns", [])

                if not exog_columns:
                    exog_columns = [
                        "power", "temperature", "humidity", "rainfall",
                        "hour_of_day", "day_of_week", "is_weekend",
                        "lag_24", "lag_168", "rolling_mean_24", "rolling_mean_168"
                    ]

                # Load coefficients
                coef_df = pd.read_csv(coef_path)
                params  = coef_df.set_index("term")["coef"]

                # Dummy data to initialise state-space dimensions
                dummy_endog = np.zeros(500)
                dummy_exog  = pd.DataFrame(
                    np.zeros((500, len(exog_columns))),
                    columns=exog_columns
                )

                model_arch = SARIMAX(
                    dummy_endog,
                    exog=dummy_exog,
                    order=order,
                    seasonal_order=seasonal_order,
                    enforce_stationarity=False,
                    enforce_invertibility=False,
                    trend="n"
                )

                # Some models have a 'const' term saved in the CSV
                if "const" in params.index and "const" not in model_arch.param_names:
                    model_arch = SARIMAX(
                        dummy_endog,
                        exog=dummy_exog,
                        order=order,
                        seasonal_order=seasonal_order,
                        enforce_stationarity=False,
                        enforce_invertibility=False,
                        trend="c"
                    )

                aligned_params = [params[name] for name in model_arch.param_names]
                res = model_arch.smooth(aligned_params)
                cls._instances[appliance] = res
                logger.info(f"Successfully loaded {appliance} SARIMAX model.")

            except Exception as e:
                logger.error(f"Failed to load {appliance} model: {e}")
                raise

        return cls._instances[appliance]
