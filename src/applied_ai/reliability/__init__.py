"""Opt-in reliability utilities; provider adapters remain single-attempt by default."""

from applied_ai.reliability.circuit_breaker import CircuitBreaker, CircuitState
from applied_ai.reliability.idempotency import IdempotencyGuard
from applied_ai.reliability.limits import ConcurrencyLimiter, TokenBucketLimiter
from applied_ai.reliability.policy import RetryPolicy
from applied_ai.reliability.provider import ReliableProvider
from applied_ai.reliability.utilities import (
    ErrorClassification,
    RequestQueue,
    classify_error,
    full_jitter,
    recover_json_output,
    validate_text_output,
    with_degradation,
)

__all__ = [
    "CircuitBreaker",
    "CircuitState",
    "ConcurrencyLimiter",
    "ErrorClassification",
    "IdempotencyGuard",
    "RequestQueue",
    "ReliableProvider",
    "RetryPolicy",
    "TokenBucketLimiter",
    "classify_error",
    "full_jitter",
    "recover_json_output",
    "validate_text_output",
    "with_degradation",
]
