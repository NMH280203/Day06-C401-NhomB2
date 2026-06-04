import json
from typing import Any

from core.logging_config import get_logger, log_exception
from models.schemas import FoodSuggestion, UserContext
from prompt.builder import build_system_prompt
from services import llm
from services.llm_errors import is_llm_unavailable
from services.llm_messages import response_to_assistant_message
from tools import definitions, executor

logger = get_logger("food_agent")

AGENT_SYSTEM = """Bạn là food agent. Dùng tools để lấy thời tiết (nếu có vị trí) và gợi ý món.

VỊ TRÍ: Nếu context có địa điểm user nhập (quận/thành phố), gợi ý món phù hợp vùng đó
(vd: Hà Nội vs Sài Gòn). Không bỏ qua địa điểm user nêu.

Khi đủ thông tin, tóm tắt ngắn các món đã tìm được.
Nếu thiếu budget hoặc meal_time quan trọng, dùng ask_user_for_context."""


def _context_dict(context: UserContext) -> dict:
    return context.model_dump()


def _food_search_params(context: UserContext, **extra: object) -> dict:
    params: dict = {
        "meal_time": context.meal_time or "lunch",
        "budget": context.budget or 80000,
        "preferences": context.preferences,
        "allergies": context.allergies,
        "purpose": context.purpose or "solo",
    }
    if context.location:
        params["lat"] = context.location.lat
        params["lng"] = context.location.lng
        if context.location.address:
            params["location_address"] = context.location.address
    params.update(extra)
    return params


async def _run_without_llm(context: UserContext) -> dict:
    weather = "normal"
    if context.location:
        w = await executor.execute(
            "get_weather",
            {"lat": context.location.lat, "lng": context.location.lng},
        )
        weather = w.get("condition", "normal")
    result = await executor.execute(
        "search_food_by_criteria",
        _food_search_params(context, weather=weather),
    )
    foods = result.get("foods", [])
    return {"foods": foods, "food_names": [f["name"] for f in foods]}


async def run(context: UserContext) -> dict:
    system = build_system_prompt(context) + "\n\n" + AGENT_SYSTEM
    user_note = (
        "Hãy gợi ý món phù hợp. Dùng search_food_by_criteria sau khi biết weather (nếu có location)."
    )
    messages: list[dict] = [{"role": "user", "content": user_note}]
    collected_foods: list[dict] = []

    for _ in range(8):
        try:
            response = await llm.call(system=system, messages=messages, tools=definitions.food_tools)
        except Exception as exc:
            log_exception(logger, "food_agent llm failed", exc)
            if is_llm_unavailable(exc):
                return await _run_without_llm(context)
            return {"foods": [], "food_names": [], "error": str(exc)}

        if response.stop_reason == "end_turn":
            foods = collected_foods
            if not foods:
                result = await executor.execute(
                    "search_food_by_criteria",
                    _food_search_params(context, weather="normal"),
                )
                foods = result.get("foods", [])
            names = [f["name"] for f in foods]
            return {"foods": foods, "food_names": names}

        if response.stop_reason != "tool_use":
            break

        messages.append(response_to_assistant_message(response))
        tool_uses = [b for b in response.content if b.type == "tool_use"]
        tool_results_content = []

        for tu in tool_uses:
            inp = dict(tu.input)
            if tu.name == "get_weather" and context.location:
                inp.setdefault("lat", context.location.lat)
                inp.setdefault("lng", context.location.lng)
            if tu.name == "search_food_by_criteria":
                for k, v in _food_search_params(context).items():
                    inp.setdefault(k, v)

            result = await executor.execute(tu.name, inp)
            if result.get("ask"):
                return {
                    "ask": True,
                    "field": result["field"],
                    "message": result["message"],
                }
            if tu.name == "search_food_by_criteria":
                collected_foods.extend(result.get("foods", []))

            tool_results_content.append(
                {
                    "type": "tool_result",
                    "tool_use_id": tu.id,
                    "content": json.dumps(result, ensure_ascii=False),
                }
            )

        messages.append({"role": "user", "content": tool_results_content})

    names = [f["name"] for f in collected_foods]
    return {"foods": collected_foods, "food_names": names}
