from services import weather as weather_service


async def handle(tool_input: dict) -> dict:
    lat = float(tool_input["lat"])
    lng = float(tool_input["lng"])
    return await weather_service.fetch_weather(lat, lng)
