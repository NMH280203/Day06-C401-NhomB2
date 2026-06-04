from services import places as places_service


async def search(tool_input: dict) -> dict:
    lat = float(tool_input["lat"])
    lng = float(tool_input["lng"])
    query = str(tool_input.get("query", "nhà hàng"))
    radius = int(tool_input.get("radius", 2000))
    results = await places_service.search_nearby(lat, lng, query, radius)
    return {"restaurants": results}


async def detail(tool_input: dict) -> dict:
    place_id = str(tool_input["place_id"])
    result = await places_service.get_detail(place_id)
    if result is None:
        return {"restaurant": None, "error": "not_found"}
    return {"restaurant": result}
