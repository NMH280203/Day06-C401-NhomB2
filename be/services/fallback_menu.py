"""Thực đơn tĩnh khi LLM food_search lỗi — lọc theo bữa, budget, preferences, allergies."""

from __future__ import annotations

from typing import Any

from models.schemas import FoodSuggestion

# Mỗi món: meal_times, tags, allergens (món chứa — loại nếu user dị ứng)
_FALLBACK_CATALOG: list[dict[str, Any]] = [
    {
        "name": "Phở bò tái",
        "category": "Món nước",
        "description": "Phở bò truyền thống, nước dùng trong",
        "estimated_price": 55000,
        "reason": "Dễ tìm quán, no vừa phải",
        "tags": ["popular", "no_spicy", "comfort"],
        "meal_times": ["breakfast", "lunch", "dinner"],
        "allergens": ["gluten"],
    },
    {
        "name": "Phở gà",
        "category": "Món nước",
        "description": "Phở gà thanh, nhẹ hơn phở bò",
        "estimated_price": 50000,
        "reason": "Phù hợp ăn nhẹ, không cay",
        "tags": ["light", "no_spicy", "healthy"],
        "meal_times": ["breakfast", "lunch", "dinner"],
        "allergens": ["gluten"],
    },
    {
        "name": "Bún chả Hà Nội",
        "category": "Bún",
        "description": "Thịt nướng than hoa, nước mắm chua ngọt",
        "estimated_price": 60000,
        "reason": "Đặc trưng miền Bắc, bữa trưa tối",
        "tags": ["popular", "local"],
        "meal_times": ["lunch", "dinner"],
        "allergens": ["hải sản"],
    },
    {
        "name": "Bún thịt nướng",
        "category": "Bún",
        "description": "Bún tươi, thịt nướng, rau sống",
        "estimated_price": 45000,
        "reason": "Giá vừa, no nhanh",
        "tags": ["fast", "popular"],
        "meal_times": ["lunch", "dinner"],
        "allergens": [],
    },
    {
        "name": "Bún bò Huế",
        "category": "Món nước",
        "description": "Bún bò cay đậm vị miền Trung",
        "estimated_price": 55000,
        "reason": "Thích vị đậm, có thể cay",
        "tags": ["spicy", "local"],
        "meal_times": ["lunch", "dinner"],
        "allergens": [],
    },
    {
        "name": "Cơm tấm sườn bì chả",
        "category": "Cơm",
        "description": "Sườn nướng, bì, chả trứng",
        "estimated_price": 50000,
        "reason": "No chắc, phổ biến Sài Gòn",
        "tags": ["popular", "fast"],
        "meal_times": ["lunch", "dinner"],
        "allergens": [],
    },
    {
        "name": "Cơm gà Hội An",
        "category": "Cơm",
        "description": "Cơm gà thơm, nước mắm gừng",
        "estimated_price": 48000,
        "reason": "Một người, vừa ngân sách",
        "tags": ["local", "no_spicy"],
        "meal_times": ["lunch", "dinner"],
        "allergens": [],
    },
    {
        "name": "Cơm niêu Singapore",
        "category": "Cơm",
        "description": "Cơm chiên hoặc cơm trắng kèm topping",
        "estimated_price": 65000,
        "reason": "Đổi gió so với cơm tấm",
        "tags": ["variety"],
        "meal_times": ["lunch", "dinner"],
        "allergens": ["hải sản"],
    },
    {
        "name": "Hủ tiếu Nam Vang",
        "category": "Món nước",
        "description": "Hủ tiếu khô hoặc nước, tôm thịt",
        "estimated_price": 45000,
        "reason": "Bữa sáng trưa nhẹ",
        "tags": ["popular"],
        "meal_times": ["breakfast", "lunch"],
        "allergens": ["hải sản", "tôm"],
    },
    {
        "name": "Mì Quảng",
        "category": "Mì",
        "description": "Mì vàng, ít nước, topping đa dạng",
        "estimated_price": 50000,
        "reason": "Đặc sản miền Trung",
        "tags": ["local"],
        "meal_times": ["lunch", "dinner"],
        "allergens": ["gluten", "hải sản", "tôm"],
    },
    {
        "name": "Bánh mì thịt nướng",
        "category": "Bánh",
        "description": "Bánh mì giòn, thịt nướng, pate",
        "estimated_price": 35000,
        "reason": "Nhanh, tiện mang đi",
        "tags": ["fast", "popular"],
        "meal_times": ["breakfast", "snack"],
        "allergens": ["gluten"],
    },
    {
        "name": "Bánh cuốn",
        "category": "Bánh",
        "description": "Bánh cuốn nóng, chả lụa, nước mắm",
        "estimated_price": 40000,
        "reason": "Bữa sáng thanh đạm",
        "tags": ["light", "no_spicy"],
        "meal_times": ["breakfast", "lunch"],
        "allergens": ["gluten"],
    },
    {
        "name": "Xôi xéo",
        "category": "Xôi",
        "description": "Xôi nếp, đậu xanh, hành phi",
        "estimated_price": 25000,
        "reason": "Sáng no, giá rẻ",
        "tags": ["vegetarian", "fast"],
        "meal_times": ["breakfast", "snack"],
        "allergens": [],
    },
    {
        "name": "Cháo lòng",
        "category": "Cháo",
        "description": "Cháo nóng, lòng heo, quẩy",
        "estimated_price": 40000,
        "reason": "Trời mưa lạnh rất hợp",
        "tags": ["comfort"],
        "meal_times": ["breakfast", "dinner"],
        "allergens": ["gluten"],
    },
    {
        "name": "Cháo gà",
        "category": "Cháo",
        "description": "Cháo gà đơn giản, dễ tiêu",
        "estimated_price": 35000,
        "reason": "Nhẹ bụng, healthy",
        "tags": ["light", "healthy", "no_spicy"],
        "meal_times": ["breakfast", "lunch", "dinner"],
        "allergens": [],
    },
    {
        "name": "Bún riêu cua",
        "category": "Bún",
        "description": "Riêu cua, cà chua, rau thơm",
        "estimated_price": 45000,
        "reason": "Món nước đậm đà",
        "tags": ["popular"],
        "meal_times": ["lunch", "dinner"],
        "allergens": ["hải sản", "cua"],
    },
    {
        "name": "Bún mắm",
        "category": "Bún",
        "description": "Nước lèo mắm, topping đầy đủ",
        "estimated_price": 50000,
        "reason": "Vị miền Tây đặc trưng",
        "tags": ["local", "strong_flavor"],
        "meal_times": ["lunch", "dinner"],
        "allergens": ["hải sản", "tôm"],
    },
    {
        "name": "Gỏi cuốn tôm thịt",
        "category": "Gỏi",
        "description": "Cuốn tươi, chấm tương hoặc mắm nêm",
        "estimated_price": 40000,
        "reason": "Healthy, ít dầu",
        "tags": ["healthy", "light", "no_spicy"],
        "meal_times": ["lunch", "dinner", "snack"],
        "allergens": ["tôm", "hải sản"],
    },
    {
        "name": "Nem nướng Nha Trang",
        "category": "Khai vị",
        "description": "Nem nướng, bánh tráng, rau sống",
        "estimated_price": 70000,
        "reason": "Nhóm bạn, chia sẻ",
        "tags": ["friends"],
        "meal_times": ["lunch", "dinner"],
        "allergens": [],
    },
    {
        "name": "Lẩu thái chua cay",
        "category": "Lẩu",
        "description": "Nước lẩu chua cay, hải sản/rau",
        "estimated_price": 120000,
        "reason": "Nhóm 2–4 người, bữa tối",
        "tags": ["spicy", "friends", "variety"],
        "meal_times": ["dinner"],
        "allergens": ["hải sản", "tôm"],
    },
    {
        "name": "Lẩu bò nhúng dấm",
        "category": "Lẩu",
        "description": "Bò tươi, rau, bún kèm",
        "estimated_price": 150000,
        "reason": "No lâu, phù hợp tụ tập",
        "tags": ["friends", "family"],
        "meal_times": ["dinner"],
        "allergens": [],
    },
    {
        "name": "Bò kho bánh mì",
        "category": "Món nước",
        "description": "Bò kho nóng, ăn kèm bánh mì",
        "estimated_price": 55000,
        "reason": "Comfort food, trời mưa",
        "tags": ["comfort"],
        "meal_times": ["breakfast", "lunch", "dinner"],
        "allergens": ["gluten"],
    },
    {
        "name": "Canh chua cá",
        "category": "Canh",
        "description": "Canh chua miền Tây, cá/lóc",
        "estimated_price": 80000,
        "reason": "Cơm nhà, vị chua thanh",
        "tags": ["family", "no_spicy"],
        "meal_times": ["lunch", "dinner"],
        "allergens": ["hải sản"],
    },
    {
        "name": "Cá kho tộ",
        "category": "Món mặn",
        "description": "Cá kho đậm đà, ăn với cơm trắng",
        "estimated_price": 70000,
        "reason": "Cơm nhà truyền thống",
        "tags": ["family", "local"],
        "meal_times": ["lunch", "dinner"],
        "allergens": ["hải sản"],
    },
    {
        "name": "Đậu hũ sốt cà",
        "category": "Chay",
        "description": "Đậu hũ chiên hoặc luộc, sốt cà",
        "estimated_price": 40000,
        "reason": "Chay, healthy, giá mềm",
        "tags": ["vegetarian", "healthy", "no_spicy"],
        "meal_times": ["lunch", "dinner"],
        "allergens": ["đậu nành"],
    },
    {
        "name": "Phở chay",
        "category": "Chay",
        "description": "Phở nước rau củ, nấm",
        "estimated_price": 45000,
        "reason": "Chay, không thịt",
        "tags": ["vegetarian", "healthy"],
        "meal_times": ["breakfast", "lunch", "dinner"],
        "allergens": ["gluten"],
    },
    {
        "name": "Salad ức gà",
        "category": "Healthy",
        "description": "Rau xanh, ức gà, sốt nhẹ",
        "estimated_price": 65000,
        "reason": "Healthy, low carb",
        "tags": ["healthy", "light", "no_spicy"],
        "meal_times": ["lunch", "dinner"],
        "allergens": [],
    },
    {
        "name": "Poke bowl cá hồi",
        "category": "Healthy",
        "description": "Cơm/rau, cá hồi, trứng",
        "estimated_price": 95000,
        "reason": "Healthy, đổi gió",
        "tags": ["healthy", "variety"],
        "meal_times": ["lunch", "dinner"],
        "allergens": ["hải sản", "cá"],
    },
    {
        "name": "Bánh xèo miền Tây",
        "category": "Bánh",
        "description": "Xèo giòn, tôm thịt, rau sống",
        "estimated_price": 60000,
        "reason": "Đặc sản, chia nhóm",
        "tags": ["local", "friends"],
        "meal_times": ["lunch", "dinner"],
        "allergens": ["tôm", "hải sản"],
    },
    {
        "name": "Chè đậu xanh",
        "category": "Tráng miệng",
        "description": "Chè mát, ngọt vừa",
        "estimated_price": 20000,
        "reason": "Snack sau bữa",
        "tags": ["vegetarian", "light"],
        "meal_times": ["snack"],
        "allergens": [],
    },
    {
        "name": "Sinh tố bơ",
        "category": "Đồ uống",
        "description": "Sinh tố bơ đặc, no nhẹ",
        "estimated_price": 35000,
        "reason": "Xế trưa, không cần ngồi lâu",
        "tags": ["fast", "light"],
        "meal_times": ["snack", "breakfast"],
        "allergens": ["sữa", "lactose"],
    },
    {
        "name": "Cà phê sữa đá + bánh mì",
        "category": "Sáng",
        "description": "Combo sáng Sài Gòn",
        "estimated_price": 30000,
        "reason": "Nhanh, rẻ",
        "tags": ["fast", "popular"],
        "meal_times": ["breakfast", "snack"],
        "allergens": ["gluten", "lactose", "sữa"],
    },
    {
        "name": "Bún đậu mắm tôm",
        "category": "Bún",
        "description": "Đậu phụ, thịt, mắm tôm",
        "estimated_price": 55000,
        "reason": "Đặc trưng Hà Nội",
        "tags": ["local", "strong_flavor"],
        "meal_times": ["lunch", "dinner"],
        "allergens": ["đậu nành", "tôm", "hải sản"],
    },
    {
        "name": "Miến gà",
        "category": "Miến",
        "description": "Miến nước gà, nhẹ",
        "estimated_price": 45000,
        "reason": "Không gluten (miến), thanh",
        "tags": ["light", "healthy"],
        "meal_times": ["breakfast", "lunch", "dinner"],
        "allergens": [],
    },
    {
        "name": "Súp bí đỏ kem",
        "category": "Healthy",
        "description": "Súp ấm, ít cay",
        "estimated_price": 60000,
        "reason": "Trời mưa, healthy",
        "tags": ["healthy", "vegetarian", "no_spicy", "comfort"],
        "meal_times": ["lunch", "dinner"],
        "allergens": ["lactose", "sữa"],
    },
]

