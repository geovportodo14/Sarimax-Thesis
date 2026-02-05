from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
try:
    from utils.email_utils import send_welcome_email, send_threshold_alert
except ImportError:
    from api.utils.email_utils import send_welcome_email, send_threshold_alert

# Load environment variables from .env in the root directory
load_dotenv()

app = FastAPI()

class WelcomeRequest(BaseModel):
    email: str

class ThresholdRequest(BaseModel):
    email: str
    usage_percent: int
    budget: float
    cost: float

@app.get("/")
def root():
    return {"status": "ok", "message": "Sarimax backend is running"}

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
