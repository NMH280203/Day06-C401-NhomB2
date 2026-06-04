"""Phát hiện thiếu context và hỏi lại user trước khi gợi ý."""

from __future__ import annotations

import re
from dataclasses import dataclass

from models.schemas import UserContext
from services.geo_hints import apply_location_priority, extract_location_from_text

# Từ khóa cần quán / vị trí
_RESTAURANT_HINTS = (
    "quán",
    "nhà hàng",
    "restaurant",
    "gần",
    "gần đây",
    "nearby",
    "near me",
    "địa chỉ",
    "cafe",
    "cà phê",
    "trà sữa",
    "view",
    "ở đâu",
    "chỗ nào",
    "tìm quán",
)

_VAGUE_PHRASES = (
    "ăn gì",
    "uống gì",
    "gì ngon",
    "không biết ăn",
    "không biết uống",
    "gợi ý",
    "recommend",
    "tối nay",
    "trưa nay",
    "sáng nay",
)

_SPECIFIC_DISH = re.compile(
    r"\b(phở|bún|bánh|com|cơm|lẩu|nướng|pizza|sushi|burger|salad|chay|"
    r"cafe|cà phê|trà sữa|bánh mì|hủ tiếu|mì|gà|vịt|hải sản)\b",
    re.I,
)


@dataclass(frozen=True)
class Clarification:
    field: str
    message: str
    missing_fields: tuple[str, ...]


def _parse_budget(text: str, ctx: UserContext) -> int | None:
    if ctx.budget:
        return ctx.budget
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*triệu", text, re.I)
    if m:
        return int(float(m.group(1).replace(",", ".")) * 1_000_000)
    m = re.search(r"(\d+)\s*k\b", text, re.I)
    if m:
        return int(m.group(1)) * 1000
    m = re.search(r"(\d{2,3})\s*(?:k|nghìn|ngàn)", text, re.I)
    if m:
        return int(m.group(1)) * 1000
    m = re.search(r"(?:dưới|tối đa|khoảng|~)\s*(\d{2,4})\s*k", text, re.I)
    if m:
        return int(m.group(1)) * 1000
    m = re.search(r"\b(\d{4,7})\b", text)
    if m:
        v = int(m.group(1))
        return v if v < 500_000 else min(v, 500_000)
    return None


def _parse_meal_time(text: str, ctx: UserContext) -> str | None:
    if ctx.meal_time:
        return ctx.meal_time
    t = text.lower()
    if any(w in t for w in ("sáng", "breakfast")):
        return "breakfast"
    if any(w in t for w in ("trưa", "lunch")):
        return "lunch"
    if any(w in t for w in ("tối", "chiều", "dinner")):
        return "dinner"
    if any(w in t for w in ("xế", "snack", "vặt", "uống")):
        return "snack"
    return None


def _parse_people(text: str, ctx: UserContext) -> int | None:
    if ctx.people:
        return ctx.people
    m = re.search(r"(\d+)\s*người", text, re.I)
    if m:
        return int(m.group(1))
    m = re.search(r"(\d+)\s*ng\b", text, re.I)
    if m:
        return int(m.group(1))
    if any(w in text.lower() for w in ("một mình", "1 mình", "solo", "alone")):
        return 1
    if "đôi" in text.lower() or "2 người" in text.lower():
        return 2
    return None


def _parse_preferences(text: str, ctx: UserContext) -> list[str]:
    prefs = list(ctx.preferences or [])
    keywords = {
        "healthy": "healthy",
        "ăn nhẹ": "light",
        "nhẹ": "light",
        "không cay": "no_spicy",
        "không ớt": "no_spicy",
        "chay": "vegetarian",
        "đổi gió": "variety",
        "nhanh": "fast",
        "cay": "cay",
        "cay nồng": "cay",
        "món cay": "cay",
        "ngọt": "ngot",
        "ngot": "ngot",
        "chua": "chua",
        "chua ngọt": "chua",
        "mặn": "man",
        "đậm đà": "beo",
        "béo": "beo",
        "thanh": "nhat",
        "đắng": "dang",
    }
    t = text.lower()
    for k, v in keywords.items():
        if k in t and v not in prefs:
            prefs.append(v)
    return prefs


def _parse_allergies(text: str, ctx: UserContext) -> list[str]:
    allergies = list(ctx.allergies or [])
    for term in ("chay", "hải sản", "gluten", "lactose", "đậu nành", "tôm", "cua", "đỗ"):
        if term in text.lower() and term not in allergies:
            allergies.append(term)
    return allergies


