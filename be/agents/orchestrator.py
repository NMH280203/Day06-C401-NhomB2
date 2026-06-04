import json

from typing import Awaitable, Callable

from agents import food_agent, restaurant_agent, rule_fallback
from core.logging_config import exception_summary, get_logger, log_event, log_exception, log_restaurants
from models.schemas import Message, UserContext
from prompt.builder import build_system_prompt
from services import llm
from services.chat_response import finish, respond_apology, respond_ask, stream_text
from services.geo_hints import apply_location_priority, extract_location_from_text
from services.llm_errors import is_llm_unavailable
from services.llm_messages import response_to_assistant_message
from services.out_of_scope import respond as respond_out_of_scope
from services.scope import is_food_related
from tools import definitions

StreamCallback = Callable[[str, dict], Awaitable[None]]
logger = get_logger("orchestrator")

ORCHESTRATOR_SYSTEM = """Bạn là orchestrator gợi ý món & quán ăn uống tại Việt Nam.

PHẠM VI (in-scope):
- Món ăn, nhà hàng, quán ăn, buffet, lẩu, street food
- Cafe, cà phê, trà sữa, quán nước, bánh ngọt, bar/pub (gợi ý địa điểm)
- Câu dài nhiều ràng buộc về ăn uống → LUÔN xử lý

OUT-OF-SCOPE (từ chối / intent out_of_scope):
- Code, crypto, chính trị, bài tập, thời tiết thuần, tin tức, du lịch không gắn ăn uống
- KHÔNG gắn out_of_scope cho cafe/trà sữa/quán nước

QUY TẮC:
- Luồng: detect_intent → run_food_agent → run_restaurant_agent (nếu có location)
- **Vị trí:** Ưu tiên quận/thành phố user GÕ > GPS
- Câu có tên quận/thành phố → gọi restaurant agent
- KHÔNG ghi đè location trong context patch
- Trả lời ngắn gọn, tôn trọng dị ứng & ngân sách"""


def _to_api_messages(messages: list[Message]) -> list[dict]:
    return [{"role": m.role, "content": m.content} for m in messages]


def _last_user_text(messages: list[Message]) -> str:
    for m in reversed(messages):
        if m.role == "user" and m.content.strip():
            return m.content.strip()
    return ""


def _merge_context(base: UserContext, patch: dict | None) -> UserContext:
    merged = base.model_dump()
    if not patch:
        return base
    for key, val in patch.items():
        if val is None:
            continue
        if key == "location":
            # Không cho LLM/agent ghi đè — vị trí do user chat / GPS đã resolve ở orchestrator
            continue
        if val == [] or val == {}:
            continue
        merged[key] = val
    return UserContext.model_validate(merged)


def _resolve_agent_context(
    base: UserContext,
    patch: dict | None,
    user_text: str,
) -> UserContext:
    """Merge context patch từ tool, giữ ưu tiên vị trí user nhập."""
    merged = _merge_context(base, patch)
    ctx, _ = apply_location_priority(merged, user_text)
    return ctx


async def _safe_fallback(
    messages: list[Message],
    context: UserContext,
    stream_callback: StreamCallback,
    reason: str,
) -> None:
    try:
        await rule_fallback.run(messages, context, stream_callback, reason=reason)
    except Exception as exc:
        log_exception(logger, "rule_fallback failed", exc)
        await respond_apology(stream_callback)


