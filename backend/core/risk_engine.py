from pathlib import Path
import joblib
import numpy as np
import xgboost as xgb
from typing import Dict, Any
from .alerts import get_flood_event_signal   # <-- FIXED

# Load ML Model
ML_PATH = Path(__file__).resolve().parent.parent / "ml" / "flood_xgb.joblib"
_model = None
_feature_names = None

if ML_PATH.exists():
    artefact = joblib.load(ML_PATH)
    _model = artefact["model"]
    _feature_names = artefact["features"]
    print("🚀 Flood XGBoost Model Loaded Successfully.")
else:
    print("⚠ ML Model NOT FOUND — Using fallback rule")

def compute_flood_risk_ml(features: Dict[str, float]) -> Dict[str, Any]:
    if _model is None:
        return {"score": 0.2, "level": "Low", "method": "fallback-rule"}

    X = np.array([features[f] for f in _feature_names]).reshape(1, -1)
    dmatrix = xgb.DMatrix(X, feature_names=_feature_names)
    prob = float(_model.predict(dmatrix)[0])

    if prob >= 0.75:
        level = "High"
    elif prob >= 0.40:
        level = "Medium"
    else:
        level = "Low"

    return {"score": round(prob, 3), "level": level, "method": "ML-XGBoost"}

def compute_risks(weather_data: Dict[str, Any]) -> Dict[str, Any]:
    current = weather_data.get("current_weather", {})
    hourly = weather_data.get("hourly", {})

    temp = current.get("temperature")
    wind = current.get("windspeed", 0.0)
    precip_list = hourly.get("precipitation", [])

    recent_rain_1d = max(precip_list[-1:], default=0.0)
    recent_rain_3d = sum(precip_list[-3:]) if len(precip_list) >= 3 else recent_rain_1d
    recent_rain_7d = sum(precip_list[-7:]) if len(precip_list) >= 7 else recent_rain_3d

    humidity_series = hourly.get("relativehumidity_2m", [60])
    humidity = humidity_series[-1] if humidity_series else 60

    features = {
        "rain_last_1d": recent_rain_1d,
        "rain_last_3d": recent_rain_3d,
        "rain_last_7d": recent_rain_7d,
        "humidity": humidity,
        "wind_speed": wind,
        "elevation": 150
    }

    flood_ai = compute_flood_risk_ml(features)

    # 7 DAY + LIVE ALERTS
    alert = get_flood_event_signal(
        weather_data.get("location_name", ""),
        weather_data.get("country_name", "")
    )

    # Fusion Logic
    if alert["city_alert"]:
        flood_ai["level"] = "High"
        flood_ai["score"] = max(flood_ai["score"], 0.95)
        flood_ai["method"] = "🚨 LIVE CITY ALERT + ML"
    elif alert["country_alert"]:
        flood_ai["level"] = "High"
        flood_ai["score"] = max(flood_ai["score"], 0.85)
        flood_ai["method"] = "⚠ NATIONAL FLOOD EMERGENCY + ML"

    # Heat Risk
    if temp is None:
        heat_score, heat_level = 0.5, "Unknown"
    else:
        if temp >= 40:
            heat_score, heat_level = 0.95, "High"
        elif temp >= 32:
            heat_score, heat_level = 0.7, "Medium"
        else:
            heat_score, heat_level = 0.2, "Low"

    # Storm Risk
    if wind >= 80:
        storm_score, storm_level = 0.95, "High"
    elif wind >= 45:
        storm_score, storm_level = 0.7, "Medium"
    else:
        storm_score, storm_level = 0.2, "Low"

    return {
        "risks": {
            "flood": flood_ai,
            "heat": {"score": round(heat_score, 2), "level": heat_level},
            "storm": {"score": round(storm_score, 2), "level": storm_level},
        },
        "alert": alert,
        "features": features,
        "ai_insight": (
            f"Flood Risk: {flood_ai['level']} — Hybrid Score: {flood_ai['score']} "
            f"— Engine: {flood_ai['method']} — Events Window: last 7 days "
            f"— Sources: {', '.join(alert['sources_used'])}"
        )
    }
