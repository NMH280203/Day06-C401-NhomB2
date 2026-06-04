import math
import os

import httpx

from core.logging_config import get_logger, log_exception
from models.schemas import Restaurant

NEARBY_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"

logger = get_logger("places")


def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return round(2 * r * math.asin(math.sqrt(a)), 2)


def _mock_restaurants(lat: float, lng: float, query: str) -> list[dict]:
    base = [
        {
            "place_id": "mock_1",
            "name": f"Quán {query.title()} Sài Gòn",
            "address": "12 Nguyễn Huệ, Quận 1, TP.HCM",
            "lat": lat + 0.002,
            "lng": lng + 0.001,
            "rating": 4.5,
            "price_level": 2,
            "is_open": True,
            "phone": "0281234567",
            "maps_url": "https://maps.google.com/?q=mock_1",
            "photo_url": None,
            "featured_dishes": [query, "combo trưa"],
            "user_ratings_total": 320,
        },
        {
            "place_id": "mock_2",
            "name": "Nhà hàng Bếp Việt",
            "address": "45 Lê Lợi, Quận 1, TP.HCM",
            "lat": lat + 0.004,
            "lng": lng - 0.002,
            "rating": 4.2,
            "price_level": 1,
            "is_open": True,
            "phone": None,
            "maps_url": "https://maps.google.com/?q=mock_2",
            "photo_url": None,
            "featured_dishes": ["phở", "bún"],
            "user_ratings_total": 180,
        },
        {
            "place_id": "mock_3",
            "name": "Healthy Bowl Corner",
            "address": "8 Pasteur, Quận 1, TP.HCM",
            "lat": lat - 0.003,
            "lng": lng + 0.003,
            "rating": 4.7,
            "price_level": 3,
            "is_open": False,
            "phone": "0289876543",
            "maps_url": "https://maps.google.com/?q=mock_3",
            "photo_url": None,
            "featured_dishes": ["salad", "bowl healthy"],
            "user_ratings_total": 540,
        },
    ]
    for item in base:
        item["distance_km"] = _haversine_km(lat, lng, item["lat"], item["lng"])
    return base


def _map_place_result(place: dict, origin_lat: float, origin_lng: float) -> dict:
    loc = place.get("geometry", {}).get("location", {})
    plat = loc.get("lat", origin_lat)
    plng = loc.get("lng", origin_lng)
    place_id = place.get("place_id", "")
    return {
        "place_id": place_id,
        "name": place.get("name", "Unknown"),
        "address": place.get("vicinity") or place.get("formatted_address", ""),
        "lat": plat,
        "lng": plng,
        "distance_km": _haversine_km(origin_lat, origin_lng, plat, plng),
        "rating": float(place.get("rating", 0)),
        "price_level": int(place.get("price_level", 2)),
        "is_open": place.get("opening_hours", {}).get("open_now", True),
        "phone": None,
        "maps_url": f"https://www.google.com/maps/place/?q=place_id:{place_id}",
        "photo_url": None,
        "featured_dishes": [],
        "user_ratings_total": int(place.get("user_ratings_total", 0)),
    }


async def search_nearby(
    lat: float,
    lng: float,
    query: str,
    radius: int = 2000,
) -> list[dict]:
    api_key = os.getenv("GOOGLE_PLACES_API_KEY")
    if not api_key:
        return _mock_restaurants(lat, lng, query)

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                NEARBY_URL,
                params={
                    "location": f"{lat},{lng}",
                    "radius": radius,
                    "keyword": query,
                    "key": api_key,
                    "language": "vi",
                },
            )
            resp.raise_for_status()
            data = resp.json()
        if data.get("status") not in ("OK", "ZERO_RESULTS"):
            logger.warning("Places nearby status: %s", data.get("status"))
            return _mock_restaurants(lat, lng, query)
        results = data.get("results", [])
        return [_map_place_result(p, lat, lng) for p in results]
    except Exception as exc:
        log_exception(logger, "Places search failed", exc, lat=lat, lng=lng, query=query)
        return _mock_restaurants(lat, lng, query)


async def get_detail(place_id: str) -> dict | None:
    api_key = os.getenv("GOOGLE_PLACES_API_KEY")
    if not api_key or place_id.startswith("mock_"):
        mocks = _mock_restaurants(10.7769, 106.7009, "ăn")
        for m in mocks:
            if m["place_id"] == place_id:
                return m
        return mocks[0] if mocks else None

    fields = "name,formatted_address,formatted_phone_number,opening_hours,rating,price_level,geometry,url,photos"
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                DETAILS_URL,
                params={"place_id": place_id, "fields": fields, "key": api_key, "language": "vi"},
            )
            resp.raise_for_status()
            data = resp.json()
        result = data.get("result")
        if not result:
            return None
        loc = result.get("geometry", {}).get("location", {})
        lat, lng = loc.get("lat", 0), loc.get("lng", 0)
        return {
            "place_id": place_id,
            "name": result.get("name", ""),
            "address": result.get("formatted_address", ""),
            "lat": lat,
            "lng": lng,
            "distance_km": 0.0,
            "rating": float(result.get("rating", 0)),
            "price_level": int(result.get("price_level", 2)),
            "is_open": result.get("opening_hours", {}).get("open_now", True),
            "phone": result.get("formatted_phone_number"),
            "maps_url": result.get("url", f"https://www.google.com/maps/place/?q=place_id:{place_id}"),
            "photo_url": None,
            "featured_dishes": [],
            "user_ratings_total": int(result.get("user_ratings_total", 0)),
        }
    except Exception as exc:
        log_exception(logger, "Places detail failed", exc, place_id=place_id)
        return None


def to_restaurant(raw: dict, score: float = 0.0) -> Restaurant:
    return Restaurant(
        place_id=raw["place_id"],
        name=raw["name"],
        address=raw["address"],
        distance_km=raw.get("distance_km", 0.0),
        rating=raw.get("rating", 0.0),
        price_level=raw.get("price_level", 2),
        is_open=raw.get("is_open", True),
        phone=raw.get("phone"),
        maps_url=raw.get("maps_url", ""),
        photo_url=raw.get("photo_url"),
        featured_dishes=raw.get("featured_dishes", []),
        score=score,
    )
