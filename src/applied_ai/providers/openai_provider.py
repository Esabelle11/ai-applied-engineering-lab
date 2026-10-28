"""Minimal synchronous OpenAI Responses API adapter using optional httpx.

No SDK-level retries are added here. ``ReliableProvider`` supplies an explicit retry policy.
"""

from __future__ import annotations

import math
import os
import time
from collections.abc import Mapping
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from typing import TYPE_CHECKING, Any

from applied_ai.core.capabilities import ProviderCapabilities
from applied_ai.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    CapabilityNotSupportedError,
    ConfigurationError,
    InvalidRequestError,
    ModelRefusalError,
    ProviderConnectionError,
    ProviderResponseError,
    ProviderTimeoutError,
    ProviderUnavailableError,
    RateLimitError,
)
from applied_ai.core.requests import LLMRequest
from applied_ai.core.responses import LLMResponse, TokenUsage
from applied_ai.core.structured import parse_structured_output

if TYPE_CHECKING:
    import httpx


class OpenAIProvider:
    """Provider-neutral generate() via POST /v1/responses, with injectable HTTP client."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str = "https://api.openai.com/v1",
        timeout_seconds: float = 30.0,
        client: httpx.Client | None = None,
    ) -> None:
        try:
            import httpx as httpx_module
        except ImportError as exc:
            raise ConfigurationError(
                "OpenAIProvider needs optional httpx: uv sync --extra openai"
            ) from exc
        key = api_key if api_key is not None else os.environ.get("OPENAI_API_KEY", "")
        if not key.strip():
            raise ConfigurationError("OPENAI_API_KEY is required for the live provider")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if not base_url.startswith("https://"):
            raise ValueError("base_url must use HTTPS to protect API credentials")
        self._key = key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout_seconds
        self._httpx = httpx_module
        self._owns_client = client is None
        self._client = client if client is not None else httpx_module.Client()
        self._capabilities = ProviderCapabilities(structured_output=True)

    @property
    def name(self) -> str:
        return "openai"

    @property
    def capabilities(self) -> ProviderCapabilities:
        return self._capabilities

    def close(self) -> None:
        """Close only the HTTP client created by this provider."""
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> OpenAIProvider:
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    def generate(self, request: LLMRequest) -> LLMResponse:
        payload: dict[str, Any] = {
            "model": request.model,
            "input": [
                {"role": message.role, "content": message.content} for message in request.messages
            ],
            "store": False,
        }
        if request.max_output_tokens is not None:
            payload["max_output_tokens"] = request.max_output_tokens
        if request.temperature is not None:
            payload["temperature"] = request.temperature
        if request.response_format is not None:
            if not self.capabilities.structured_output:
                # Defensive: custom adapter subclasses may alter capability flags.
                raise CapabilityNotSupportedError(
                    "Provider does not support structured output", provider=self.name
                )
            spec = request.response_format
            payload["text"] = {
                "format": {
                    "type": "json_schema",
                    "name": spec.name,
                    "schema": dict(spec.schema),
                    "strict": spec.strict,
                }
            }
        start = time.perf_counter()
        try:
            response = self._client.post(
                f"{self._base_url}/responses",
                headers={
                    "Authorization": f"Bearer {self._key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=min(self._timeout, request.timeout_seconds)
                if request.timeout_seconds is not None
                else self._timeout,
            )
        except self._httpx.TimeoutException as exc:
            raise ProviderTimeoutError("OpenAI request timed out", provider=self.name) from exc
        except self._httpx.RequestError as exc:
            raise ProviderConnectionError(
                "Unable to connect to OpenAI", provider=self.name
            ) from exc
        latency = time.perf_counter() - start
        if response.status_code >= 400:
            raise self._map_http_error(response)
        try:
            body: Any = response.json()
        except ValueError as exc:
            raise ProviderResponseError("OpenAI returned invalid JSON", provider=self.name) from exc
        if not isinstance(body, dict):
            raise ProviderResponseError("OpenAI response is not an object", provider=self.name)
        request_id = _optional_str(body.get("id")) or response.headers.get("x-request-id")
        status = body.get("status")
        if status != "completed":
            raise ProviderResponseError(
                "OpenAI response was not completed", provider=self.name, request_id=request_id
            )
        text = _extract_text(body, request_id=request_id)
        usage = _parse_usage(body.get("usage"))
        parsed = (
            parse_structured_output(text, request.response_format, provider=self.name)
            if request.response_format is not None
            else None
        )
        return LLMResponse(
            text=text,
            model=_optional_str(body.get("model")) or request.model,
            provider=self.name,
            request_id=request_id,
            finish_reason=str(status),
            usage=usage,
            latency_seconds=latency,
            parsed_output=parsed,
        )

    def _map_http_error(self, response: httpx.Response) -> Exception:
        code = response.status_code
        request_id = response.headers.get("x-request-id")
        kwargs = {"provider": self.name, "status_code": code, "request_id": request_id}
        retry_after = _parse_retry_after(response.headers.get("retry-after"))
        retry_kwargs = {**kwargs, "retry_after_seconds": retry_after}
        if code == 401:
            return AuthenticationError("OpenAI authentication failed", **kwargs)
        if code == 403:
            return AuthorizationError("OpenAI authorization failed", **kwargs)
        if code == 408:
            return ProviderTimeoutError("OpenAI request timed out", **retry_kwargs)
        if code == 429:
            return RateLimitError("OpenAI rate limit exceeded", **retry_kwargs)
        if code in {409, 425} or code >= 500:
            return ProviderUnavailableError("OpenAI service unavailable", **retry_kwargs)
        return InvalidRequestError("OpenAI rejected the request", **kwargs)


def _optional_str(value: Any) -> str | None:
    return value if isinstance(value, str) and value else None


def _parse_usage(value: Any) -> TokenUsage | None:
    if not isinstance(value, Mapping):
        return None

    def token(key: str) -> int | None:
        count = value.get(key)
        return count if type(count) is int and count >= 0 else None

    return TokenUsage(
        input_tokens=token("input_tokens"),
        output_tokens=token("output_tokens"),
        total_tokens=token("total_tokens"),
    )


def _extract_text(body: dict[str, Any], *, request_id: str | None) -> str:
    pieces: list[str] = []
    output = body.get("output")
    if not isinstance(output, list):
        raise ProviderResponseError(
            "OpenAI response has no output list", provider="openai", request_id=request_id
        )
    for item in output:
        if not isinstance(item, Mapping) or item.get("type") != "message":
            continue
        content = item.get("content")
        if not isinstance(content, list):
            continue
        for part in content:
            if not isinstance(part, Mapping):
                continue
            if part.get("type") == "refusal" or part.get("refusal"):
                raise ModelRefusalError(
                    "OpenAI model refused the request", provider="openai", request_id=request_id
                )
            if part.get("type") == "output_text" and isinstance(part.get("text"), str):
                pieces.append(part["text"])
    if not pieces:
        raise ProviderResponseError(
            "OpenAI response contains no text", provider="openai", request_id=request_id
        )
    return "".join(pieces)


def _parse_retry_after(header: str | None) -> float | None:
    """Support delta-seconds and HTTP-date; malformed headers are ignored."""
    if header is None:
        return None
    try:
        seconds = float(header.strip())
    except ValueError:
        try:
            target = parsedate_to_datetime(header)
            if target.tzinfo is None:
                target = target.replace(tzinfo=UTC)
            seconds = (target - datetime.now(UTC)).total_seconds()
        except (TypeError, ValueError, OverflowError):
            return None
    return max(0.0, seconds) if math.isfinite(seconds) else None
