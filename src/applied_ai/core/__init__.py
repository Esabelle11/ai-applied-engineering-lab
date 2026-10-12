"""Provider-neutral contracts and categorized errors."""

from applied_ai.core.capabilities import ProviderCapabilities
from applied_ai.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    CapabilityNotSupportedError,
    CircuitOpenError,
    ConcurrencyLimitError,
    ConfigurationError,
    InvalidRequestError,
    InvalidStructuredOutputError,
    LLMError,
    ModelRefusalError,
    ProviderConnectionError,
    ProviderResponseError,
    ProviderTimeoutError,
    ProviderUnavailableError,
    RateLimitError,
    RequestDeadlineExceededError,
    RetryExhaustedError,
)
from applied_ai.core.messages import Message
from applied_ai.core.protocols import LLMProvider
from applied_ai.core.requests import LLMRequest, StructuredOutputSpec
from applied_ai.core.responses import LLMResponse, ReliabilityStats, TokenUsage

__all__ = [
    "AuthenticationError",
    "AuthorizationError",
    "CapabilityNotSupportedError",
    "ConfigurationError",
    "InvalidRequestError",
    "InvalidStructuredOutputError",
    "LLMError",
    "LLMProvider",
    "LLMRequest",
    "LLMResponse",
    "Message",
    "ModelRefusalError",
    "ProviderCapabilities",
    "ProviderConnectionError",
    "ProviderResponseError",
    "ProviderTimeoutError",
    "ProviderUnavailableError",
    "RateLimitError",
    "RetryExhaustedError",
    "RequestDeadlineExceededError",
    "CircuitOpenError",
    "ConcurrencyLimitError",
    "ReliabilityStats",
    "StructuredOutputSpec",
    "TokenUsage",
]