_MEAT_KEYWORDS = (
    "thịt",
    "bò",
    "gà",
    "heo",
    "lợn",
    "sườn",
    "bì",
    "chả",
    "tôm",
    "cua",
    "cá ",
    "cá,",
    "hải sản",
    "lòng",
    "nem nướng",
    "bún chả",
    "bánh xèo",
)

_ALLERGY_ALIASES: dict[str, list[str]] = {
    "hải sản": ["hải sản", "tôm", "cua", "cá"],
    "tôm": ["tôm", "hải sản"],
    "cua": ["cua", "hải sản"],
    "cá": ["cá", "hải sản"],
    "gluten": ["gluten"],
    "lactose": ["lactose", "sữa"],
    "sữa": ["sữa", "lactose"],
    "đậu nành": ["đậu nành"],
    "chay": [],  # handled via vegetarian filter
}


def _normalize_allergies(allergies: list[str]) -> set[str]:
    out: set[str] = set()
    for a in allergies:
        key = a.strip().lower()
        out.add(key)
        if key == "chay":
            out.add("chay")
        for alias in _ALLERGY_ALIASES.get(key, [key]):
            out.add(alias)
    return out


def _looks_like_meat_or_seafood(dish: dict[str, Any]) -> bool:
    if "vegetarian" in dish.get("tags", []):
        return False
    name = dish.get("name", "").lower()
    if "chay" in name or "đậu hũ" in name or "xôi" in name:
        return False
    return any(kw in name for kw in _MEAT_KEYWORDS)


