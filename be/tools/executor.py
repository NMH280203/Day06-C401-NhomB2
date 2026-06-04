from core.logging_config import get_logger, log_event
from tools.handlers import food_search, places, ranking, weather

ASK_TOOLS = {"ask_user_for_context"}
logger = get_logger("tools")


async def execute(tool_name: str, tool_input: dict) -> dict:
    summary = {
        k: tool_input[k]
        for k in ("lat", "lng", "query", "radius", "place_id", "top_n", "field")
        if k in tool_input
    }
    if tool_name == "rank_restaurants":
        summary["input_count"] = len(tool_input.get("restaurants", []))
        summary["foods"] = ",".join(tool_input.get("food_names", [])[:5])
    log_event(logger, "Tool execute", tool=tool_name, **summary)

    if tool_name == "get_weather":
        return await weather.handle(tool_input)
    if tool_name == "search_food_by_criteria":
        return await food_search.handle(tool_input)
    if tool_name == "search_nearby_restaurants":
        return await places.search(tool_input)
    if tool_name == "get_restaurant_detail":
        return await places.detail(tool_input)
    if tool_name == "rank_restaurants":
        return await ranking.handle(tool_input)
    if tool_name == "ask_user_for_context":
        return {
            "ask": True,
            "field": tool_input.get("field", "unknown"),
            "message": tool_input.get("message", "Bạn có thể cho mình thêm thông tin không?"),
        }
    return {"error": f"Unknown tool: {tool_name}"}
