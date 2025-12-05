import requests
from typing import Optional, Dict

def geocode_place(place: str) -> Optional[Dict]:
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": place, "count": 1, "format": "json"}
    resp = requests.get(url, params=params, timeout=10)

    if resp.status_code != 200:
        return None
    
    data = resp.json()
    results = data.get("results", [])
    if not results:
        return None

    r = results[0]
    return {
        "name": r.get("name"),
        "country": r.get("country"),
        "lat": r.get("latitude"),
        "lon": r.get("longitude"),
    }
