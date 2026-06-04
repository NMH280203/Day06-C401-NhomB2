"""Tìm quán ăn qua Overpass API (OpenStreetMap) — không cần Google Places key."""

from __future__ import annotations

import logging
import math
import os
import re
from typing import Any

import httpx

from core.logging_config import get_logger, log_event, log_exception, log_restaurants
from models.schemas import Restaurant

DEFAULT_OVERPASS_URL = "https://overpass-api.de/api/interpreter"
AMENITY_REGEX = "restaurant|cafe|fast_food|food_court|biergarten|bar|pub"

logger = get_logger("places")


def _overpass_url() -> str:
    return os.getenv("OVERPASS_API_URL", DEFAULT_OVERPASS_URL).rstrip("/")


def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return round(2 * r * math.asin(math.sqrt(a)), 2)


def _build_address(tags: dict[str, Any]) -> str:
    parts = [
        tags.get("addr:housenumber"),
        tags.get("addr:street"),
        tags.get("addr:suburb") or tags.get("addr:district"),
        tags.get("addr:city") or tags.get("addr:province"),
    ]
    text = ", ".join(p for p in parts if p)
    return text or tags.get("addr:full", "Địa chỉ chưa có trên OSM")


def _element_coords(element: dict) -> tuple[float, float] | None:
    if element.get("type") == "node":
        lat, lng = element.get("lat"), element.get("lon")
        if lat is not None and lng is not None:
            return float(lat), float(lng)
    center = element.get("center") or {}
    lat, lng = center.get("lat"), center.get("lon")
    if lat is not None and lng is not None:
        return float(lat), float(lng)
    return None


def _osm_maps_url(element_type: str, osm_id: int, lat: float, lng: float) -> str:
    return f"https://www.openstreetmap.org/{element_type}/{osm_id}#map=18/{lat}/{lng}"


def _featured_dishes(tags: dict[str, Any]) -> list[str]:
    dishes: list[str] = []
    cuisine = tags.get("cuisine")
    if cuisine:
        dishes.extend(c.strip() for c in str(cuisine).split(";") if c.strip())
    for key in ("diet:vegetarian", "diet:vegan"):
        if tags.get(key) == "yes":
            dishes.append("chay")
    return dishes[:5]


def _estimate_rating(osm_id: int) -> float:
    """OSM không có rating — ước lượng ổn định cho ranking."""
    return round(3.8 + (osm_id % 12) * 0.1, 1)


def _estimate_price_level(tags: dict[str, Any]) -> int:
    if tags.get("diet:vegetarian") == "yes" or tags.get("cuisine") == "healthy":
        return 2
    amenity = tags.get("amenity", "")
    if amenity in ("fast_food", "cafe"):
        return 1
    if tags.get("cuisine") in ("fine_dining", "japanese", "korean"):
        return 3
    return 2


def _matches_query(tags: dict[str, Any], query: str) -> bool:
    q = query.strip().lower()
    if not q or q in {"nhà hàng", "restaurant", "ăn", "food", "quán"}:
        return True
    haystack = " ".join(
        str(tags.get(k, ""))
        for k in ("name", "name:vi", "name:en", "cuisine", "amenity", "description")
    ).lower()
    words = [w for w in re.split(r"\W+", q) if len(w) > 2]
    if not words:
        return True
    return any(w in haystack for w in words)


def _map_osm_element(
    element: dict,
    origin_lat: float,
    origin_lng: float,
) -> dict | None:
    tags = element.get("tags") or {}
    name = tags.get("name") or tags.get("name:vi") or tags.get("name:en")
    if not name:
        return None

    coords = _element_coords(element)
    if not coords:
        return None
    plat, plng = coords
    osm_type = element.get("type", "node")
    osm_id = int(element["id"])
    place_id = f"{osm_type}/{osm_id}"

    return {
        "place_id": place_id,
        "name": name,
        "address": _build_address(tags),
        "lat": plat,
        "lng": plng,
        "distance_km": _haversine_km(origin_lat, origin_lng, plat, plng),
        "rating": _estimate_rating(osm_id),
        "price_level": _estimate_price_level(tags),
        "is_open": True,
        "phone": tags.get("phone") or tags.get("contact:phone"),
        "maps_url": _osm_maps_url(osm_type, osm_id, plat, plng),
        "photo_url": None,
        "featured_dishes": _featured_dishes(tags),
        "user_ratings_total": max(10, osm_id % 500),
    }


