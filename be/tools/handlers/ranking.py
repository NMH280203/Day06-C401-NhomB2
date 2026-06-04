from models.schemas import Restaurant
from services.places import to_restaurant


def _norm(value: float, lo: float, hi: float) -> float:
    if hi <= lo:
        return 1.0
    return max(0.0, min(1.0, (value - lo) / (hi - lo)))


def _food_match_score(restaurant: dict, food_names: list[str]) -> float:
    if not food_names:
        return 0.5
    haystack = " ".join(
        [
            restaurant.get("name", ""),
            " ".join(restaurant.get("featured_dishes", [])),
        ]
    ).lower()
    hits = sum(1 for f in food_names if f.lower() in haystack)
    return hits / len(food_names) if food_names else 0.0


async def handle(tool_input: dict) -> dict:
    raw_list: list[dict] = tool_input.get("restaurants", [])
    food_names: list[str] = tool_input.get("food_names", [])
    top_n = int(tool_input.get("top_n", 5))

    if not raw_list:
        return {"restaurants": []}

    ratings = [r.get("rating", 0) for r in raw_list]
    distances = [r.get("distance_km", 0) for r in raw_list]
    reviews = [r.get("user_ratings_total", 0) for r in raw_list]
    prices = [r.get("price_level", 2) for r in raw_list]

    r_max, r_min = max(ratings), min(ratings)
    d_max, d_min = max(distances), min(distances)
    rev_max, rev_min = max(reviews), min(reviews)

    scored: list[Restaurant] = []
    for r in raw_list:
        food_match = _food_match_score(r, food_names)
        rating_n = _norm(r.get("rating", 0), r_min, r_max)
        dist_n = 1.0 - _norm(r.get("distance_km", 0), d_min, d_max)
        price_n = 1.0 - _norm(r.get("price_level", 2), min(prices), max(prices))
        reviews_n = _norm(r.get("user_ratings_total", 0), rev_min, rev_max)

        score = (
            food_match * 0.3
            + rating_n * 0.25
            + dist_n * 0.2
            + price_n * 0.15
            + reviews_n * 0.1
        )
        scored.append(to_restaurant(r, round(score, 4)))

    scored.sort(key=lambda x: x.score, reverse=True)
    top = scored[:top_n]
    return {"restaurants": [r.model_dump() for r in top]}
