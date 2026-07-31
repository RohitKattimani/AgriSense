"""
Weather forecast service. Uses OpenWeather's One Call / 5-day forecast API
if OPENWEATHER_API_KEY is set and WEATHER_PROVIDER=openweather, otherwise
generates a deterministic, seeded mock forecast so the app works offline.
"""
from __future__ import annotations
import random
import logging
from datetime import date, timedelta
from typing import Dict, List, Optional

import httpx

from app.config import settings

logger = logging.getLogger("agrisense.weather")


def _mock_forecast(lat: float, lon: float, days: int = 5) -> List[Dict]:
    seed = int((lat + 90) * 1000) + int((lon + 180) * 1000)
    rng = random.Random(seed + date.today().toordinal())
    forecast = []
    for i in range(days):
        d = date.today() + timedelta(days=i)
        rain_chance = round(rng.uniform(0, 1), 2)
        forecast.append({
            "date": d.isoformat(),
            "temp_c_min": round(rng.uniform(18, 24), 1),
            "temp_c_max": round(rng.uniform(28, 38), 1),
            "rain_probability": rain_chance,
            "condition": "Rain" if rain_chance > 0.6 else ("Cloudy" if rain_chance > 0.3 else "Clear"),
        })
    return forecast


def get_forecast(lat: float = 12.9716, lon: float = 77.5946, days: int = 5) -> Dict:
    """Returns {location, days: [...], rain_expected_within_days}"""
    if settings.WEATHER_PROVIDER == "openweather" and settings.OPENWEATHER_API_KEY:
        try:
            resp = httpx.get(
                "https://api.openweathermap.org/data/2.5/forecast",
                params={"lat": lat, "lon": lon, "appid": settings.OPENWEATHER_API_KEY, "units": "metric"},
                timeout=10,
            )
            resp.raise_for_status()
            raw = resp.json()
            by_day: Dict[str, Dict] = {}
            for entry in raw.get("list", []):
                d = entry["dt_txt"].split(" ")[0]
                by_day.setdefault(d, {"temps": [], "rain": []})
                by_day[d]["temps"].append(entry["main"]["temp"])
                by_day[d]["rain"].append(entry.get("pop", 0))
            days_out = []
            for d, v in list(by_day.items())[:days]:
                days_out.append({
                    "date": d,
                    "temp_c_min": round(min(v["temps"]), 1),
                    "temp_c_max": round(max(v["temps"]), 1),
                    "rain_probability": round(max(v["rain"]), 2),
                    "condition": "Rain" if max(v["rain"]) > 0.5 else "Clear/Cloudy",
                })
            source = "openweather"
        except Exception as e:
            logger.warning(f"OpenWeather call failed, using mock forecast: {e}")
            days_out = _mock_forecast(lat, lon, days)
            source = "mock (openweather call failed)"
    else:
        days_out = _mock_forecast(lat, lon, days)
        source = "mock"

    rain_day = next((i for i, d in enumerate(days_out) if d["rain_probability"] >= 0.5), None)

    return {
        "location": {"lat": lat, "lon": lon},
        "source": source,
        "forecast": days_out,
        "rain_expected_within_days": rain_day,
    }
