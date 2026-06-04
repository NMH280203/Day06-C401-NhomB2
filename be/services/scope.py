"""Phạm vi hội thoại: ăn uống, quán ăn, cafe, trải nghiệm F&B — mặc định từ chối off-topic."""

from __future__ import annotations

import re

OUT_OF_SCOPE_REPLY = (
    "Mình là trợ lý **gợi ý món ăn & địa điểm ăn uống** — chỉ hỗ trợ các câu liên quan:\n"
    "• Món ăn, quán ăn, nhà hàng, buffet, lẩu, street food\n"
    "• **Cafe, cà phê, trà sữa**, quán nước, bánh ngọt (đi uống/ăn nhẹ)\n"
    "• Ngân sách, khẩu vị, vị trí, chay, healthy, hẹn hò qua bữa ăn…\n\n"
    "Câu hỏi của bạn **không thuộc phạm vi ăn uống** nên mình không trả lời được.\n\n"
    "Thử hỏi lại, ví dụ:\n"
    "• *\"Quán cafe view đẹp gần Quận 1\"*\n"
    "• *\"Trưa một mình 50k, gợi ý món và quán gần đây\"*"
)

OUT_OF_SCOPE_FOLLOW_UPS = [
    "Quán cafe làm việc yên tĩnh gần tôi",
    "Gợi ý món trưa khoảng 50k",
    "Trà sữa ngon quận 1",
]

# Rõ ràng KHÔNG thuộc phạm vi F&B
_OFF_TOPIC_PATTERNS = [
    r"^\s*(viết|debug|fix|code|lập trình)\s",
    r"\b(hướng dẫn|dạy|tutorial)\s+(viết\s+)?(code|python|javascript|react)\b",
    r"\b(bitcoin|crypto|chứng khoán|forex|coin)\b",
    r"\b(bài tập toán|giải phương trình|đạo hàm|tích phân)\b",
    r"\b(chính trị|bầu cử|đảng phái|quốc hội)\b",
    r"\b(đặt vé|vé máy bay|booking khách sạn|khách sạn|resort)\b(?!.*(ăn|quán|cafe|café|breakfast|buffet))",
    r"\b(thời tiết|weather forecast|dự báo thời tiết)\b(?!.*(ăn|uống|quán|cafe|món))",
    r"\b(tin tức|bóng đá|thể thao|tỷ số)\b(?!.*(ăn|quán|bar))",
    r"\b(học tiếng anh|dịch văn bản|viết email|cv|xin việc)\b",
    r"\b(mua điện thoại|iphone|laptop|xe máy)\b",
    r"^\s*(hello|hi|hey)\s*$",
    r"^\s*(xin chào|chào bạn|chào)\s*$",
]

# Trong phạm vi: ăn, uống, quán, cafe, trải nghiệm F&B
_IN_SCOPE_PATTERNS = [
    r"\b(ăn|đồ ăn|món|quán|nhà hàng|restaurant|food|menu|buffet|lẩu|nướng|street food)\b",
    r"\b(cafe|café|cà phê|coffee|espresso|latte|capuccino|cappuccino)\b",
    r"\b(trà sữa|bubble tea|boba|trà chanh|sinh tố|smoothie|juice)\b",
    r"\b(quán nước|tiệm trà|tea house|high tea|brunch)\b",
    r"\b(bar|pub|beer garden|bia|nhậu|cocktail)\b",
    r"\b(bánh ngọt|bánh kem|dessert|tiệm bánh|bakery|patisserie)\b",
    r"\b(phở|bún|cơm|bánh|chay|healthy|keto|low-?carb|dị ứng|allerg|vegan|vegetarian)\b",
    r"\b(gợi ý|suggest|recommend)\b.*\b(món|quán|food|eat|drink|cafe|uống|ăn)\b",
    r"\b(gợi ý|tìm|chỉ|recommend)\b.*\b(cafe|quán)\b",
    r"\b(spicy|comfort food|fine dining|fusion|việt nam|vietnamese)\b",
    r"\b(trưa|sáng|tối|chiều|bữa|lunch|dinner|breakfast|snack|xế)\b",
    r"\b(\d+\s*k|\d+\s*nghìn|triệu|million|ngân sách|budget|dưới\s+\d+)\b",
    r"\b(quận|district|hanoi|hà nội|sài gòn|ho chi minh|hoàn kiếm|gần đây|gần tôi)\b",
    r"\b(thèm|ngon|no|đói|kiêng|ăn kiêng|dùng bữa|uống gì|ăn gì)\b",
    r"\b(hải sản|gluten|lactose|cay|không cay)\b",
    r"\b(view đẹp|yên tĩnh|làm việc|hẹn hò|date|work friendly)\b.*\b(cafe|quán|cà phê)\b",
    r"\b(cafe|quán|cà phê)\b.*\b(view|yên tĩnh|làm việc|hẹn hò|wifi)\b",
    r"\b(sân bay|transit|airport).*(ăn|món|quán|cafe|food)\b",
    r"\b(ăn|món|quán|cafe|food).*(sân bay|transit|airport)\b",
]


def _normalize(text: str) -> str:
    return text.lower().strip()


def is_food_related(text: str) -> bool:
    """
    True = trong phạm vi ăn uống / F&B (kể cả cafe, trà sữa).
    False = ngoài phạm vi → gọi out_of_scope fallback.
    """
    t = _normalize(text)
    if not t:
        return False

    for pat in _OFF_TOPIC_PATTERNS:
        if re.search(pat, t, re.IGNORECASE):
            return False

    for pat in _IN_SCOPE_PATTERNS:
        if re.search(pat, t, re.IGNORECASE):
            return True

    # Câu ngắn mang tính chào / không rõ — không đoán là ăn uống
    if len(t) < 12:
        return False

    return False
