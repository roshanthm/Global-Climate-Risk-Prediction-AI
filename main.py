from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict
import requests
from core.risk_engine import compute_risks
from core.geo import geocode_place, fetch_weather

app = FastAPI(title="Global Disaster Intelligence System - Backend")

# CORS Middleware (allows frontend to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ Pydantic Models ------------------
class RiskRequest(BaseModel):
    location: str

class RiskResponse(BaseModel):
    risks: Dict
    alert: Dict
    features: Dict
    ai_insight: str
    location: Dict
    weather: Dict


# ----------------------- API Routes -----------------------

@app.post("/risk", response_model=RiskResponse)
def risk(req: RiskRequest):
    # Geocode → get lat/lon
    geo = geocode_place(req.location)
    if geo is None:
        return {"error": "Location not found"}

    # Fetch live weather
    weather = fetch_weather(geo["lat"], geo["lon"])
    if weather is None:
        return {"error": "Weather service unavailable"}

    # Pass location into risk engine for alert lookup
    weather["location_name"] = geo["name"]

    result = compute_risks(weather)

    return {
        "risks": result["risks"],
        "alert": result["alert"],
        "features": result["features"],
        "ai_insight": result["ai_insight"],
        "location": geo,
        "weather": {
            "temp_c": weather["current_weather"].get("temperature"),
            "wind_kmh": weather["current_weather"].get("windspeed"),
            "recent_rain_mm": result["features"]["rain_last_1d"],
            "last_update": weather["current_weather"].get("time"),
        }
    }


@app.get("/")
def home():
    return {"status": "Backend running - GDIS Active"}