async def run(
    messages: list[Message],
    context: UserContext,
    stream_callback: StreamCallback,
) -> None:
    user_text = _last_user_text(messages)
    context, location_source = apply_location_priority(context, user_text)
    log_event(
        logger,
        "Orchestrator start",
        user=user_text[:160],
        has_location=bool(context.location),
        location_source=location_source,
        lat=context.location.lat if context.location else None,
        lng=context.location.lng if context.location else None,
        address=context.location.address if context.location else None,
    )

    if user_text and not is_food_related(user_text):
        await respond_out_of_scope(stream_callback)
        return

    loc_note = None
    if location_source == "user_message" and user_text:
        loc = extract_location_from_text(user_text)
        if loc and loc.address:
            loc_note = loc.address
    system = (
        build_system_prompt(
            context,
            location_source=location_source,
            user_location_note=loc_note,
        )
        + "\n\n"
        + ORCHESTRATOR_SYSTEM
    )
    api_messages = _to_api_messages(messages)
    food_payload: dict | None = None
    restaurant_payload: dict | None = None
    sent_text = False

    try:
        for _ in range(6):
            try:
                response = await llm.call(
                    system=system,
                    messages=api_messages,
                    tools=definitions.orchestrator_tools,
                )
            except Exception as exc:
                log_exception(logger, "orchestrator llm call failed", exc)
                await _safe_fallback(messages, context, stream_callback, exception_summary(exc))
                return

            if response.stop_reason == "end_turn":
                break

            if response.stop_reason != "tool_use":
                break

            api_messages.append(response_to_assistant_message(response))
            tool_uses = [b for b in response.content if b.type == "tool_use"]
            tool_results_content = []

            for tu in tool_uses:
                result: dict
                log_event(logger, "Orchestrator tool", tool=tu.name, input_keys=",".join(tu.input.keys()))
                if tu.name == "detect_intent":
                    intent = tu.input.get("intent", "clarify")
                    confidence = tu.input.get("confidence", 0)
                    missing = tu.input.get("missing_context", [])
                    if intent == "out_of_scope":
                        if user_text and is_food_related(user_text):
                            intent = "food_and_restaurant"
                            log_event(logger, "Scope override", reason="llm_out_of_scope_but_in_scope")
                        else:
                            await respond_out_of_scope(stream_callback)
                            return
                    await stream_callback(
                        "thinking",
                        {
                            "status": f"intent={intent}, confidence={confidence}",
                            "missing_context": missing,
                        },
                    )
                    result = {
                        "intent": intent,
                        "confidence": confidence,
                        "missing_context": missing,
                    }
                elif tu.name == "run_food_agent":
                    ctx_in = tu.input.get("context") if isinstance(tu.input.get("context"), dict) else {}
                    ctx = _resolve_agent_context(context, ctx_in, user_text)
                    agent_result = await food_agent.run(ctx)
                    if agent_result.get("ask"):
                        await respond_ask(
                            stream_callback,
                            agent_result.get("field", "context"),
                            agent_result.get("message", "Bạn cho mình thêm thông tin nhé?"),
                        )
                        return
                    food_payload = agent_result
                    log_event(
                        logger,
                        "Orchestrator food_results",
                        count=len(agent_result.get("foods", [])),
                        names=",".join(agent_result.get("food_names", [])[:5]),
                    )
                    await stream_callback("food_results", agent_result)
                    result = agent_result
                elif tu.name == "run_restaurant_agent":
                    ctx_in = tu.input.get("context") if isinstance(tu.input.get("context"), dict) else {}
                    ctx = _resolve_agent_context(context, ctx_in, user_text)
                    names = tu.input.get("food_names") or (
                        food_payload.get("food_names", []) if food_payload else []
                    )
                    agent_result = await restaurant_agent.run(ctx, names)
                    if agent_result.get("ask"):
                        await respond_ask(
                            stream_callback,
                            agent_result.get("field", "location"),
                            agent_result.get("message", "Bạn đang ở khu vực nào để mình tìm quán gần bạn?"),
                        )
                        return
                    restaurant_payload = agent_result
                    restaurants = agent_result.get("restaurants", [])
                    log_restaurants(logger, "Orchestrator restaurant_results", restaurants)
                    await stream_callback("restaurant_results", agent_result)
                    result = agent_result
                else:
                    result = {"error": f"unknown tool {tu.name}"}

                tool_results_content.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": tu.id,
                        "content": json.dumps(result, ensure_ascii=False),
                    }
                )

            api_messages.append({"role": "user", "content": tool_results_content})

        # Chưa có kết quả món → fallback
        if not food_payload:
            await _safe_fallback(messages, context, stream_callback, "no_food_results")
            return

        summary_parts = []
        if food_payload:
            summary_parts.append(
                f"Đã gợi ý {len(food_payload.get('foods', []))} món: "
                + ", ".join(food_payload.get("food_names", [])[:5])
            )
        if restaurant_payload:
            summary_parts.append(
                f"Đã tìm {len(restaurant_payload.get('restaurants', []))} quán phù hợp."
            )
        api_messages.append(
            {
                "role": "user",
                "content": (
                    "Kết quả agent:\n"
                    + "\n".join(summary_parts)
                    + "\nHãy tổng hợp cho user bằng tiếng Việt, ngắn gọn, có bullet nếu cần."
                ),
            }
        )

        try:
            stream_mgr = await llm.call(system=system, messages=api_messages, stream=True)
            async with stream_mgr as stream:
                async for text in stream.text_stream:
                    if text:
                        sent_text = True
                        await stream_callback("text", {"delta": text})
        except Exception as exc:
            log_exception(logger, "orchestrator stream failed", exc)
            if not sent_text:
                summary = (
                    f"Dựa trên yêu cầu của bạn, mình gợi ý các món: "
                    f"{', '.join(food_payload.get('food_names', [])[:5])}."
                )
                if restaurant_payload:
                    names = [r.get("name", "") for r in restaurant_payload.get("restaurants", [])[:3]]
                    summary += f" Quán có thể thử: {', '.join(names)}."
                await stream_text(summary, stream_callback)
                sent_text = True

        if not sent_text:
            summary = (
                f"Mình đã chọn giúp bạn: {', '.join(food_payload.get('food_names', [])[:5])}. "
                "Xem chi tiết món và quán ở panel bên phải nhé!"
            )
            await stream_text(summary, stream_callback)

        await finish(
            stream_callback,
            [
                "So sánh thêm quán khác",
                "Đổi món trong cùng ngân sách",
                "Gợi ý món nhẹ hơn",
            ],
        )
    except Exception as exc:
        log_exception(logger, "orchestrator run failed", exc)
        await _safe_fallback(messages, context, stream_callback, exception_summary(exc))
