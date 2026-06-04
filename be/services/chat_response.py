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
) -> None:
    """Hỏi thêm context nhưng vẫn kết thúc turn (có done)."""
    await stream_callback("ask_context", {"ask": True, "field": field, "message": message})
    await stream_text(message, stream_callback)
    await finish(stream_callback)
