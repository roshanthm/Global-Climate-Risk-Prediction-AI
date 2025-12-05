import requests
from typing import Optional, Dict

def fetch_weather(lat: float, lon: float) -> Optional[Dict]:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "hourly": "precipitation,temperature_2m,windgusts_10m",
        "forecast_days": 1,
        "timezone": "auto",
    }
    resp = requests.get(url, params=params, timeout=10)

    if resp.status_code != 200:
        return None

    return resp.json()
