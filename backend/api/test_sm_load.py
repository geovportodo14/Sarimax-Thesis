from statsmodels.tsa.statespace.sarimax import SARIMAXResults
import os

path = os.path.join("backend", "modeling", "aircon", "best_model.pkl")
try:
    print(f"Loading {path}...")
    model = SARIMAXResults.load(path)
    print("Success loading with statsmodels!")
except Exception as e:
    print(f"Statsmodels .load() failed: {type(e).__name__} - {e}")
