"""Synchronous resilience wrapper over any ``LLMProvider``.

This wrapper *only* calls provider.generate(). It does not rerun user tools.
A deadline is propagated to providers through LLMRequest.timeout_seconds;
custom providers must honor that field for an enforced in-flight timeout.
"""

from __future__ import annotations

import math
import random
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import replace

from applied_ai.core.capabilities import ProviderCapabilities
from applied_ai.core.exceptions import (
    CapabilityNotSupportedError,
    CircuitOpenError,
    LLMError,
    RequestDeadlineExceededError,
    RetryExhaustedError,
)
from applied_ai.core.protocols import LLMProvider
from applied_ai.core.requests import LLMRequest
from applied_ai.core.responses import LLMResponse, ReliabilityStats
from applied_ai.reliability.circuit_breaker import CircuitBreaker
from applied_ai.reliability.limits import ConcurrencyLimiter, TokenBucketLimiter
from applied_ai.reliability.policy import RetryPolicy


class ReliableProvider:
    """Opt-in retry/failover decorator; one attempt per underlying provider call."""

    def __init__(
        self,
        primary: LLMProvider,
        *,
        fallbacks: Sequence[LLMProvider] = (),
        fallback_models: Mapping[str, str] | None = None,
        policy: RetryPolicy | None = None,
        total_timeout_seconds: float = 30.0,
        rate_limiter: TokenBucketLimiter | None = None,
        concurrency_limiter: ConcurrencyLimiter | None = None,
        circuits: Mapping[str, CircuitBreaker] | None = None,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
        random_fraction: Callable[[], float] = random.random,
    ) -> None:
        if not math.isfinite(total_timeout_seconds) or total_timeout_seconds <= 0:
            raise ValueError("total_timeout_seconds must be finite and positive")
        names = [p.name for p in (primary, *fallbacks)]
        if len(names) != len(set(names)):
            raise ValueError("Provider names must be unique for failover")
        overrides = dict(fallback_models or {})
        if not set(overrides).issubset(set(names[1:])):
            raise ValueError("fallback_models must name configured fallback providers")
        if any(not model.strip() for model in overrides.values()):
            raise ValueError("Fallback model identifiers must not be empty")
        self._fallback_models = overrides
        self._primary = primary
        self._fallbacks = tuple(fallbacks)
        self._policy = policy or RetryPolicy()
        self._timeout = total_timeout_seconds
        self._limiter = rate_limiter
        self._concurrency = concurrency_limiter
        self._circuits = dict(circuits or {})
        self._clock = clock
        self._sleep = sleep
        self._random_fraction = random_fraction

    @property
    def name(self) -> str:
        return self._primary.name

    @property
    def capabilities(self) -> ProviderCapabilities:
        return self._primary.capabilities

    def _remaining(self, deadline: float) -> float:
        seconds = deadline - self._clock()
        if seconds <= 0:
            raise RequestDeadlineExceededError("Total LLM request deadline exceeded")
        return seconds

    @staticmethod
    def _require_capability(provider: LLMProvider, request: LLMRequest) -> None:
        if request.response_format is not None and not provider.capabilities.structured_output:
            raise CapabilityNotSupportedError(
                f"Provider {provider.name} cannot satisfy structured output",
                provider=provider.name,
            )
        if not provider.capabilities.synchronous_generation:
            raise CapabilityNotSupportedError(
                f"Provider {provider.name} cannot generate synchronously",
                provider=provider.name,
            )

    def generate(self, request: LLMRequest) -> LLMResponse:
        start = self._clock()
        deadline = start + min(
            self._timeout,
            request.timeout_seconds if request.timeout_seconds is not None else self._timeout,
        )
        attempts = 0
        failovers = 0
        categories: list[str] = []
        providers = (self._primary, *self._fallbacks)
        for index, provider in enumerate(providers):
            target = (
                replace(request, model=self._fallback_models.get(provider.name, request.model))
                if index
                else request
            )
            self._require_capability(provider, target)
            breaker = self._circuits.get(provider.name)
            if index:
                failovers += 1
            for attempt in range(1, self._policy.max_attempts + 1):
                self._remaining(deadline)
                probe_acquired = False
                provider_invoked = False
                try:
                    if breaker is not None:
                        breaker.before_call()
                        probe_acquired = True
                    if self._limiter is not None:
                        self._limiter.acquire(deadline=deadline)
                    if self._concurrency is not None:
                        with self._concurrency.slot(timeout_seconds=self._remaining(deadline)):
                            attempts += 1
                            provider_invoked = True
                            response = provider.generate(
                                replace(target, timeout_seconds=self._remaining(deadline))
                            )
                    else:
                        attempts += 1
                        provider_invoked = True
                        response = provider.generate(
                            replace(target, timeout_seconds=self._remaining(deadline))
                        )
                    self._remaining(deadline)  # reject late results
                    if breaker is not None:
                        breaker.record_success()
                    return replace(
                        response,
                        reliability=ReliabilityStats(
                            attempts=attempts,
                            failovers=failovers,
                            elapsed_seconds=self._clock() - start,
                            error_categories=tuple(categories),
                        ),
                    )
                except CircuitOpenError:
                    categories.append("circuit_open")
                    if index == len(providers) - 1:
                        raise
                    break
                except LLMError as error:
                    categories.append(error.category)
                    if breaker is not None and probe_acquired:
                        if not provider_invoked:
                            breaker.abandon_call()  # local budget or admission failed
                        elif error.retryable:
                            breaker.record_failure()
                        else:
                            breaker.record_success()  # provider replied or rejected request
                    if not error.retryable:
                        raise
                    if attempt == self._policy.max_attempts:
                        if index == len(providers) - 1:
                            raise RetryExhaustedError(
                                last_error=error, attempts=attempts
                            ) from error
                        break
                    delay = self._policy.delay_seconds(attempt, error, self._random_fraction())
                    if delay >= self._remaining(deadline):
                        raise RequestDeadlineExceededError(
                            "Insufficient deadline budget for retry delay"
                        ) from error
                    self._sleep(delay)
                except Exception:
                    if breaker is not None and probe_acquired:
                        breaker.abandon_call()
                    raise
        raise AssertionError("Provider exhaustion was not handled")