def enrich_context_from_text(context: UserContext, text: str) -> UserContext:
    """Trích budget, bữa ăn, số người, sở thích từ câu user."""
    if not text or not text.strip():
        return context

    data = context.model_dump()
    budget = _parse_budget(text, context)
    if budget is not None:
        data["budget"] = budget
    meal = _parse_meal_time(text, context)
    if meal is not None:
        data["meal_time"] = meal
    people = _parse_people(text, context)
    if people is not None:
        data["people"] = people
    prefs = _parse_preferences(text, context)
    if prefs:
        data["preferences"] = prefs
    allergies = _parse_allergies(text, context)
    if allergies:
        data["allergies"] = allergies

    merged = UserContext.model_validate(data)
    merged, _ = apply_location_priority(merged, text)
    return merged


def wants_restaurant_search(text: str) -> bool:
    t = text.lower()
    return any(h in t for h in _RESTAURANT_HINTS)


def is_vague_request(text: str, ctx: UserContext) -> bool:
    t = text.lower().strip()
    if len(t) > 55 and _SPECIFIC_DISH.search(t):
        return False
    if any(p in t for p in _VAGUE_PHRASES):
        return not ctx.budget or not ctx.meal_time
    if len(t) < 10 and not ctx.budget and not _SPECIFIC_DISH.search(t):
        return True
    return False


def list_missing_fields(context: UserContext, text: str) -> list[str]:
    """Danh sách field còn thiếu để gợi ý tốt hơn."""
    missing: list[str] = []
    t = text.lower()

    need_place = wants_restaurant_search(t) or "quán" in t or "cafe" in t
    if need_place and not context.location and not extract_location_from_text(text):
        missing.append("location")

    if is_vague_request(text, context) and not context.budget:
        missing.append("budget")

    if is_vague_request(text, context) and not context.meal_time:
        missing.append("meal_time")

    if context.budget and context.budget > 150_000 and not context.people:
        if any(w in t for w in ("mình", "solo", "nhóm", "team", "gia đình", "hẹn hò")):
            pass
        elif not re.search(r"\d+\s*người", t, re.I):
            missing.append("people")

    if any(w in t for w in ("chay", "healthy", "không cay", "dị ứng")) and not (
        context.preferences or context.allergies
    ):
        missing.append("dietary")

    return missing


_QUESTIONS: dict[str, str] = {
    "location": (
        "Bạn đang ở **khu vực nào** (quận/thành phố hoặc cho phép GPS) "
        "để mình tìm quán gần bạn nhé?"
    ),
    "budget": (
        "Bạn muốn ăn với **ngân sách khoảng bao nhiêu** một người? "
        "(vd: 50k, 80k, 150k)"
    ),
    "meal_time": (
        "Bạn định ăn **bữa nào** — sáng, trưa, tối hay ăn vặt/uống?"
    ),
    "people": (
        "Bạn đi **mấy người** ạ? (vd: 1 người, 2 người, nhóm 4)"
    ),
    "dietary": (
        "Bạn có **dị ứng, ăn chay** hoặc sở thích đặc biệt nào cần tránh không?"
    ),
}

_PRIORITY = ("location", "budget", "meal_time", "people", "dietary")


def build_clarification(
    missing: list[str],
    *,
    prefer_field: str | None = None,
) -> Clarification | None:
    if not missing:
        return None
    ordered = [f for f in _PRIORITY if f in missing]
    if not ordered:
        return None
    field = prefer_field if prefer_field in ordered else ordered[0]
    extra = [f for f in ordered if f != field]
    msg = _QUESTIONS[field]
    if extra:
        labels = {
            "location": "vị trí",
            "budget": "ngân sách",
            "meal_time": "bữa ăn",
            "people": "số người",
            "dietary": "dị ứng/sở thích",
        }
        also = ", ".join(labels.get(f, f) for f in extra[:2])
        msg += f"\n\n_(Sau đó mình sẽ hỏi thêm về {also} nếu cần.)_"
    return Clarification(field=field, message=msg, missing_fields=tuple(ordered))


def needs_clarification(context: UserContext, text: str) -> Clarification | None:
    ctx = enrich_context_from_text(context, text)
    missing = list_missing_fields(ctx, text)
    return build_clarification(missing)
