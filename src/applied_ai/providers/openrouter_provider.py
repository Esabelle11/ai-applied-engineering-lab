"""OpenRouter chat-completions adapter. Model capability declarations are conservative."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

from applied_ai.core.capabilities import ProviderCapabilities
from applied_ai.core.exceptions import (
    CapabilityNotSupportedError,
    ConfigurationError,
    ProviderResponseError,
)
from applied_ai.core.requests import LLMRequest
from applied_ai.core.responses import LLMResponse, TokenUsage
from applied_ai.providers.http_common import HTTPJSONTransport, token_count

if TYPE_CHECKING:
    import httpx


class OpenRouterProvider:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        timeout_seconds: float = 30,
        client: httpx.Client | None = None,
    ) -> None:
        key = api_key if api_key is not None else os.getenv("OPENROUTER_API_KEY", "")
        if not key.strip():
            raise ConfigurationError("OPENROUTER_API_KEY is required")
        self._key = key
        self._transport = HTTPJSONTransport(
            "openrouter", timeout_seconds=timeout_seconds, client=client
        )

    @property
    def name(self) -> str:
        return "openrouter"

    @property
    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities()  # Structured-output support is model-dependent.

    def close(self) -> None:
        self._transport.close()

    def __enter__(self) -> OpenRouterProvider:
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    def generate(self, request: LLMRequest) -> LLMResponse:
        if request.response_format is not None:
            raise CapabilityNotSupportedError(
                "Structured JSON Schema support varies by OpenRouter model; no silent downgrade",
                provider=self.name,
            )
        payload: dict[str, Any] = {
            "model": request.model,
            "messages": [{"role": m.role, "content": m.content} for m in request.messages],
        }
        if request.max_output_tokens is not None:
            payload["max_tokens"] = request.max_output_tokens
        if request.temperature is not None:
            payload["temperature"] = request.temperature
        body, elapsed, rid = self._transport.post(
            "https://openrouter.ai/api/v1/chat/completions",
            {"Authorization": f"Bearer {self._key}", "Content-Type": "application/json"},
            payload,
            request.timeout_seconds,
        )
        try:
            choice = body["choices"][0]
            result = choice["message"]["content"]
            if not isinstance(result, str):
                raise TypeError("Non-text output")
        except (KeyError, IndexError, TypeError) as exc:
            raise ProviderResponseError(
                "OpenRouter returned no text response", provider=self.name
            ) from exc
        usage = body.get("usage")
        tokens = (
            TokenUsage(
                token_count(usage.get("prompt_tokens")),
                token_count(usage.get("completion_tokens")),
                token_count(usage.get("total_tokens")),
            )
            if isinstance(usage, dict)
            else None
        )
        return LLMResponse(
            text=result,
            provider=self.name,
            model=str(body.get("model", request.model)),
            request_id=str(body.get("id") or rid) if (body.get("id") or rid) else None,
            finish_reason=str(choice.get("finish_reason")) if choice.get("finish_reason") else None,
            usage=tokens,
            latency_seconds=elapsed,
        )
