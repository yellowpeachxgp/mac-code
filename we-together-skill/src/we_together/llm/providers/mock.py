"""Mock LLM provider：用于所有单元测试和无 API Key 场景降级。"""
from __future__ import annotations

import json

from we_together.llm.client import (
    LLMMessage,
    LLMResponse,
    JSONExtractionError,
)


class MockLLMClient:
    provider = "mock"

    def __init__(
        self,
        *,
        scripted_responses: list[str] | None = None,
        scripted_json: list[dict] | None = None,
        default_content: str = "[mock response]",
        default_json: dict | None = None,
    ):
        self._scripted_responses = list(scripted_responses or [])
        self._scripted_json = list(scripted_json or [])
        self.default_content = default_content
        self.default_json = default_json if default_json is not None else {"mock": True}
        self.calls: list[dict] = []

    def chat(self, messages: list[LLMMessage], **kwargs) -> LLMResponse:
        self.calls.append({"type": "chat", "messages": messages, "kwargs": kwargs})
        if self._scripted_responses:
            content = self._scripted_responses.pop(0)
        else:
            content = self.default_content
        return LLMResponse(content=content, model="mock", usage={}, raw={})

    def chat_json(
        self,
        messages: list[LLMMessage],
        schema_hint: dict | str,
        **kwargs,
    ) -> dict:
        self.calls.append({
            "type": "chat_json",
            "messages": messages,
            "schema_hint": schema_hint,
            "kwargs": kwargs,
        })
        if self._scripted_json:
            return self._scripted_json.pop(0)
        return dict(self.default_json)

    def queue_response(self, content: str) -> None:
        self._scripted_responses.append(content)

    def queue_json(self, payload: dict) -> None:
        self._scripted_json.append(payload)


def parse_json_loose(text: str) -> dict:
    """尝试从 LLM 响应中抽取 JSON 对象。

    支持:
      - 纯 JSON
      - ```json ... ``` 围栏
      - 前后有多余解释文本
    """
    text = text.strip()
    if text.startswith("```"):
        inner = text.strip("`")
        if inner.lower().startswith("json"):
            inner = inner[4:]
        text = inner.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise JSONExtractionError(f"no JSON object found in: {text[:80]!r}")
    candidate = text[start : end + 1]
    try:
        return json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise JSONExtractionError(str(exc)) from exc
