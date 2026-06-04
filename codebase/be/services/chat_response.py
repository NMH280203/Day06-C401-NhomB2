"""Phản hồi thân thiện cho user — không đẩy raw error ra chat."""

from typing import Awaitable, Callable

StreamCallback = Callable[[str, dict], Awaitable[None]]

APOLOGY_REPLY = (
    "Xin lỗi bạn, mình đang gặp sự cố kỹ thuật tạm thời nên chưa trả lời đầy đủ được. "
    "Bạn thử gửi lại câu hỏi sau vài giây, hoặc rút gọn thành: ngân sách + số người + "
    "khu vực + sở thích (vd: *Trưa 2 người 150k healthy quận 1*). Mình sẽ gợi ý món và quán ngay khi có thể!"
)

APOLOGY_FOLLOW_UPS = [
    "Gợi ý món trưa 2 người 150k",
    "Quán healthy gần quận 1",
    "Món Việt ấm, không hải sản",
]


async def stream_text(text: str, stream_callback: StreamCallback, chunk: int = 28) -> None:
    for i in range(0, len(text), chunk):
        await stream_callback("text", {"delta": text[i : i + chunk]})


async def finish(
    stream_callback: StreamCallback,
    follow_ups: list[str] | None = None,
) -> None:
    await stream_callback(
        "done",
        {"follow_up_suggestions": follow_ups or APOLOGY_FOLLOW_UPS},
    )


async def respond_apology(
    stream_callback: StreamCallback,
    detail: str | None = None,
) -> None:
    await stream_callback("thinking", {"status": "đang xử lý sự cố..."})
    msg = APOLOGY_REPLY
    if detail:
        msg += f"\n\n_(Chi tiết kỹ thuật đã được ghi log.)_"
    await stream_text(msg, stream_callback)
    await finish(stream_callback)


async def respond_ask(
    stream_callback: StreamCallback,
    field: str,
    message: str,
    missing_fields: list[str] | None = None,
) -> None:
    """Hỏi thêm context nhưng vẫn kết thúc turn (có done)."""
    fields = missing_fields or [field]
    await stream_callback(
        "ask_context",
        {
            "ask": True,
            "field": field,
            "message": message,
            "missing_fields": fields,
        },
    )
    await stream_text(message, stream_callback)
    await finish(
        stream_callback,
        _follow_ups_for_field(field),
    )


def _follow_ups_for_field(field: str) -> list[str]:
    suggestions = {
        "location": [
            "Quận 1, TP.HCM",
            "Hoàn Kiếm, Hà Nội",
            "Dùng vị trí GPS của tôi",
        ],
        "budget": [
            "Khoảng 50k/người",
            "Khoảng 100k/người",
            "Dưới 150k cho 2 người",
        ],
        "meal_time": [
            "Bữa trưa hôm nay",
            "Bữa tối 2 người",
            "Ăn vặt / cafe chiều",
        ],
        "people": [
            "1 người",
            "2 người",
            "Nhóm 4 người",
        ],
        "dietary": [
            "Ăn chay",
            "Không hải sản",
            "Healthy, ít dầu",
        ],
    }
    return suggestions.get(field, APOLOGY_FOLLOW_UPS)
