from typing import Awaitable, Callable

from services.chat_response import finish, stream_text
from services.scope import OUT_OF_SCOPE_FOLLOW_UPS, OUT_OF_SCOPE_REPLY

StreamCallback = Callable[[str, dict], Awaitable[None]]


async def respond(stream_callback: StreamCallback) -> None:
    await stream_callback(
        "thinking",
        {"status": "out_of_scope — từ chối câu hỏi ngoài đồ ăn"},
    )
    await stream_text(OUT_OF_SCOPE_REPLY, stream_callback)
    await finish(stream_callback, OUT_OF_SCOPE_FOLLOW_UPS)
