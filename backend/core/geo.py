### FILE: core/geo.py
import requests

# 🔥 **Override Exact Known Locations**
OVERRIDE_LOCATIONS = {
    # INDIA MAJOR FLOOD STATES + CITIES
    "kerala": {"name": "Kerala", "country": "India", "lat": 10.8505, "lon": 76.2711},
    "kottayam": {"name": "Kottayam", "country": "India", "lat": 9.5916, "lon": 76.5222},
    "kochi": {"name": "Kochi", "country": "India", "lat": 9.9312, "lon": 76.2673},
    "ernakulam": {"name": "Ernakulam", "country": "India", "lat": 9.9816, "lon": 76.2999},
    "alappuzha": {"name": "Alappuzha", "country": "India", "lat": 9.4981, "lon": 76.3388},
    "trivandrum": {"name": "Thiruvananthapuram", "country": "India", "lat": 8.5241, "lon": 76.9366},
    "kozhikode": {"name": "Kozhikode", "country": "India", "lat": 11.2588, "lon": 75.7804},

    # OTHER INDIA
    "delhi": {"name": "Delhi", "country": "India", "lat": 28.7041, "lon": 77.1025},
    "new delhi": {"name": "New Delhi", "country": "India", "lat": 28.6139, "lon": 77.2090},
    "mumbai": {"name": "Mumbai", "country": "India", "lat": 19.0760, "lon": 72.8777},
    "chennai": {"name": "Chennai", "country": "India", "lat": 13.0827, "lon": 80.2707},
    "kolkata": {"name": "Kolkata", "country": "India", "lat": 22.5726, "lon": 88.3639},

    # INDONESIA
    "aceh": {"name": "Aceh", "country": "Indonesia", "lat": 4.6951, "lon": 96.7494},
    "jakarta": {"name": "Jakarta", "country": "Indonesia", "lat": -6.2088, "lon": 106.8456},
    "sunda": {"name": "Sunda Region", "country": "Indonesia", "lat": -6.405, "lon": 106.064},
    "sunda kelapa": {"name": "Sunda Kelapa Port", "country": "Indonesia", "lat": -6.1263, "lon": 106.8133},

    # SRI LANKA
    "colombo": {"name": "Colombo", "country": "Sri Lanka", "lat": 6.9271, "lon": 79.8612},
    "sri lanka": {"name": "Sri Lanka", "country": "Sri Lanka", "lat": 7.8731, "lon": 80.7718}
}


def geocode_place(place: str):
    place = place.lower().strip()

    # override dictionary check
    if place in OVERRIDE_LOCATIONS:
        return OVERRIDE_LOCATIONS[place]

    # fallback open-meteo geocoding
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": place, "count": 1, "language": "en", "format": "json"}
    resp = requests.get(url, params=params, timeout=10)

    if resp.status_code != 200:
        return None

    data = resp.json()
    if "results" not in data or len(data["results"]) == 0:
        return None

    r = data["results"][0]
    return {
        "name": r.get("name"),
        "country": r.get("country"),
        "lat": r.get("latitude"),
        "lon": r.get("longitude")
    }


def fetch_weather(lat: float, lon: float):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "hourly": "temperature_2m,relativehumidity_2m,precipitation,windgusts_10m",
        "forecast_days": 1,
        "timezone": "auto"
    }
    resp = requests.get(url, params=params, timeout=10)
    if resp.status_code != 200:
        return None
    return resp.json()
