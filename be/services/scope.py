"""Phạm vi hội thoại: chỉ đồ ăn / nhà hàng / gợi ý bữa ăn."""

import re

OUT_OF_SCOPE_REPLY = (
    "Mình là trợ lý **gợi ý món ăn và nhà hàng** — chỉ hỗ trợ các câu hỏi liên quan đến ăn uống "
    "(gợi ý món, quán, ngân sách, khẩu vị, địa điểm ăn, bữa sáng/trưa/tối, chay, healthy…).\n\n"
    "Câu hỏi của bạn **không thuộc phạm vi** này nên mình không trả lời được. "
    "Bạn thử hỏi lại theo kiểu: *\"Trưa một mình 50k không cay, gợi ý món và quán gần đây\"* nhé!"
)

OUT_OF_SCOPE_FOLLOW_UPS = [
    "Gợi ý món trưa khoảng 50k",
    "Tìm quán healthy gần tôi",
    "Ăn chay buổi tối có gì?",
]

# Chỉ chặn khi RÕ ràng không phải đồ ăn
_OFF_TOPIC_STRICT = [
    r"^\s*(viết|debug|fix)\s+(code|python|javascript)",
    r"\b(hướng dẫn|dạy|tutorial)\s+(viết\s+)?(code|python|react)\b",
    r"\b(bitcoin|crypto|chứng khoán|forex)\b(?!.*(ăn|food))",
    r"\b(bài tập toán|giải phương trình|đạo hàm)\b",
    r"\b(chính trị|bầu cử|đảng phái)\b",
]

_FOOD_SIGNALS = [
    r"\b(ăn|đồ ăn|món|quán|nhà hàng|restaurant|food|menu|buffet|lẩu|nướng)\b",
    r"\b(phở|bún|cơm|bánh|chay|healthy|keto|low-?carb|dị ứng|allerg)",
    r"\b(gợi ý|suggest|recommend|option)\b.*\b(món|quán|food|eat)\b",
    r"\b(gợi ý|suggest)\b",
    r"\b(spicy|comfort food|fine dining|fusion|việt nam|vietnamese)\b",
    r"\b(trưa|sáng|tối|chiều|bữa|lunch|dinner|breakfast)\b",
    r"\b(\d+\s*k|\d+\s*nghìn|triệu|million|ngân sách|budget|dưới\s+\d+)\b",
    r"\b(quận|district|hanoi|hà nội|sài gòn|ho chi minh|hoan kiem)\b",
    r"\b(thèm|ngon|no|đói|kiêng|ăn kiêng|dùng bữa)\b",
    r"\b(hải sản|gluten|lactose|cay|không cay)\b",
    r"\b(sân bay|transit).*(ăn|món|quán)\b",
]


def _normalize(text: str) -> str:
    return text.lower().strip()


def is_food_related(text: str) -> bool:
    """Ưu tiên cho phép câu dài về ăn uống; chỉ chặn off-topic rõ ràng."""
    t = _normalize(text)
    if not t:
        return False

    for pat in _FOOD_SIGNALS:
        if re.search(pat, t, re.IGNORECASE):
            return True

    for pat in _OFF_TOPIC_STRICT:
        if re.search(pat, t, re.IGNORECASE):
            return False

    # Câu dài (>40 ký tự) có khả năng là yêu cầu phức tạp về ăn — cho qua
    if len(t) > 40:
        return True

    if len(t) < 15:
        return True

    return False
