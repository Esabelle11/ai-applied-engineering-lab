"""Google Gemini generateContent REST adapter (text-only)."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any
from urllib.parse import quote

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


class GoogleProvider:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        timeout_seconds: float = 30,
        client: httpx.Client | None = None,
    ) -> None:
        key = (
            api_key
            if api_key is not None
            else (os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or "")
        )
        if not key.strip():
            raise ConfigurationError("GOOGLE_API_KEY or GEMINI_API_KEY is required")
        self._key = key
        self._transport = HTTPJSONTransport(
            "google", timeout_seconds=timeout_seconds, client=client
        )

    @property
    def name(self) -> str:
        return "google"

    @property
    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities()

    def close(self) -> None:
        self._transport.close()

    def __enter__(self) -> GoogleProvider:
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    def generate(self, request: LLMRequest) -> LLMResponse:
        if request.response_format is not None:
            raise CapabilityNotSupportedError(
                "Structured output is not implemented for Google adapter", provider=self.name
            )
        system = "\n".join(m.content for m in request.messages if m.role in ("system", "developer"))
        contents = [
            {"role": "model" if m.role == "assistant" else "user", "parts": [{"text": m.content}]}
            for m in request.messages
            if m.role in ("user", "assistant")
        ]
        if not contents:
            raise ConfigurationError(
                "Google requires a user or assistant message", provider=self.name
            )
        payload: dict[str, Any] = {"contents": contents}
        if system:
            payload["systemInstruction"] = {"parts": [{"text": system}]}
        gen_config: dict[str, Any] = {}
        if request.max_output_tokens is not None:
            gen_config["maxOutputTokens"] = request.max_output_tokens
        if request.temperature is not None:
            gen_config["temperature"] = request.temperature
        if gen_config:
            payload["generationConfig"] = gen_config
        body, elapsed, rid = self._transport.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{quote(request.model, safe='-_.')}:generateContent",
            {"x-goog-api-key": self._key, "Content-Type": "application/json"},
            payload,
            request.timeout_seconds,
        )
        try:
            candidate = body["candidates"][0]
            parts = candidate["content"]["parts"]
            texts = [
                p["text"] for p in parts if isinstance(p, dict) and isinstance(p.get("text"), str)
            ]
            if not texts:
                raise ValueError("No text")
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise ProviderResponseError(
                "Google returned no text response", provider=self.name
            ) from exc
        usage = body.get("usageMetadata")
        tokens = (
            TokenUsage(
                token_count(usage.get("promptTokenCount")),
                token_count(usage.get("candidatesTokenCount")),
                token_count(usage.get("totalTokenCount")),
            )
            if isinstance(usage, dict)
            else None
        )
        return LLMResponse(
            "\n".join(texts),
            request.model,
            self.name,
            request_id=rid,
            finish_reason=candidate.get("finishReason"),
            usage=tokens,
            latency_seconds=elapsed,
        )
