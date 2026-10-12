"""Normalized provider errors. Error messages never include upstream response bodies."""

from __future__ import annotations

import math


class LLMError(Exception):
    """Base error with safe diagnostic metadata for future reliability policies."""

    category = "unknown"
    retryable = False

    def __init__(
        self,
        message: str,
        *,
        provider: str | None = None,
        status_code: int | None = None,
        request_id: str | None = None,
        retry_after_seconds: float | None = None,
    ) -> None:
        super().__init__(message)
        self.provider = provider
        self.status_code = status_code
        self.request_id = request_id
        if retry_after_seconds is not None and (
            not math.isfinite(retry_after_seconds) or retry_after_seconds < 0
        ):
            raise ValueError("retry_after_seconds must be finite and non-negative")
        self.retry_after_seconds = retry_after_seconds


class ConfigurationError(LLMError):
    category = "configuration"


class InvalidRequestError(LLMError):
    category = "invalid_request"


class CapabilityNotSupportedError(LLMError):
    category = "unsupported_capability"


class AuthenticationError(LLMError):
    category = "authentication"


class AuthorizationError(LLMError):
    category = "authorization"


class RateLimitError(LLMError):
    category = "rate_limit"
    retryable = True


class ProviderTimeoutError(LLMError):
    category = "timeout"
    retryable = True


class ProviderConnectionError(LLMError):
    category = "connection"
    retryable = True


class ProviderUnavailableError(LLMError):
    category = "provider_unavailable"
    retryable = True


class ProviderResponseError(LLMError):
    category = "provider_response"


class InvalidStructuredOutputError(LLMError):
    category = "invalid_structured_output"


class ModelRefusalError(LLMError):
    category = "model_refusal"


class RetryExhaustedError(LLMError):
    """A transient failure remained after all permitted attempts."""

    category = "retry_exhausted"

    def __init__(self, *, last_error: LLMError, attempts: int) -> None:
        super().__init__(
            f"Provider retry budget exhausted after {attempts} attempt(s) ({last_error.category})",
            provider=last_error.provider,
            status_code=last_error.status_code,
            request_id=last_error.request_id,
            retry_after_seconds=last_error.retry_after_seconds,
        )
        self.last_error = last_error
        self.attempts = attempts


class RequestDeadlineExceededError(LLMError):
    category = "request_deadline_exceeded"


class CircuitOpenError(LLMError):
    category = "circuit_open"


class ConcurrencyLimitError(LLMError):
    category = "concurrency_limit"
