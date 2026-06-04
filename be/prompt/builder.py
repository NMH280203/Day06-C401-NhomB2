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


def build_system_prompt(context: UserContext) -> str:
    parts = [BASE_PROMPT.strip(), "\n\n## Ngữ cảnh hiện tại"]
    meal = context.meal_time or _infer_meal_time()
    parts.append(f"- Thời điểm bữa ăn (suy luận): {meal}")

    if context.location:
        addr = context.location.address or f"{context.location.lat}, {context.location.lng}"
        parts.append(f"- Vị trí: {addr}")
    else:
        parts.append("- Vị trí: chưa có (cần hỏi nếu gợi ý quán gần)")

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