def _dish_conflicts_allergy(dish: dict[str, Any], user_allergies: set[str]) -> bool:
    dish_allergens = {a.lower() for a in dish.get("allergens", [])}
    if dish_allergens.intersection(user_allergies):
        return True
    # Chay / vegetarian: loại món có thịt, hải sản (trừ món gắn tag vegetarian)
    if "chay" in user_allergies or "vegetarian" in user_allergies:
        if "vegetarian" in dish.get("tags", []):
            return False
        non_veg = dish_allergens - {"gluten", "đậu nành", "lactose", "sữa"}
        if non_veg:
            return True
        if _looks_like_meat_or_seafood(dish):
            return True
    return False


def _score_dish(
    dish: dict[str, Any],
    *,
    meal_time: str,
    budget: int,
    preferences: list[str],
    weather: str,
    purpose: str,
) -> float:
    score = 0.0
    if meal_time in dish.get("meal_times", []):
        score += 3.0
    price = int(dish.get("estimated_price", 0))
    if price <= budget:
        score += 2.0
    elif price <= budget * 1.15:
        score += 0.5
    else:
        score -= 2.0

    tags = set(dish.get("tags", []))
    prefs = set(preferences or [])
    score += len(tags.intersection(prefs)) * 1.2

    if weather in ("rain", "mưa", "rainy") and "comfort" in tags:
        score += 1.5
    if weather in ("hot", "nóng") and ("light" in tags or "healthy" in tags):
        score += 1.0

    if purpose == "family" and "family" in tags:
        score += 1.0
    if purpose in ("friends", "date") and ("friends" in tags or "variety" in tags):
        score += 0.8
    if purpose == "solo" and ("fast" in tags or "popular" in tags):
        score += 0.5

    if "no_spicy" in prefs and "spicy" in tags:
        score -= 3.0
    if "healthy" in prefs and "healthy" in tags:
        score += 1.5
    if "vegetarian" in prefs and "vegetarian" in tags:
        score += 2.0

    return score


