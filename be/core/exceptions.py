"""Xử lý exception thống nhất — log file, phản hồi user thân thiện."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from core.logging_config import exception_summary, get_logger, log_exception
from services.chat_response import respond_apology

T = TypeVar("T")
StreamCallback = Callable[[str, dict], Awaitable[None]]

logger = get_logger("exceptions")


async def handle_chat_failure(
    stream_callback: StreamCallback,
    exc: BaseException,
    *,
    where: str,
    user_message: str | None = None,
) -> None:
    """Log chi tiết, trả lời xin lỗi qua SSE (không leak lỗi kỹ thuật)."""
    log_exception(
        logger,
        f"Chat failure at {where}",
        exc,
        user_message=(user_message or "")[:120],
    )
    await respond_apology(stream_callback)


async def run_safe(
    fn: Callable[[], Awaitable[T]],
    *,
    where: str,
    fallback: T,
    on_error: Callable[[BaseException], Awaitable[None]] | None = None,
) -> T:
    try:
        return await fn()
    except Exception as exc:
        log_exception(logger, f"Error in {where}", exc)
        if on_error:
            await on_error(exc)
        return fallback
