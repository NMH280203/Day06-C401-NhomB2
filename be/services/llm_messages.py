"""Convert LLM responses to message blocks (preserves Gemini thought_signature)."""

from typing import Any

from services.llm import ContentBlock, LLMResponse, _tool_id


def blocks_to_message_content(blocks: list[ContentBlock]) -> list[dict]:
    out: list[dict] = []
    for block in blocks:
        if block.type == "text":
            out.append({"type": "text", "text": block.text})
        elif block.type == "tool_use":
            item: dict[str, Any] = {
                "type": "tool_use",
                "id": block.id,
                "name": block.name,
                "input": block.input,
            }
            if block.thought_signature is not None:
                item["thought_signature"] = block.thought_signature
            if block.function_call_id:
                item["function_call_id"] = block.function_call_id
            out.append(item)
    return out


def response_to_assistant_message(response: LLMResponse) -> dict:
    return {
        "role": "assistant",
        "content": blocks_to_message_content(response.content),
    }
