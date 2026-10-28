"""Ollama local /api/chat adapter; never sends credentials to remote hosts."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from urllib.parse import urlsplit

from applied_ai.core.capabilities import ProviderCapabilities
from applied_ai.core.exceptions import CapabilityNotSupportedError, ProviderResponseError
from applied_ai.core.requests import LLMRequest
from applied_ai.core.responses import LLMResponse, TokenUsage
from applied_ai.providers.http_common import HTTPJSONTransport, token_count

if TYPE_CHECKING:
    import httpx


class OllamaProvider:
    def __init__(
        self,
        *,
        base_url: str = "http://127.0.0.1:11434",
        timeout_seconds: float = 30,
        client: httpx.Client | None = None,
    ) -> None:
        parsed = urlsplit(base_url)
        if (
            parsed.scheme != "http"
            or parsed.hostname not in ("localhost", "127.0.0.1", "::1")
            or parsed.username
            or parsed.password
        ):
            raise ValueError("Ollama adapter only allows loopback HTTP endpoints")
        self._base_url = base_url.rstrip("/")
        self._transport = HTTPJSONTransport(
            "ollama", timeout_seconds=timeout_seconds, client=client
        )

    @property
    def name(self) -> str:
        return "ollama"

    @property
    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities()

    def close(self) -> None:
        self._transport.close()

    def __enter__(self) -> OllamaProvider:
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    def generate(self, request: LLMRequest) -> LLMResponse:
        if request.response_format is not None:
            raise CapabilityNotSupportedError(
                "Structured output is not implemented for Ollama adapter", provider=self.name
            )
        payload: dict[str, Any] = {
            "model": request.model,
            "messages": [
                {"role": "system" if m.role == "developer" else m.role, "content": m.content}
                for m in request.messages
            ],
            "stream": False,
        }
        options: dict[str, Any] = {}
        if request.temperature is not None:
            options["temperature"] = request.temperature
        if request.max_output_tokens is not None:
            options["num_predict"] = request.max_output_tokens
        if options:
            payload["options"] = options
        body, elapsed, rid = self._transport.post(
            self._base_url + "/api/chat", {}, payload, request.timeout_seconds
        )
        msg = body.get("message")
        if not isinstance(msg, dict) or not isinstance(msg.get("content"), str):
            raise ProviderResponseError("Ollama returned no text response", provider=self.name)
        return LLMResponse(
            msg["content"],
            str(body.get("model", request.model)),
            self.name,
            request_id=rid,
            finish_reason=body.get("done_reason"),
            usage=TokenUsage(
                token_count(body.get("prompt_eval_count")),
                token_count(body.get("eval_count")),
                None,
            ),
            latency_seconds=elapsed,
        )
