import json
import os
import re
import uuid
from dataclasses import dataclass, field
from typing import Any, AsyncIterator

from google import genai
from google.genai import types

from core.logging_config import get_logger, log_exception

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-lite")
MAX_TOKENS = 4096

logger = get_logger("llm")

_client: genai.Client | None = None


@dataclass
class ContentBlock:
    type: str
    text: str = ""
    id: str = ""
    name: str = ""
    input: dict = field(default_factory=dict)
    thought_signature: Any = None
    function_call_id: str | None = None


@dataclass
class LLMResponse:
    stop_reason: str
    content: list[ContentBlock]


class _GeminiStream:
    """Async context manager exposing text_stream for orchestrator."""

    def __init__(self, stream: Any):
        self._stream = stream

    async def __aenter__(self) -> "_GeminiStream":
        return self

    async def __aexit__(self, *args: Any) -> None:
        return None

    @property
    def text_stream(self) -> AsyncIterator[str]:
        return self._iter_text()

    async def _iter_text(self) -> AsyncIterator[str]:
        async for chunk in self._stream:
            if chunk.text:
                yield chunk.text


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY (or GOOGLE_API_KEY) is not set")
        _client = genai.Client(api_key=api_key)
    return _client


def _tool_id(name: str) -> str:
    return f"{name}__{uuid.uuid4().hex[:8]}"


def _name_from_tool_id(tool_use_id: str) -> str:
    if "__" in tool_use_id:
        return tool_use_id.split("__", 1)[0]
    return tool_use_id


def _anthropic_tools_to_gemini(tools: list[dict]) -> list[types.Tool]:
    declarations = []
    for t in tools:
        schema = dict(t.get("input_schema", {}))
        declarations.append(
            types.FunctionDeclaration(
                name=t["name"],
                description=t.get("description", ""),
                parameters=schema,
            )
        )
    return [types.Tool(function_declarations=declarations)]


def _messages_to_contents(messages: list[dict]) -> list[types.Content]:
    contents: list[types.Content] = []

    for msg in messages:
        role = msg.get("role", "user")
        gemini_role = "model" if role == "assistant" else "user"
        raw = msg.get("content", "")

        if isinstance(raw, str):
            if raw.strip():
                contents.append(
                    types.Content(role=gemini_role, parts=[types.Part(text=raw)])
                )
            continue

        parts: list[types.Part] = []
        for block in raw:
            btype = block.get("type")
            if btype == "text":
                text = block.get("text", "")
                if text:
                    parts.append(types.Part(text=text))
            elif btype == "tool_use":
                args = block.get("input") or {}
                fc_kwargs: dict[str, Any] = {
                    "name": block.get("name", ""),
                    "args": args,
                }
                if block.get("function_call_id"):
                    fc_kwargs["id"] = block["function_call_id"]
                part_kwargs: dict[str, Any] = {
                    "function_call": types.FunctionCall(**fc_kwargs),
                }
                if block.get("thought_signature") is not None:
                    part_kwargs["thought_signature"] = block["thought_signature"]
                parts.append(types.Part(**part_kwargs))
            elif btype == "tool_result":
                name = _name_from_tool_id(block.get("tool_use_id", ""))
                try:
                    response = json.loads(block.get("content", "{}"))
                except json.JSONDecodeError:
                    response = {"raw": block.get("content", "")}
                parts.append(
                    types.Part(
                        function_response=types.FunctionResponse(
                            name=name,
                            response=response,
                        )
                    )
                )

        if parts:
            contents.append(types.Content(role=gemini_role, parts=parts))

    return contents


def _parse_response(response: types.GenerateContentResponse) -> LLMResponse:
    blocks: list[ContentBlock] = []
    has_tool_call = False

    if not response.candidates:
        return LLMResponse(stop_reason="end_turn", content=[])

    for part in response.candidates[0].content.parts or []:
        if part.text:
            blocks.append(ContentBlock(type="text", text=part.text))
        if part.function_call:
            fc = part.function_call
            has_tool_call = True
            args = dict(fc.args) if fc.args else {}
            blocks.append(
                ContentBlock(
                    type="tool_use",
                    id=_tool_id(fc.name or "tool"),
                    name=fc.name or "",
                    input=args,
                    thought_signature=getattr(part, "thought_signature", None),
                    function_call_id=getattr(fc, "id", None),
                )
            )

    stop = "tool_use" if has_tool_call else "end_turn"
    return LLMResponse(stop_reason=stop, content=blocks)


def _extract_json(text: str) -> dict:
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if fence:
        text = fence.group(1).strip()
    return json.loads(text)


def _build_config(system: str, tools: list[dict] | None) -> types.GenerateContentConfig:
    cfg: dict[str, Any] = {
        "system_instruction": system,
        "max_output_tokens": MAX_TOKENS,
    }
    if tools:
        cfg["tools"] = _anthropic_tools_to_gemini(tools)
        cfg["automatic_function_calling"] = types.AutomaticFunctionCallingConfig(
            disable=True
        )
    return types.GenerateContentConfig(**cfg)


async def call(
    system: str,
    messages: list[dict],
    tools: list[dict] | None = None,
    stream: bool = False,
) -> Any:
    client = _get_client()
    contents = _messages_to_contents(messages)
    config = _build_config(system, tools)

    if stream:
        aio_stream = await client.aio.models.generate_content_stream(
            model=MODEL,
            contents=contents,
            config=config,
        )
        return _GeminiStream(aio_stream)

    response = await client.aio.models.generate_content(
        model=MODEL,
        contents=contents,
        config=config,
    )
    return _parse_response(response)


async def call_json(system: str, prompt: str) -> dict:
    client = _get_client()
    try:
        response = await client.aio.models.generate_content(
            model=MODEL,
            contents=[types.Content(role="user", parts=[types.Part(text=prompt)])],
            config=types.GenerateContentConfig(
                system_instruction=system + "\n\nTrả về CHỈ một object JSON hợp lệ, không markdown.",
                max_output_tokens=MAX_TOKENS,
                response_mime_type="application/json",
            ),
        )
        text = response.text or ""
        if not text and response.candidates:
            text = "".join(
                p.text for p in (response.candidates[0].content.parts or []) if p.text
            )
        return _extract_json(text)
    except Exception as exc:
        log_exception(logger, "call_json failed", exc)
        raise
