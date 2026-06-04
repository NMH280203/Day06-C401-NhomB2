from tools.handlers import food_search, places, ranking, weather

ASK_TOOLS = {"ask_user_for_context"}


async def execute(tool_name: str, tool_input: dict) -> dict:
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
