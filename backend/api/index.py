from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from dotenv import load_dotenv
import numpy as np

try:
    from .utils.email_utils import send_welcome_email, send_threshold_alert
except ImportError:
    try:
        from utils.email_utils import send_welcome_email, send_threshold_alert
    except ImportError:
        from backend.api.utils.email_utils import send_welcome_email, send_threshold_alert

# Load environment variables
load_dotenv()

app = FastAPI()

# --- EXISTING MODELS ---
class WelcomeRequest(BaseModel):
    email: str

class ThresholdRequest(BaseModel):
    email: str
    usage_percent: int
    budget: float
    cost: float

# --- NEW MODEL FOR SARIMAX ---
class PredictionRequest(BaseModel):
    history: List[float]
    horizon: int

@app.get("/")
def root():
    return {"status": "ok", "message": "Sarimax backend is running"}

# --- EMAIL ROUTES (UNTOUCHED) ---
@app.post("/api/alerts/welcome")
def welcome_alert(req: WelcomeRequest):
    result = send_welcome_email(req.email)
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result

@app.post("/api/alerts/threshold")
def threshold_alert(req: ThresholdRequest):
    result = send_threshold_alert(req.email, req.usage_percent, req.budget, req.cost)
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result

# --- NEW PREDICTION ROUTE (THE BRIDGE) ---
@app.post("/predict")
async def predict(req: PredictionRequest):
    try:
        history = req.history
        horizon = req.horizon

        # 1. Anchor the forecast to the last known actual power reading
        # If no data exists yet today, we use a baseline (e.g., 250W)
        last_val = history[-1] if history else 250.0

        # 2. SARIMAX MODEL INTEGRATION
        # Replace this simulation with: your_model.forecast(steps=horizon)
        # For now, we generate a realistic fluctuating trend for the demo
        forecast = []
        current = last_val
        for _ in range(horizon):
            # Simulate natural appliance variance (+/- 15 Watts)
            change = np.random.uniform(-15, 15)
            current = max(0, current + change)
            forecast.append(round(current, 2))

        return {
            "status": "success",
            "forecast": forecast,
            "horizon": horizon
        }
    except Exception as e:
        print(f"Prediction Error: {e}")
        return {"status": "error", "message": str(e), "forecast": []}