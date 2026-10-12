"""Anthropic Messages REST adapter for basic text generation only."""

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


class AnthropicProvider:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        timeout_seconds: float = 30,
        client: httpx.Client | None = None,
    ) -> None:
        key = api_key if api_key is not None else os.getenv("ANTHROPIC_API_KEY", "")
        if not key.strip():
            raise ConfigurationError("ANTHROPIC_API_KEY is required")
        self._key = key
        self._transport = HTTPJSONTransport(
            "anthropic", timeout_seconds=timeout_seconds, client=client
        )

    @property
    def name(self) -> str:
        return "anthropic"

    @property
    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities()

    def close(self) -> None:
        self._transport.close()

    def __enter__(self) -> AnthropicProvider:
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    def generate(self, request: LLMRequest) -> LLMResponse:
        if request.response_format is not None:
            raise CapabilityNotSupportedError(
                "Structured output is not implemented for Anthropic adapter", provider=self.name
            )
        system = "\n".join(m.content for m in request.messages if m.role in ("system", "developer"))
        messages = [
            {"role": m.role, "content": m.content}
            for m in request.messages
            if m.role in ("user", "assistant")
        ]
        if not messages:
            raise ConfigurationError(
                "Anthropic requires at least one user or assistant message", provider=self.name
            )
        payload: dict[str, Any] = {
            "model": request.model,
            "messages": messages,
            "max_tokens": request.max_output_tokens or 512,
        }
        if system:
            payload["system"] = system
        if request.temperature is not None:
            payload["temperature"] = request.temperature
        body, elapsed, rid = self._transport.post(
            "https://api.anthropic.com/v1/messages",
            {
                "x-api-key": self._key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            payload,
            request.timeout_seconds,
        )
        content = body.get("content")
        if not isinstance(content, list):
            raise ProviderResponseError(
                "Anthropic response missing content blocks", provider=self.name
            )
        texts = [
            b["text"]
            for b in content
            if isinstance(b, dict) and b.get("type") == "text" and isinstance(b.get("text"), str)
        ]
        if not texts:
            raise ProviderResponseError("Anthropic returned no text blocks", provider=self.name)
        usage = body.get("usage")
        tokens = (
            TokenUsage(
                token_count(usage.get("input_tokens")),
                token_count(usage.get("output_tokens")),
                None,
            )
            if isinstance(usage, dict)
            else None
        )
        return LLMResponse(
            "\n".join(texts),
            str(body.get("model", request.model)),
            self.name,
            request_id=str(body.get("id") or rid) if (body.get("id") or rid) else None,
            finish_reason=body.get("stop_reason"),
            usage=tokens,
            latency_seconds=elapsed,
        )
