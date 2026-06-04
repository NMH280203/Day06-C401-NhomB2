from datetime import datetime

from models.schemas import UserContext
from prompt.system_prompt import BASE_PROMPT


def _infer_meal_time() -> str:
    hour = datetime.now().hour
    if hour < 5:
        return "snack"
    if hour < 11:
        return "breakfast"
    if hour < 17:
        return "lunch"
    if hour < 22:
        return "dinner"
    return "snack"


def build_system_prompt(
    context: UserContext,
    *,
    location_source: str | None = None,
    user_location_note: str | None = None,
) -> str:
    location_source = location_source or context.location_source
    parts = [BASE_PROMPT.strip(), "\n\n## Ngữ cảnh hiện tại"]
    meal = context.meal_time or _infer_meal_time()
    parts.append(f"- Thời điểm bữa ăn (suy luận): {meal}")

    if context.location:
        addr = context.location.address or f"{context.location.lat}, {context.location.lng}"
        lat, lng = context.location.lat, context.location.lng
        if location_source == "user_message":
            parts.append(
                f"- **Vị trí ưu tiên (user nhập trong chat):** {addr} "
                f"(lat={lat:.5f}, lng={lng:.5f})"
            )
            parts.append(
                "  → BẮT BUỘC tìm quán và gợi ý theo khu vực này; "
                "không dùng GPS/thành phố khác nếu user đã nêu quận/địa danh."
            )
        else:
            parts.append(
                f"- Vị trí (GPS/thiết bị hoặc context): {addr} "
                f"(lat={lat:.5f}, lng={lng:.5f})"
            )
        if user_location_note:
            parts.append(f"- Ghi chú địa điểm từ user: {user_location_note}")
    else:
        parts.append("- Vị trí: chưa có — hỏi quận/khu vực nếu cần gợi ý quán gần")

    if context.budget is not None:
        parts.append(f"- Ngân sách: {context.budget:,} VND")
    if context.people is not None:
        parts.append(f"- Số người: {context.people}")
    if context.purpose:
        parts.append(f"- Mục đích: {context.purpose}")
    if context.preferences:
        parts.append(f"- Sở thích: {', '.join(context.preferences)}")
    if context.allergies:
        parts.append(f"- Dị ứng / kiêng: {', '.join(context.allergies)}")

    return "\n".join(parts)
