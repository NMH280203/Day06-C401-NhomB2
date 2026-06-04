"""Suy luận vị trí từ câu user — ưu tiên cao hơn GPS/context thiết bị."""

from __future__ import annotations

import re

from models.schemas import Location, UserContext

# lat, lng gần đúng trung tâm quận/khu (key dài match trước)
_AREA_COORDS: dict[str, tuple[float, float, str]] = {
    "phú mỹ hưng": (10.7287, 106.7228, "Phú Mỹ Hưng, Quận 7, TP.HCM"),
    "tân sơn nhất": (10.8188, 106.6520, "Sân bay Tân Sơn Nhất, TP.HCM"),
    "bình thạnh": (10.8106, 106.7091, "Bình Thạnh, TP.HCM"),
    "thảo điền": (10.8028, 106.7407, "Thảo Điền, Quận 2, TP.HCM"),
    "hồ gươm": (21.0285, 105.8520, "Hồ Gươm, Hoàn Kiếm, Hà Nội"),
    "hoàn kiếm": (21.0285, 105.8542, "Hoàn Kiếm, Hà Nội"),
    "tây hồ": (21.0683, 105.8195, "Tây Hồ, Hà Nội"),
    "đống đa": (21.0134, 105.8270, "Đống Đa, Hà Nội"),
    "cầu giấy": (21.0333, 105.7940, "Cầu Giấy, Hà Nội"),
    "quận 1": (10.7769, 106.7009, "Quận 1, TP.HCM"),
    "quận 2": (10.7872, 106.7498, "Quận 2, TP.HCM"),
    "quận 3": (10.7843, 106.6846, "Quận 3, TP.HCM"),
    "quận 4": (10.7578, 106.7019, "Quận 4, TP.HCM"),
    "quận 5": (10.7540, 106.6634, "Quận 5, TP.HCM"),
    "quận 6": (10.7465, 106.6352, "Quận 6, TP.HCM"),
    "quận 7": (10.7340, 106.7217, "Quận 7, TP.HCM"),
    "quận 8": (10.7241, 106.6286, "Quận 8, TP.HCM"),
    "quận 10": (10.7720, 106.6663, "Quận 10, TP.HCM"),
    "quận 11": (10.7629, 106.6501, "Quận 11, TP.HCM"),
    "quận 12": (10.8671, 106.6413, "Quận 12, TP.HCM"),
    "q1": (10.7769, 106.7009, "Quận 1, TP.HCM"),
    "q2": (10.7872, 106.7498, "Quận 2, TP.HCM"),
    "q3": (10.7843, 106.6846, "Quận 3, TP.HCM"),
    "q7": (10.7340, 106.7217, "Quận 7, TP.HCM"),
    "sài gòn": (10.7769, 106.7009, "Trung tâm TP.HCM"),
    "tp.hcm": (10.7769, 106.7009, "TP.HCM"),
    "tp hcm": (10.7769, 106.7009, "TP.HCM"),
    "hồ chí minh": (10.7769, 106.7009, "TP.HCM"),
    "hà nội": (21.0285, 105.8542, "Hà Nội"),
    "hanoi": (21.0285, 105.8542, "Hanoi"),
    "đà nẵng": (16.0544, 108.2022, "Đà Nẵng"),
    "nha trang": (12.2388, 109.1967, "Nha Trang"),
}

_SORTED_AREA_KEYS = sorted(_AREA_COORDS.keys(), key=len, reverse=True)

# "ở quận 7", "gần Bình Thạnh", "tại Hà Nội"
_AREA_PATTERNS = [
    re.compile(r"(?:ở|tại|gần|khu vực|quanh)\s+([a-z0-9\s.]+?)(?:,|\.|$|\s+(?:tp|thành phố))", re.I),
    re.compile(r"(quận\s*\d+|q\d+)\b", re.I),
]


def extract_location_from_text(text: str) -> Location | None:
    """Trích vị trí từ câu user (quận, thành phố, landmark)."""
    if not text or not text.strip():
        return None
    t = text.lower().strip()

    for key in _SORTED_AREA_KEYS:
        if key in t:
            lat, lng, address = _AREA_COORDS[key]
            return Location(lat=lat, lng=lng, address=address)

    for pat in _AREA_PATTERNS:
        m = pat.search(t)
        if not m:
            continue
        fragment = m.group(1).strip().lower() if m.lastindex and m.lastindex >= 1 else m.group(0).lower()
        for key in _SORTED_AREA_KEYS:
            if key in fragment or fragment in key:
                lat, lng, address = _AREA_COORDS[key]
                return Location(lat=lat, lng=lng, address=address)

    return None


def apply_location_priority(context: UserContext, text: str) -> tuple[UserContext, str | None]:
    """
    Ưu tiên vị trí user gõ trong tin nhắn > GPS/context FE gửi lên.
    Trả về (context đã cập nhật, nguồn vị trí: user_message | device_gps | None).
    """
    from_text = extract_location_from_text(text)
    if from_text:
        data = context.model_dump()
        data["location"] = from_text.model_dump()
        data["location_source"] = "user_message"
        return UserContext.model_validate(data), "user_message"

    if context.location:
        data = context.model_dump()
        if not data.get("location_source"):
            data["location_source"] = "device_gps"
        return UserContext.model_validate(data), "device_gps"

    return context, None


def enrich_context_from_text(context: UserContext, text: str) -> UserContext:
    """Giữ tương thích code cũ — chỉ gán location nếu chưa có (deprecated)."""
    ctx, _ = apply_location_priority(context, text)
    return ctx
