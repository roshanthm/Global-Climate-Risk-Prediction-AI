import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List

# ---------------- BASIC HELPERS ----------------
def _safe_get(url: str, params: Dict[str, Any] = None) -> Any:
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        return None
    return None

# ---------------- RELIEFWEB (DISASTERS) ----------------
RELIEFWEB_DISASTERS_URL = "https://api.reliefweb.int/v1/disasters"

def _reliefweb_recent_flood_titles(query: str, window_days: int = 7) -> List[str]:
    data = _safe_get(
        RELIEFWEB_DISASTERS_URL,
        params={
            "appname": "gdis-climate-risk",
            "profile": "full",
            "preset": "latest",
            "limit": 50,
            "query[value]": query,
        },
    )
    if not data or "data" not in data:
        return []

    cutoff = datetime.utcnow() - timedelta(days=window_days)
    titles = []

    for d in data["data"]:
        fields = d.get("fields", {})
        title = fields.get("name") or fields.get("title") or ""
        hazard_type = fields.get("type", [{}])[0].get("name", "").lower()
        date_info = fields.get("date", {})
        date_str = (
            date_info.get("created")
            or date_info.get("original")
            or date_info.get("start")
        )
        if not date_str:
            continue

        try:
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except Exception:
            continue

        if dt < cutoff:
            continue

        text = f"{hazard_type} {title}".lower()

        if any(k in text for k in ["flood", "flash flood", "heavy rain", "landslide"]):
            titles.append(title)

    return titles


# ---------------- GDACS ----------------
GDACS_SEARCH_URL = "https://www.gdacs.org/gdacsapi/api/events/geteventlist/SEARCH"

def _gdacs_recent_flood_titles(window_days: int = 7) -> List[Dict[str, Any]]:
    todate = datetime.utcnow().date()
    fromdate = todate - timedelta(days=window_days)

    params = {
        "eventlist": "FL",
        "fromdate": fromdate.isoformat(),
        "todate": todate.isoformat(),
    }

    data = _safe_get(GDACS_SEARCH_URL, params=params)
    if not data:
        return []

    events = []
    features = data.get("features") or data.get("Features") or []

    for f in features:
        props = f.get("properties", {})
        name = props.get("eventname") or props.get("name") or ""
        country = props.get("country") or ""
        if name:
            events.append({"name": name, "country": country})

    return events


# ---------------- PUBLIC WRAPPER ----------------
def get_flood_event_signal(location_name: str, country_name: str) -> Dict[str, Any]:
    location_name = (location_name or "").strip()
    country_name = (country_name or "").strip()

    WINDOW_DAYS = 7

    rw_city = _reliefweb_recent_flood_titles(location_name, WINDOW_DAYS) if location_name else []
    rw_country = _reliefweb_recent_flood_titles(country_name, WINDOW_DAYS) if country_name else []

    gdacs = _gdacs_recent_flood_titles(WINDOW_DAYS)
    gdacs_city = []
    gdacs_country = []

    for ev in gdacs:
        name = (ev.get("name") or "").lower()
        country = (ev.get("country") or "").lower()
        if location_name and location_name.lower() in name:
            gdacs_city.append(ev["name"])
        if country_name and country_name.lower() in (country or name):
            gdacs_country.append(ev["name"])

    city_alert = bool(rw_city or gdacs_city)
    country_alert = bool(rw_country or gdacs_country)

    sources = list(dict.fromkeys(rw_city + rw_country + gdacs_city + gdacs_country))[:5]

    return {
        "city_alert": city_alert,
        "country_alert": country_alert,
        "titles": sources,
        "window_days": WINDOW_DAYS,
        "sources_used": ["ReliefWeb", "GDACS"],
    }
