from core.logging_config import get_logger, log_exception
from models.schemas import FoodSuggestion
from services import llm

logger = get_logger("food_search")

FOOD_JSON_SYSTEM = """Bạn là chuyên gia ẩm thực Việt Nam.
Gợi ý 3–5 món ăn phù hợp tiêu chí. Trả JSON:
{"foods": [{"name": "...", "category": "...", "description": "...", "estimated_price": 50000, "reason": "...", "tags": ["..."]}]}
estimated_price là VND. Tôn trọng allergies — không gợi ý món vi phạm."""


async def handle(tool_input: dict) -> dict:
    prompt = (
        f"meal_time: {tool_input.get('meal_time', 'lunch')}\n"
        f"budget: {tool_input.get('budget', 80000)} VND\n"
        f"preferences: {tool_input.get('preferences', [])}\n"
        f"allergies: {tool_input.get('allergies', [])}\n"
        f"weather: {tool_input.get('weather', 'normal')}\n"
        f"purpose: {tool_input.get('purpose', 'solo')}"
    )
    try:
        data = await llm.call_json(FOOD_JSON_SYSTEM, prompt)
        foods_raw = data.get("foods", [])
        foods = [FoodSuggestion.model_validate(f).model_dump() for f in foods_raw]
        return {"foods": foods}
    except Exception as exc:
        log_exception(logger, "food_search LLM failed, using static menu", exc)
        fallback = [
            FoodSuggestion(
                name="Phở bò tái",
                category="Món nước",
                description="Phở truyền thống, no nhẹ",
                estimated_price=min(int(tool_input.get("budget", 80000)), 65000),
                reason="Phù hợp bữa trưa, dễ tìm quán",
                tags=["no_spicy", "popular"],
            ).model_dump(),
            FoodSuggestion(
                name="Cơm gà Hội An",
                category="Cơm",
                description="Cơm gà thơm, vừa ngân sách",
                estimated_price=min(int(tool_input.get("budget", 80000)), 55000),
                reason="Một người, no vừa",
                tags=["local"],
            ).model_dump(),
        ]
        return {"foods": fallback}
