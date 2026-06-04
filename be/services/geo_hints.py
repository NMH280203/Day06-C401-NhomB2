"""Suy luận vị trí gần đúng từ tên quận/khu trong câu user (TP.HCM / Hà Nội)."""

import re

from models.schemas import Location, UserContext

# lat, lng gần đúng trung tâm quận/khu
_AREA_COORDS: dict[str, tuple[float, float, str]] = {
    "quận 1": (10.7769, 106.7009, "Quận 1, TP.HCM"),
    "q1": (10.7769, 106.7009, "Quận 1, TP.HCM"),
    "quận 2": (10.7872, 106.7498, "Quận 2, TP.HCM"),
    "thảo điền": (10.8028, 106.7407, "Thảo Điền, Quận 2, TP.HCM"),
    "quận 3": (10.7843, 106.6846, "Quận 3, TP.HCM"),
    "quận 4": (10.7578, 106.7019, "Quận 4, TP.HCM"),
    "quận 7": (10.7340, 106.7217, "Quận 7, TP.HCM"),
    "phú mỹ hưng": (10.7287, 106.7228, "Phú Mỹ Hưng, Quận 7, TP.HCM"),
    "quận 10": (10.7720, 106.6663, "Quận 10, TP.HCM"),
    "bình thạnh": (10.8106, 106.7091, "Bình Thạnh, TP.HCM"),
    "tân sơn nhất": (10.8188, 106.6520, "Sân bay Tân Sơn Nhất, TP.HCM"),
    "sài gòn": (10.7769, 106.7009, "Trung tâm TP.HCM"),
    "tp.hcm": (10.7769, 106.7009, "TP.HCM"),
    "hồ chí minh": (10.7769, 106.7009, "TP.HCM"),
    "hoàn kiếm": (21.0285, 105.8542, "Hoàn Kiếm, Hà Nội"),
    "tây hồ": (21.0683, 105.8195, "Tây Hồ, Hà Nội"),
    "đống đa": (21.0134, 105.8270, "Đống Đa, Hà Nội"),
    "hà nội": (21.0285, 105.8542, "Hà Nội"),
    "hanoi": (21.0285, 105.8542, "Hanoi"),
}


def enrich_context_from_text(context: UserContext, text: str) -> UserContext:
    if context.location:
        return context
    t = text.lower()
    for key, (lat, lng, address) in _AREA_COORDS.items():
        if key in t:
            data = context.model_dump()
            data["location"] = Location(lat=lat, lng=lng, address=address).model_dump()
            return UserContext.model_validate(data)
    return context
