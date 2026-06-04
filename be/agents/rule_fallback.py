"""Rule-based chat flow when Gemini is unavailable (quota, invalid key, etc.)."""

import re
from typing import Awaitable, Callable

from core.logging_config import get_logger, log_event, log_location, log_restaurants
from models.schemas import Message, UserContext
from services.chat_response import finish, respond_ask, stream_text
from services.geo_hints import apply_location_priority
from services.out_of_scope import respond as respond_out_of_scope
from services.scope import is_food_related
from tools import executor

StreamCallback = Callable[[str, dict], Awaitable[None]]
logger = get_logger("rule_fallback")


def _last_user_text(messages: list[Message]) -> str:
    for m in reversed(messages):
        if m.role == "user" and m.content.strip():
            return m.content.strip().lower()
    return ""


def _parse_budget(text: str, ctx: UserContext) -> int:
    if ctx.budget:
        return ctx.budget
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*triệu", text)
    if m:
        return int(float(m.group(1).replace(",", ".")) * 1_000_000)
    m = re.search(r"(\d+)\s*k\b", text, re.I)
    if m:
        return int(m.group(1)) * 1000
    m = re.search(r"(\d{2,3})\s*(?:k|nghìn|ngàn)", text)
    if m:
        return int(m.group(1)) * 1000
    m = re.search(r"(?:dưới|tối đa|khoảng|~)\s*(\d{2,4})\s*k", text, re.I)
    if m:
        return int(m.group(1)) * 1000
    m = re.search(r"\b(\d{4,7})\b", text)
    if m:
        v = int(m.group(1))
        return v if v < 500_000 else min(v, 500_000)
    return 80000


def _parse_meal_time(text: str, ctx: UserContext) -> str:
    if ctx.meal_time:
        return ctx.meal_time
    if any(w in text for w in ("sáng", "breakfast")):
        return "breakfast"
    if any(w in text for w in ("trưa", "lunch")):
        return "lunch"
    if any(w in text for w in ("tối", "chiều", "dinner")):
        return "dinner"
    if any(w in text for w in ("xế", "snack", "vặt")):
        return "snack"
    return "lunch"


def _parse_preferences(text: str, ctx: UserContext) -> list[str]:
    prefs = list(ctx.preferences or [])
    keywords = {
        "healthy": "healthy",
        "ăn nhẹ": "light",
        "nhẹ": "light",
        "không cay": "no_spicy",
        "không ớt": "no_spicy",
        "chay": "vegetarian",
        "đổi gió": "variety",
        "nhanh": "fast",
    }
    for k, v in keywords.items():
        if k in text and v not in prefs:
            prefs.append(v)
    return prefs


def _parse_allergies(text: str, ctx: UserContext) -> list[str]:
    allergies = list(ctx.allergies or [])
    for term in ("chay", "hải sản", "gluten", "lactose", "đậu nành", "tôm", "cua"):
        if term in text and term not in allergies:
            allergies.append(term)
    return allergies


def _is_vague(text: str, ctx: UserContext) -> bool:
    if len(text) > 50:
        return False
    vague_phrases = ("ăn gì", "gì ngon", "không biết ăn")
    if any(p in text for p in vague_phrases):
        return not ctx.budget and not re.search(r"\d", text)
    return len(text) < 8 and not ctx.budget


async def run(
    messages: list[Message],
    context: UserContext,
    stream_callback: StreamCallback,
    reason: str = "",
) -> None:
    text = _last_user_text(messages)
    log_event(logger, "Rule fallback start", reason=reason[:200], user=text[:120])

    if text and not is_food_related(text):
        await respond_out_of_scope(stream_callback)
        return

    context, loc_src = apply_location_priority(context, text)
    if context.location:
        log_location(logger, "Rule fallback location", context.location.lat, context.location.lng)
    if loc_src:
        log_event(logger, "Rule fallback location", source=loc_src)

    await stream_callback(
        "thinking",
        {
            "status": "Chế độ dự phòng — Gemini tạm không khả dụng, dùng gợi ý theo quy tắc",
        },
    )

    if _is_vague(text, context):
        await respond_ask(
            stream_callback,
            "budget",
            "Bạn muốn ăn với ngân sách khoảng bao nhiêu (vd: 50k, 80k) và mấy người ạ?",
        )
        return

    meal_time = _parse_meal_time(text, context)
    budget = _parse_budget(text, context)
    preferences = _parse_preferences(text, context)
    allergies = _parse_allergies(text, context)
    weather = "normal"

    if context.location:
        w = await executor.execute(
            "get_weather",
            {"lat": context.location.lat, "lng": context.location.lng},
        )
        weather = w.get("condition", "normal")

    food_params: dict = {
        "meal_time": meal_time,
        "budget": budget,
        "preferences": preferences,
        "allergies": allergies,
        "weather": weather,
        "purpose": context.purpose or "solo",
    }
    if context.location:
        food_params["lat"] = context.location.lat
        food_params["lng"] = context.location.lng
        if context.location.address:
            food_params["location_address"] = context.location.address
    food_result = await executor.execute("search_food_by_criteria", food_params)
    foods = food_result.get("foods", [])
    food_names = [f["name"] for f in foods]
    await stream_callback("food_results", {"foods": foods, "food_names": food_names})

    restaurants: list[dict] = []
    if context.location and food_names:
        query = " ".join(food_names[:2])
        search = await executor.execute(
            "search_nearby_restaurants",
            {
                "lat": context.location.lat,
                "lng": context.location.lng,
                "query": query,
                "radius": 2000,
                "budget": budget,
            },
        )
        rank = await executor.execute(
            "rank_restaurants",
            {
                "restaurants": search.get("restaurants", []),
                "food_names": food_names,
                "top_n": 5,
            },
        )
        restaurants = rank.get("restaurants", [])
        await stream_callback("restaurant_results", {"restaurants": restaurants})

    names = ", ".join(food_names[:3]) if food_names else "một vài món phù hợp"
    loc_note = (
        f" Mình cũng tìm được {len(restaurants)} quán gần bạn."
        if restaurants
        else " Bạn cho phép vị trí để mình gợi ý quán nhé."
    )
    summary = (
        f"Dựa trên ngữ cảnh (khoảng {budget:,}đ, bữa {meal_time}), "
        f"mình gợi ý: **{names}**.{loc_note}\n\n"
        "_(Gợi ý tự động — bạn có thể hỏi thêm để tinh chỉnh.)_"
    )
    await stream_text(summary, stream_callback)
    await finish(
        stream_callback,
        [
            "Gợi ý món chay trong 50k",
            "Tìm quán gần có món này",
            "Đổi sang món healthy hơn",
        ],
    )
