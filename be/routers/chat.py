import asyncio
import json
import time

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from agents.orchestrator import run as orchestrator_run
from core.logging_config import (
    clear_request_id,
    format_context,
    get_logger,
    log_event,
    log_exception,
    log_location,
    set_request_id,
)
from models.schemas import ChatRequest
from services.chat_response import respond_apology

router = APIRouter()
logger = get_logger("chat")


def _format_sse(event: str, data: dict) -> str:
    payload = json.dumps(data, ensure_ascii=False)
    return f"event: {event}\ndata: {payload}\n\n"


def _user_preview(request: ChatRequest) -> str:
    return next(
        (m.content[:160] for m in reversed(request.messages) if m.role == "user" and m.content),
        "",
    )


def _context_summary(request: ChatRequest) -> str:
    ctx = request.context
    parts: list[str] = []
    if ctx.location:
        parts.append(f"loc={ctx.location.lat:.6f},{ctx.location.lng:.6f}")
    if ctx.budget:
        parts.append(f"budget={ctx.budget}")
    if ctx.meal_time:
        parts.append(f"meal={ctx.meal_time}")
    if ctx.preferences:
        parts.append(f"prefs={','.join(ctx.preferences[:3])}")
    if ctx.allergies:
        parts.append(f"allergies={','.join(ctx.allergies[:3])}")
    return " | ".join(parts) if parts else "no_context"


@router.post("/chat")
async def chat(request: ChatRequest) -> StreamingResponse:
    request_id = set_request_id()
    started = time.perf_counter()
    user_preview = _user_preview(request)
    ctx_summary = _context_summary(request)

    log_event(
        logger,
        "CHAT start",
        messages=len(request.messages),
        user=user_preview,
        context=ctx_summary,
    )
    if request.context.location:
        log_location(
            logger,
            "CHAT user_location",
            request.context.location.lat,
            request.context.location.lng,
        )

    queue: asyncio.Queue[tuple[str, dict] | None] = asyncio.Queue()
    event_counts: dict[str, int] = {}

    async def stream_callback(event: str, data: dict) -> None:
        event_counts[event] = event_counts.get(event, 0) + 1
        if event == "restaurant_results":
            count = len(data.get("restaurants", []))
            log_event(logger, "SSE restaurant_results", count=count)
        elif event == "food_results":
            count = len(data.get("foods", []))
            log_event(logger, "SSE food_results", count=count, names=",".join(data.get("food_names", [])[:5]))
        elif event in ("ask_context", "error"):
            log_event(
                logger,
                f"SSE {event}",
                field=data.get("field"),
                detail=(data.get("message") or "")[:120],
            )
        await queue.put((event, data))

    async def event_generator():
        task = asyncio.create_task(
            orchestrator_run(request.messages, request.context, stream_callback)
        )
        try:
            while True:
                if task.done() and queue.empty():
                    break
                try:
                    item = await asyncio.wait_for(queue.get(), timeout=0.1)
                except asyncio.TimeoutError:
                    continue
                if item is None:
                    break
                event, data = item
                yield _format_sse(event, data)
            await task
            elapsed_ms = int((time.perf_counter() - started) * 1000)
            log_event(
                logger,
                "CHAT done",
                duration_ms=elapsed_ms,
                events=format_context(**event_counts),
            )
        except Exception as exc:
            log_exception(logger, "chat stream failed", exc, user_message=user_preview)
            apology_queue: list[tuple[str, dict]] = []

            async def apology_cb(event: str, data: dict) -> None:
                apology_queue.append((event, data))

            await respond_apology(apology_cb)
            for event, data in apology_queue:
                yield _format_sse(event, data)
        finally:
            if not task.done():
                task.cancel()
            clear_request_id()

    return StreamingResponse(event_generator(), media_type="text/event-stream")
