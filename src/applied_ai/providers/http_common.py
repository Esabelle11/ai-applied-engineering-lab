"""Shared minimal HTTP JSON transport and normalized failure mapping.

Single attempt only: Phase 2's ReliableProvider supplies retries and deadlines.
"""

from __future__ import annotations

import time
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from typing import TYPE_CHECKING, Any

from applied_ai.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConfigurationError,
    InvalidRequestError,
    ProviderConnectionError,
    ProviderResponseError,
    ProviderTimeoutError,
    ProviderUnavailableError,
    RateLimitError,
)

if TYPE_CHECKING:
    import httpx


def _httpx() -> Any:
    try:
        import httpx
    except ImportError as exc:
        raise ConfigurationError("Install HTTP adapters using: uv sync --extra providers") from exc
    return httpx


def retry_after(headers: Any) -> float | None:
    value = headers.get("retry-after")
    if value is None:
        return None
    try:
        return max(0.0, float(value))
    except ValueError:
        try:
            dt = parsedate_to_datetime(value)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=UTC)
            return max(0.0, (dt - datetime.now(UTC)).total_seconds())
        except (ValueError, TypeError, OverflowError):
            return None


class HTTPJSONTransport:
    """Owns a client unless one is injected; callers translate API-specific payloads."""

    def __init__(
        self,
        provider: str,
        *,
        timeout_seconds: float = 30,
        client: httpx.Client | None = None,
    ) -> None:
        httpx = _httpx()
        if not 0 < timeout_seconds <= 600:
            raise ValueError("timeout_seconds must be in (0, 600]")
        self.provider = provider
        self.timeout = timeout_seconds
        self._owns_client = client is None
        self.client = client if client is not None else httpx.Client()

    def close(self) -> None:
        if self._owns_client:
            self.client.close()

    def post(
        self,
        url: str,
        headers: dict[str, str],
        payload: dict[str, Any],
        timeout_seconds: float | None = None,
    ) -> tuple[dict[str, Any], float, str | None]:
        httpx = _httpx()
        start = time.perf_counter()
        try:
            resp = self.client.post(
                url,
                headers=headers,
                json=payload,
                timeout=min(self.timeout, timeout_seconds)
                if timeout_seconds is not None
                else self.timeout,
            )
        except httpx.TimeoutException as exc:
            raise ProviderTimeoutError(
                "Provider request timed out", provider=self.provider
            ) from exc
        except httpx.RequestError as exc:
            raise ProviderConnectionError(
                "Provider connection failed", provider=self.provider
            ) from exc
        elapsed = time.perf_counter() - start
        request_id = resp.headers.get("x-request-id") or resp.headers.get("request-id")
        status = resp.status_code
        meta = dict(provider=self.provider, status_code=status, request_id=request_id)
        if status >= 400:
            if status == 401:
                raise AuthenticationError("Authentication rejected", **meta)
            if status == 403:
                raise AuthorizationError("Access forbidden", **meta)
            if status == 429:
                # raise RateLimitError("Provider rate limit exceeded", **meta, **extra)
                raise RateLimitError(
                    "Provider rate limit exceeded",
                    provider=self.provider,
                    status_code=status,
                    request_id=request_id,
                    retry_after_seconds=retry_after(resp.headers),
                )
            if status in (408, 504):
                raise ProviderTimeoutError("Provider timed out", **meta)
            if status >= 500 or status == 409:
                # raise ProviderUnavailableError("Provider unavailable", **meta, **extra)
                raise ProviderUnavailableError(
                    "Provider unavailable",
                    provider=self.provider,
                    status_code=status,
                    request_id=request_id,
                    retry_after_seconds=retry_after(resp.headers),
                )
            raise InvalidRequestError("Provider rejected request", **meta)
        try:
            obj = resp.json()
        except (ValueError, UnicodeError) as exc:
            raise ProviderResponseError("Provider returned malformed JSON", **meta) from exc
        if not isinstance(obj, dict):
            raise ProviderResponseError("Provider response must be a JSON object", **meta)
        return obj, elapsed, request_id


def token_count(value: Any) -> int | None:
    return value if type(value) is int and value >= 0 else None
