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

try:
    from .services.predict_service import PredictService
except ImportError:
    try:
        from services.predict_service import PredictService
    except ImportError:
        from backend.api.services.predict_service import PredictService

# --- NEW MODEL FOR SARIMAX ---
class PredictionRequest(BaseModel):
    appliance: str
    history: List[float] # This is kWh history
    watts: Optional[List[float]] = None # Average Watts history
    temps: Optional[List[float]] = None # Temperature history
    hums: Optional[List[float]] = None # Humidity history
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
async def predict(request: PredictionRequest):
    try:
        # Call the actual SARIMAX integration service
        forecast = PredictService.get_forecast(
            appliance=request.appliance,
            history=request.history,
            horizon=request.horizon,
            watts=request.watts,
            temps=request.temps,
            hums=request.hums
        )

        return {
            "status": "success",
            "forecast": forecast,
            "horizon": request.horizon
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Prediction Error: {e}")
        return {"status": "error", "message": str(e), "forecast": []}