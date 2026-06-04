import asyncio
import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from agents.orchestrator import run as orchestrator_run
from core.logging_config import get_logger, log_exception
from models.schemas import ChatRequest
from services.chat_response import respond_apology

router = APIRouter()
logger = get_logger("chat")


def _format_sse(event: str, data: dict) -> str:
    payload = json.dumps(data, ensure_ascii=False)
    return f"event: {event}\ndata: {payload}\n\n"


@router.post("/chat")
async def chat(request: ChatRequest) -> StreamingResponse:
    queue: asyncio.Queue[tuple[str, dict] | None] = asyncio.Queue()
    user_preview = next(
        (m.content[:120] for m in reversed(request.messages) if m.role == "user" and m.content),
        "",
    )

    async def stream_callback(event: str, data: dict) -> None:
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

    logger.info("POST /api/chat | messages=%d", len(request.messages))
    return StreamingResponse(event_generator(), media_type="text/event-stream")
