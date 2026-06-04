from fastapi import APIRouter, Query

from core.logging_config import get_logger, log_exception
from models.schemas import RestaurantQueryParams
from tools.handlers import places, ranking

router = APIRouter()
logger = get_logger("restaurants")


@router.get("/restaurants")
async def list_restaurants(
    lat: float = Query(...),
    lng: float = Query(...),
    query: str = Query(...),
    budget: int | None = Query(None),
    radius: int = Query(2000),
    limit: int = Query(5),
):
    params = RestaurantQueryParams(
        lat=lat,
        lng=lng,
        query=query,
        budget=budget,
        radius=radius,
        limit=limit,
    )
    try:
        search_result = await places.search(
            {
                "lat": params.lat,
                "lng": params.lng,
                "query": params.query,
                "radius": params.radius,
                "budget": params.budget,
            }
        )
        rank_result = await ranking.handle(
            {
                "restaurants": search_result.get("restaurants", []),
                "food_names": [params.query],
                "top_n": params.limit,
            }
        )
        restaurants = rank_result.get("restaurants", [])
        logger.info(
            "GET /api/restaurants | query=%s lat=%s lng=%s total=%d",
            params.query,
            params.lat,
            params.lng,
            len(restaurants),
        )
        return {
            "restaurants": restaurants,
            "total": len(restaurants),
            "query_used": params.query,
        }
    except Exception as exc:
        log_exception(
            logger,
            "restaurants endpoint failed",
            exc,
            query=params.query,
            lat=params.lat,
            lng=params.lng,
        )
        return {
            "restaurants": [],
            "total": 0,
            "query_used": params.query,
            "error": "Xin lỗi, không tìm được quán lúc này. Vui lòng thử lại.",
        }
