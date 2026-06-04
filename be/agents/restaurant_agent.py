import json
import sys
from typing import Any

from core.logging_config import get_logger, log_event, log_exception, log_location, log_restaurants
from models.schemas import UserContext
from prompt.builder import build_system_prompt
from services import llm
from services.llm_errors import is_llm_unavailable
from services.llm_messages import response_to_assistant_message
from tools import definitions, executor

logger = get_logger("restaurant_agent")

AGENT_SYSTEM = """Bạn là restaurant agent. Tìm quán gần, rank theo món gợi ý.

VỊ TRÍ (ưu tiên cao nhất):
- Dùng ĐÚNG lat/lng trong context — đó là khu vực user nhập (quận/địa danh) hoặc GPS.
- Nếu ngữ cảnh ghi "user nhập trong chat" → không tìm quán ở thành phố/quận khác.
- search_nearby_restaurants: luôn truyền lat/lng từ context, không tự đổi tọa độ.

Nếu không có location → ask_user_for_context hỏi quận/khu vực."""


async def _run_without_llm(context: UserContext, food_names: list[str]) -> dict:
    query = " ".join(food_names) if food_names else "nhà hàng"
    search = await executor.execute(
        "search_nearby_restaurants",
        {
            "lat": context.location.lat,
            "lng": context.location.lng,
            "query": query,
            "radius": 2000,
            "budget": context.budget,
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
    return {"restaurants": rank.get("restaurants", [])}


async def run(context: UserContext, food_names: list[str]) -> dict:
    if not context.location:
        log_event(logger, "Restaurant agent ask location", foods=",".join(food_names[:5]))
        return {
            "ask": True,
            "field": "location",
            "message": "Bạn đang ở khu vực nào để mình tìm quán gần bạn nhé?",
        }

    system = build_system_prompt(context) + "\n\n" + AGENT_SYSTEM
    query = " ".join(food_names) if food_names else "nhà hàng ngon"
    log_event(
        logger,
        "Restaurant agent start",
        query=query,
        foods=",".join(food_names[:5]),
    )
    log_location(logger, "Restaurant agent search_from", context.location.lat, context.location.lng)
    messages: list[dict] = [
        {
            "role": "user",
            "content": f"Tìm quán cho món: {query}. Rank top 5.",
        }
    ]
    collected: list[dict] = []

    for _ in range(8):
        try:
            response = await llm.call(
                system=system, messages=messages, tools=definitions.restaurant_tools
            )
        except Exception as exc:
            log_exception(logger, "restaurant_agent llm failed", exc)
            if is_llm_unavailable(exc):
                return await _run_without_llm(context, food_names)
            return {"restaurants": [], "error": str(exc)}

        if response.stop_reason == "end_turn":
            if collected:
                return {"restaurants": collected}
            search_result = await executor.execute(
                "search_nearby_restaurants",
                {
                    "lat": context.location.lat,
                    "lng": context.location.lng,
                    "query": query,
                    "radius": 2000,
                    "budget": context.budget,
                },
            )
            rank_result = await executor.execute(
                "rank_restaurants",
                {
                    "restaurants": search_result.get("restaurants", []),
                    "food_names": food_names,
                    "top_n": 5,
                },
            )
            return {"restaurants": rank_result.get("restaurants", [])}

        if response.stop_reason != "tool_use":
            break

        messages.append(response_to_assistant_message(response))
        tool_uses = [b for b in response.content if b.type == "tool_use"]
        tool_results_content = []
        raw_for_rank: list[dict] = []

        for tu in tool_uses:
            inp = dict(tu.input)
            if tu.name == "search_nearby_restaurants":
                inp.setdefault("lat", context.location.lat)
                inp.setdefault("lng", context.location.lng)
                inp.setdefault("query", query)
                inp.setdefault("radius", 2000)
                if context.budget is not None:
                    inp.setdefault("budget", context.budget)
            if tu.name == "rank_restaurants":
                inp.setdefault("food_names", food_names)
                inp.setdefault("top_n", 5)
                if raw_for_rank and "restaurants" not in inp:
                    inp["restaurants"] = raw_for_rank

            result = await executor.execute(tu.name, inp)
            if result.get("ask"):
                return {
                    "ask": True,
                    "field": result["field"],
                    "message": result["message"],
                }
            if tu.name == "search_nearby_restaurants":
                raw_for_rank = result.get("restaurants", [])
                log_restaurants(logger, "Restaurant agent search", raw_for_rank[:10])
            if tu.name == "rank_restaurants":
                collected = result.get("restaurants", [])
                log_restaurants(logger, "Restaurant agent ranked", collected)

            tool_results_content.append(
                {
                    "type": "tool_result",
                    "tool_use_id": tu.id,
                    "content": json.dumps(result, ensure_ascii=False),
                }
            )

        messages.append({"role": "user", "content": tool_results_content})

    return {"restaurants": collected}
