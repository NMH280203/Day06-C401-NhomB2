from core.logging_config import get_logger, log_event, log_exception
from models.schemas import FoodSuggestion
from services import llm
from services.fallback_menu import pick_fallback_foods

logger = get_logger("food_search")

FOOD_JSON_SYSTEM = """Bạn là chuyên gia ẩm thực Việt Nam.
Gợi ý 3–5 món ăn phù hợp tiêu chí. Trả JSON:
{"foods": [{"name": "...", "category": "...", "description": "...", "estimated_price": 50000, "reason": "...", "tags": ["..."]}]}
estimated_price là VND. Tôn trọng allergies — không gợi ý món vi phạm.

Nếu prompt có location_priority hoặc location_address — ưu tiên món đặc trưng ĐÚNG khu vực user nêu
(Hà Nội vs Sài Gòn vs Đà Nẵng), không gợi ý món chỉ có ở miền khác trừ khi phổ biến toàn quốc."""


async def handle(tool_input: dict) -> dict:
    meal_time = tool_input.get("meal_time", "lunch")
    budget = int(tool_input.get("budget", 80000))
    preferences = tool_input.get("preferences", [])
    allergies = tool_input.get("allergies", [])
    weather = tool_input.get("weather", "normal")
    purpose = tool_input.get("purpose", "solo")

    location_lines = ""
    if tool_input.get("location_address"):
        location_lines = (
            f"location_priority: user area — {tool_input['location_address']}\n"
            f"(Gợi ý món đặc trưng hoặc phổ biến tại khu vực này.)\n"
        )
    elif tool_input.get("lat") is not None and tool_input.get("lng") is not None:
        location_lines = (
            f"location: lat={tool_input['lat']}, lng={tool_input['lng']}\n"
            f"(Ưu tiên món phù hợp vùng gần tọa độ này.)\n"
        )

    prompt = (
        location_lines
        + f"meal_time: {meal_time}\n"
        f"budget: {budget} VND\n"
        f"preferences: {preferences}\n"
        f"allergies: {allergies}\n"
        f"weather: {weather}\n"
        f"purpose: {purpose}"
    )
    try:
        data = await llm.call_json(FOOD_JSON_SYSTEM, prompt)
        foods_raw = data.get("foods", [])
        foods = [FoodSuggestion.model_validate(f).model_dump() for f in foods_raw]
        if foods:
            return {"foods": foods}
        log_event(logger, "food_search LLM empty foods, using static menu")
    except Exception as exc:
        log_exception(logger, "food_search LLM failed, using static menu", exc)

    fallback = pick_fallback_foods(
        meal_time=str(meal_time),
        budget=budget,
        preferences=list(preferences) if preferences else [],
        allergies=list(allergies) if allergies else [],
        weather=str(weather),
        purpose=str(purpose),
        limit=5,
        user_text=tool_input.get("user_text") or "",
    )
    log_event(
        logger,
        "food_search static menu",
        count=len(fallback),
        names=",".join(f["name"] for f in fallback[:5]),
    )
    return {"foods": fallback}
