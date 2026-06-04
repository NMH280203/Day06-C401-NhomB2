import os

import httpx

from core.logging_config import get_logger, log_exception

OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

logger = get_logger("weather")


def _map_condition(temp_c: float, weather_id: int) -> str:
    if 500 <= weather_id < 600:
        return "rainy"
    if temp_c > 32:
        return "hot"
    if temp_c < 20:
        return "cold"
    return "normal"


async def fetch_weather(lat: float, lng: float) -> dict:
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return {"condition": "normal", "temp_c": 28.0, "description": "Không có API key — mặc định bình thường"}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                OPENWEATHER_URL,
                params={"lat": lat, "lon": lng, "appid": api_key, "units": "metric"},
            )
            resp.raise_for_status()
            data = resp.json()
        temp_c = float(data["main"]["temp"])
        weather_id = int(data["weather"][0]["id"])
        description = data["weather"][0].get("description", "")
        return {
            "condition": _map_condition(temp_c, weather_id),
            "temp_c": temp_c,
            "description": description,
        }
    except Exception as exc:
        log_exception(logger, "weather fetch failed", exc, lat=lat, lng=lng)
        return {"condition": "normal", "temp_c": 28.0, "description": "Không lấy được thời tiết"}