def pick_fallback_foods(
    *,
    meal_time: str = "lunch",
    budget: int = 80000,
    preferences: list[str] | None = None,
    allergies: list[str] | None = None,
    weather: str = "normal",
    purpose: str = "solo",
    limit: int = 5,
) -> list[dict]:
    """Chọn tối đa `limit` món từ catalog tĩnh."""
    prefs = list(preferences or [])
    user_allergy_set = _normalize_allergies(list(allergies or []))

    candidates: list[tuple[float, dict[str, Any]]] = []
    for dish in _FALLBACK_CATALOG:
        if _dish_conflicts_allergy(dish, user_allergy_set):
            continue
        if int(dish.get("estimated_price", 0)) > budget * 1.25:
            continue
        s = _score_dish(
            dish,
            meal_time=meal_time,
            budget=budget,
            preferences=prefs,
            weather=weather,
            purpose=purpose,
        )
        if s > -1:
            candidates.append((s, dish))

    candidates.sort(key=lambda x: x[0], reverse=True)

    seen: set[str] = set()
    result: list[dict] = []
    for _, dish in candidates:
        name = dish["name"]
        if name in seen:
            continue
        seen.add(name)
        price = min(int(dish["estimated_price"]), budget)
        item = FoodSuggestion(
            name=name,
            category=dish["category"],
            description=dish["description"],
            estimated_price=price,
            reason=dish["reason"],
            tags=list(dish.get("tags", [])),
        ).model_dump()
        result.append(item)
        if len(result) >= limit:
            break

    if len(result) < 3:
        for dish in _FALLBACK_CATALOG:
            if dish["name"] in seen:
                continue
            if _dish_conflicts_allergy(dish, user_allergy_set):
                continue
            price = min(int(dish["estimated_price"]), budget)
            result.append(
                FoodSuggestion(
                    name=dish["name"],
                    category=dish["category"],
                    description=dish["description"],
                    estimated_price=price,
                    reason=dish["reason"],
                    tags=list(dish.get("tags", [])),
                ).model_dump()
            )
            seen.add(dish["name"])
            if len(result) >= limit:
                break

    return result
