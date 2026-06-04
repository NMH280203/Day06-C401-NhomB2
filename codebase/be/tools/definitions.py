orchestrator_tools: list[dict] = [
    {
        "name": "detect_intent",
        "description": (
            "Phân loại ý định. out_of_scope CHỈ khi câu KHÔNG liên quan ăn uống/F&B. "
            "Cafe, cà phê, trà sữa, quán nước, bar = IN-SCOPE (food_and_restaurant hoặc restaurant_only)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "intent": {
                    "type": "string",
                    "enum": [
                        "food_only",
                        "restaurant_only",
                        "food_and_restaurant",
                        "food_info",
                        "clarify",
                        "out_of_scope",
                    ],
                },
                "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                "missing_context": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "required": ["intent", "confidence", "missing_context"],
        },
    },
    {
        "name": "run_food_agent",
        "description": "Chạy agent gợi ý món ăn dựa trên UserContext.",
        "input_schema": {
            "type": "object",
            "properties": {
                "context": {
                    "type": "object",
                    "description": "UserContext: location, budget, people, meal_time, purpose, preferences, allergies",
                },
            },
            "required": ["context"],
        },
    },
    {
        "name": "run_restaurant_agent",
        "description": "Chạy agent tìm nhà hàng gần, có thể kèm tên món từ food agent.",
        "input_schema": {
            "type": "object",
            "properties": {
                "context": {"type": "object"},
                "food_names": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "required": ["context", "food_names"],
        },
    },
]

food_tools: list[dict] = [
    {
        "name": "get_weather",
        "description": "Lấy thời tiết hiện tại tại vị trí để gợi ý món phù hợp.",
        "input_schema": {
            "type": "object",
            "properties": {
                "lat": {"type": "number"},
                "lng": {"type": "number"},
            },
            "required": ["lat", "lng"],
        },
    },
    {
        "name": "search_food_by_criteria",
        "description": "Tìm món ăn theo tiêu chí người dùng.",
        "input_schema": {
            "type": "object",
            "properties": {
                "meal_time": {"type": "string"},
                "budget": {"type": "number"},
                "preferences": {"type": "array", "items": {"type": "string"}},
                "allergies": {"type": "array", "items": {"type": "string"}},
                "weather": {
                    "type": "string",
                    "enum": ["hot", "cold", "rainy", "normal"],
                },
                "purpose": {"type": "string"},
            },
            "required": ["meal_time", "budget", "preferences", "allergies", "weather", "purpose"],
        },
    },
    {
        "name": "ask_user_for_context",
        "description": "Hỏi người dùng thêm thông tin còn thiếu.",
        "input_schema": {
            "type": "object",
            "properties": {
                "field": {"type": "string"},
                "message": {"type": "string"},
            },
            "required": ["field", "message"],
        },
    },
]

restaurant_tools: list[dict] = [
    {
        "name": "search_nearby_restaurants",
        "description": "Tìm nhà hàng gần theo từ khóa và bán kính.",
        "input_schema": {
            "type": "object",
            "properties": {
                "lat": {"type": "number"},
                "lng": {"type": "number"},
                "query": {"type": "string"},
                "radius": {"type": "number"},
                "budget": {"type": "number"},
            },
            "required": ["lat", "lng", "query", "radius"],
        },
    },
    {
        "name": "get_restaurant_detail",
        "description": "Lấy chi tiết một nhà hàng theo place_id.",
        "input_schema": {
            "type": "object",
            "properties": {
                "place_id": {"type": "string"},
            },
            "required": ["place_id"],
        },
    },
    {
        "name": "rank_restaurants",
        "description": "Xếp hạng danh sách quán theo món và tiêu chí.",
        "input_schema": {
            "type": "object",
            "properties": {
                "restaurants": {"type": "array", "items": {"type": "object"}},
                "food_names": {"type": "array", "items": {"type": "string"}},
                "top_n": {"type": "number"},
            },
            "required": ["restaurants", "food_names"],
        },
    },
    {
        "name": "ask_user_for_context",
        "description": "Hỏi người dùng thêm thông tin còn thiếu.",
        "input_schema": {
            "type": "object",
            "properties": {
                "field": {"type": "string"},
                "message": {"type": "string"},
            },
            "required": ["field", "message"],
        },
    },
]