def _nearby_overpass_query(lat: float, lng: float, radius: int) -> str:
    return f"""
[out:json][timeout:25];
(
  node["amenity"~"{AMENITY_REGEX}"](around:{radius},{lat},{lng});
  way["amenity"~"{AMENITY_REGEX}"](around:{radius},{lat},{lng});
);
out center tags;
""".strip()


def _detail_overpass_query(osm_type: str, osm_id: int) -> str:
    return f"""
[out:json][timeout:15];
{osm_type}({osm_id});
out center tags;
""".strip()


async def _run_overpass(query: str) -> list[dict]:
    url = _overpass_url()
    headers = {
        "User-Agent": os.getenv("OVERPASS_USER_AGENT", "FoodChat/1.0 (VinAI hackathon)"),
        "Accept": "*/*",
    }
    async with httpx.AsyncClient(timeout=35.0) as client:
        resp = await client.post(url, data={"data": query}, headers=headers)
        resp.raise_for_status()
        data = resp.json()
    return data.get("elements", [])


def _mock_restaurants(lat: float, lng: float, query: str) -> list[dict]:
    """Fallback khi Overpass lỗi."""
    base = [
        {
            "place_id": "node/mock_1",
            "name": f"Quán {query.title()} (mock)",
            "address": "Gần vị trí của bạn",
            "lat": lat + 0.002,
            "lng": lng + 0.001,
            "rating": 4.3,
            "price_level": 2,
            "is_open": True,
            "phone": None,
            "maps_url": f"https://www.openstreetmap.org/#map=17/{lat}/{lng}",
            "photo_url": None,
            "featured_dishes": [query],
            "user_ratings_total": 50,
        },
    ]
    for item in base:
        item["distance_km"] = _haversine_km(lat, lng, item["lat"], item["lng"])
    return base


async def search_nearby(
    lat: float,
    lng: float,
    query: str,
    radius: int = 2000,
) -> list[dict]:
    try:
        elements = await _run_overpass(_nearby_overpass_query(lat, lng, radius))
        mapped: list[dict] = []
        for el in elements:
            if not _matches_query(el.get("tags") or {}, query):
                continue
            item = _map_osm_element(el, lat, lng)
            if item:
                mapped.append(item)
        mapped.sort(key=lambda x: x["distance_km"])
        if mapped:
            top = mapped[:20]
            log_event(
                logger,
                "Overpass search ok",
                query=query,
                lat=lat,
                lng=lng,
                radius=radius,
                raw=len(elements),
                matched=len(mapped),
                returned=len(top),
            )
            log_restaurants(logger, "Overpass hit", top)
            return top
        log_event(
            logger,
            "Overpass zero results, using mock",
            level=logging.WARNING,
            query=query,
            lat=lat,
            lng=lng,
            radius=radius,
        )
        mock = _mock_restaurants(lat, lng, query)
        log_restaurants(logger, "Overpass mock", mock)
        return mock
    except Exception as exc:
        log_exception(logger, "Overpass search failed", exc, lat=lat, lng=lng, query=query)
        mock = _mock_restaurants(lat, lng, query)
        log_event(logger, "Overpass error mock fallback", query=query, lat=lat, lng=lng)
        log_restaurants(logger, "Overpass mock", mock)
        return mock


def _parse_place_id(place_id: str) -> tuple[str, int] | None:
    if place_id.startswith("mock_") or "/" not in place_id:
        return None
    osm_type, raw_id = place_id.split("/", 1)
    if osm_type not in ("node", "way", "relation"):
        return None
    try:
        return osm_type, int(raw_id)
    except ValueError:
        return None


async def get_detail(place_id: str) -> dict | None:
    parsed = _parse_place_id(place_id)
    if not parsed:
        mocks = _mock_restaurants(10.7769, 106.7009, "ăn")
        for m in mocks:
            if m["place_id"] == place_id:
                return m
        return mocks[0] if mocks else None

    osm_type, osm_id = parsed
    try:
        elements = await _run_overpass(_detail_overpass_query(osm_type, osm_id))
        if not elements:
            return None
        item = _map_osm_element(elements[0], 0.0, 0.0)
        if item:
            item["distance_km"] = 0.0
        return item
    except Exception as exc:
        log_exception(logger, "Overpass detail failed", exc, place_id=place_id)
        return None


def to_restaurant(raw: dict, score: float = 0.0) -> Restaurant:
    return Restaurant(
        place_id=raw["place_id"],
        name=raw["name"],
        address=raw["address"],
        lat=raw.get("lat"),
        lng=raw.get("lng"),
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
