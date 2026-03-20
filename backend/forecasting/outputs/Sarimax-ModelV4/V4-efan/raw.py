import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAXResults

# load dataset
df = pd.read_csv("data/refrigerator_model_ready.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values("timestamp").set_index("timestamp")

# load trained model
model = SARIMAXResults.load("model/sarimax/refrigerator_model_ready/best_model.pkl")

# timestamp you want to inspect
target_ts = pd.Timestamp("2026-02-24 22:00:00")

# get feature columns
exog_cols = [c for c in df.columns if c != "energy"]

# rebuild exogenous input
X = df.loc[[target_ts]][exog_cols]

# forecast exactly 1 step
fc = model.get_forecast(steps=1, exog=X)

# raw prediction
raw_pred = fc.predicted_mean.iloc[0]

print("RAW prediction:", raw_pred)