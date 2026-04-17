"""OpenAI-compatible provider (延迟 import)。

适用于任何实现 OpenAI Chat Completions 协议的后端：
OpenAI 官方、Azure、Ollama、vLLM 等。
"""
from __future__ import annotations

import os

from we_together.llm.client import LLMMessage, LLMResponse
from we_together.llm.providers.mock import parse_json_loose


class OpenAICompatClient:
    provider = "openai_compat"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str = "gpt-4o-mini",
        max_tokens: int = 4096,
    ):
        try:
            import openai  # noqa: F401
        except ImportError as exc:
            raise RuntimeError(
                "openai SDK not installed. `pip install openai` or use mock provider."
            ) from exc
        self._api_key = api_key or os.environ.get("OPENAI_API_KEY") or "dummy"
        self._base_url = base_url or os.environ.get("OPENAI_BASE_URL")
        self.model = model
        self.max_tokens = max_tokens
        import openai as _openai
        client_kwargs = {"api_key": self._api_key}
        if self._base_url:
            client_kwargs["base_url"] = self._base_url
        self._client = _openai.OpenAI(**client_kwargs)

    def chat(self, messages: list[LLMMessage], **kwargs) -> LLMResponse:
        payload = [{"role": m.role, "content": m.content} for m in messages]
        resp = self._client.chat.completions.create(
            model=kwargs.get("model", self.model),
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
            messages=payload,
        )
        choice = resp.choices[0]
        content = choice.message.content or ""
        usage = {}
        if getattr(resp, "usage", None):
            usage = {
                "prompt_tokens": resp.usage.prompt_tokens,
                "completion_tokens": resp.usage.completion_tokens,
            }
        return LLMResponse(content=content, model=resp.model, usage=usage, raw={"id": resp.id})

    def chat_json(
        self,
        messages: list[LLMMessage],
        schema_hint: dict | str,
        **kwargs,
    ) -> dict:
        guard = (
            "Return ONLY a valid JSON object matching this schema hint. "
            f"No explanation. Schema: {schema_hint}"
        )
        augmented = list(messages) + [LLMMessage(role="user", content=guard)]
        resp = self.chat(augmented, **kwargs)
        return parse_json_loose(resp.content)
