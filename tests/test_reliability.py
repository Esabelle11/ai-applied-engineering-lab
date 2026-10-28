"""Deterministic fault-injection tests for reliability behavior."""

from __future__ import annotations

import pytest

from applied_ai import LLMRequest, Message, MockProvider
from applied_ai.core.exceptions import (
    AuthenticationError,
    CapabilityNotSupportedError,
    CircuitOpenError,
    ConcurrencyLimitError,
    InvalidRequestError,
    ProviderTimeoutError,
    ProviderUnavailableError,
    RateLimitError,
    RequestDeadlineExceededError,
    RetryExhaustedError,
)
from applied_ai.core.requests import StructuredOutputSpec
from applied_ai.reliability import (
    CircuitBreaker,
    CircuitState,
    ConcurrencyLimiter,
    IdempotencyGuard,
    ReliableProvider,
    RetryPolicy,
    TokenBucketLimiter,
)


class Clock:
    def __init__(self) -> None:
        self.t = 0.0
        self.sleeps: list[float] = []

    def monotonic(self) -> float:
        return self.t

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.t += seconds


class Backup(MockProvider):
    @property
    def name(self) -> str:
        return "backup"


@pytest.fixture
def sample_request() -> LLMRequest:
    return LLMRequest("model-test", (Message("user", "hello"),))


def reliable(mock: MockProvider, clock: Clock, **kwargs: object) -> ReliableProvider:
    return ReliableProvider(
        mock,
        clock=clock.monotonic,
        sleep=clock.sleep,
        random_fraction=lambda: 0.5,
        **kwargs,  # type: ignore[arg-type]
    )


def test_recovers_after_two_faults_and_reports_attempts(sample_request: LLMRequest) -> None:
    c = Clock()
    p = MockProvider(
        default_text="done", faults=[RateLimitError("429"), ProviderUnavailableError("503")]
    )
    policy = RetryPolicy(max_attempts=3, initial_delay_seconds=0.5, jitter=False)
    response = reliable(p, c, policy=policy).generate(sample_request)
    assert response.text == "done"
    assert response.reliability is not None
    assert response.reliability.attempts == 3
    assert response.reliability.error_categories == ("rate_limit", "provider_unavailable")
    assert c.sleeps == [0.5, 1.0]
    assert response.reliability.elapsed_seconds == pytest.approx(1.5)


@pytest.mark.parametrize("error", [AuthenticationError("401"), InvalidRequestError("400")])
def test_nonretryable_fails_immediately(sample_request: LLMRequest, error: Exception) -> None:
    mock = MockProvider(faults=[error])
    with pytest.raises(type(error)):
        reliable(mock, Clock()).generate(sample_request)
    assert mock.call_count == 1


def test_retry_exhaustion_preserves_last_error(sample_request: LLMRequest) -> None:
    mock = MockProvider(faults=[ProviderUnavailableError("503")] * 3)
    with pytest.raises(RetryExhaustedError) as failure:
        reliable(
            mock, Clock(), policy=RetryPolicy(max_attempts=2, initial_delay_seconds=0)
        ).generate(sample_request)
    assert failure.value.attempts == 2
    assert isinstance(failure.value.last_error, ProviderUnavailableError)
    assert mock.call_count == 2


def test_full_jitter_and_retry_after() -> None:
    p = RetryPolicy(initial_delay_seconds=2, max_delay_seconds=5, jitter=True)
    assert p.delay_seconds(1, RateLimitError("429"), 0.25) == 0.5
    assert p.delay_seconds(10, RateLimitError("429"), 1) == 5
    assert p.delay_seconds(1, RateLimitError("429", retry_after_seconds=6), 0) == 6


def test_retry_after_respected(sample_request: LLMRequest) -> None:
    c = Clock()
    mock = MockProvider(default_text="ok", faults=[RateLimitError("429", retry_after_seconds=4)])
    response = reliable(mock, c, policy=RetryPolicy(max_attempts=2)).generate(sample_request)
    assert response.text == "ok"
    assert c.sleeps == [4]


def test_deadline_prevents_waiting_beyond_budget(sample_request: LLMRequest) -> None:
    c = Clock()
    mock = MockProvider(faults=[RateLimitError("429", retry_after_seconds=20)])
    with pytest.raises(RequestDeadlineExceededError):
        reliable(mock, c, total_timeout_seconds=5).generate(sample_request)
    assert c.sleeps == []
    assert mock.call_count == 1


def test_request_timeout_caps_total_budget(sample_request: LLMRequest) -> None:
    c = Clock()
    limited = LLMRequest(sample_request.model, sample_request.messages, timeout_seconds=1)
    mock = MockProvider(faults=[RateLimitError("429", retry_after_seconds=2)])
    with pytest.raises(RequestDeadlineExceededError):
        reliable(mock, c, total_timeout_seconds=20).generate(limited)


def test_provider_receives_reduced_time_budget(sample_request: LLMRequest) -> None:
    c = Clock()

    class TimeProbe(MockProvider):
        def generate(self, req: LLMRequest):  # type: ignore[no-untyped-def]
            assert req.timeout_seconds is not None and req.timeout_seconds <= 5
            return super().generate(req)

    reliable(TimeProbe(), c, total_timeout_seconds=5).generate(sample_request)


def test_fallback_only_after_retryable_exhaustion(sample_request: LLMRequest) -> None:
    primary = MockProvider(faults=[ProviderTimeoutError("slow")] * 2)
    backup = Backup(default_text="from backup")
    result = reliable(
        primary,
        Clock(),
        fallbacks=[backup],
        policy=RetryPolicy(max_attempts=2, initial_delay_seconds=0),
    ).generate(sample_request)
    assert result.text == "from backup"
    assert result.provider == "backup"
    assert result.reliability is not None
    assert result.reliability.attempts == 3
    assert result.reliability.failovers == 1


def test_no_fallback_on_invalid_request(sample_request: LLMRequest) -> None:
    primary = MockProvider(faults=[InvalidRequestError("bad")])
    backup = Backup(default_text="not called")
    with pytest.raises(InvalidRequestError):
        reliable(primary, Clock(), fallbacks=[backup]).generate(sample_request)
    assert backup.call_count == 0


def test_capability_mismatch_is_not_downgraded() -> None:
    req = LLMRequest(
        "test",
        (Message("user", "json"),),
        response_format=StructuredOutputSpec("obj", {"type": "object"}),
    )
    primary = MockProvider(faults=[RateLimitError("429")])
    backup = Backup(supports_structured_output=False)
    with pytest.raises(CapabilityNotSupportedError):
        reliable(primary, Clock(), fallbacks=[backup], policy=RetryPolicy(max_attempts=1)).generate(
            req
        )
    assert backup.call_count == 0


def test_reject_same_name_fallback() -> None:
    with pytest.raises(ValueError):
        ReliableProvider(MockProvider(), fallbacks=[MockProvider()])


def test_token_bucket_delays_second_request() -> None:
    c = Clock()
    limiter = TokenBucketLimiter(2, burst=1, clock=c.monotonic, sleep=c.sleep)
    limiter.acquire()
    limiter.acquire()
    assert c.sleeps == [0.5]


def test_token_bucket_rejects_unreachable_deadline() -> None:
    c = Clock()
    limiter = TokenBucketLimiter(1, clock=c.monotonic, sleep=c.sleep)
    limiter.acquire()
    with pytest.raises(RequestDeadlineExceededError):
        limiter.acquire(deadline=c.monotonic() + 0.2)
    assert c.sleeps == []


def test_concurrency_capacity_and_release() -> None:
    limiter = ConcurrencyLimiter(1)

    with (
        limiter.slot(timeout_seconds=0),
        pytest.raises(ConcurrencyLimitError),
        limiter.slot(timeout_seconds=0),
    ):
        pass

    with limiter.slot(timeout_seconds=0):
        pass


def test_circuit_open_half_open_and_recovery() -> None:
    c = Clock()
    breaker = CircuitBreaker(failure_threshold=2, reset_timeout_seconds=5, clock=c.monotonic)
    breaker.before_call()
    breaker.record_failure()
    breaker.before_call()
    breaker.record_failure()
    assert breaker.state == CircuitState.OPEN
    with pytest.raises(CircuitOpenError):
        breaker.before_call()
    c.sleep(5)
    breaker.before_call()
    assert breaker.state == CircuitState.HALF_OPEN
    with pytest.raises(CircuitOpenError):
        breaker.before_call()
    breaker.record_success()
    assert breaker.state == CircuitState.CLOSED


def test_half_open_failure_reopens_circuit() -> None:
    c = Clock()
    breaker = CircuitBreaker(failure_threshold=1, reset_timeout_seconds=2, clock=c.monotonic)
    breaker.before_call()
    breaker.record_failure()
    c.sleep(2)
    breaker.before_call()
    breaker.record_failure()
    assert breaker.state == CircuitState.OPEN


def test_circuit_wrapper_fails_over_when_open(sample_request: LLMRequest) -> None:
    c = Clock()
    circuit = CircuitBreaker(failure_threshold=1, reset_timeout_seconds=10, clock=c.monotonic)
    primary = MockProvider(faults=[ProviderUnavailableError("503")])
    backup = Backup(default_text="good")
    result = reliable(
        primary,
        c,
        fallbacks=[backup],
        circuits={"mock": circuit},
        policy=RetryPolicy(max_attempts=3, initial_delay_seconds=0),
    ).generate(sample_request)
    assert result.text == "good"
    assert primary.call_count == 1
    assert circuit.state == CircuitState.OPEN


def test_deduplicated_side_effects_and_failed_attempts() -> None:
    store = IdempotencyGuard()
    writes: list[str] = []

    def effect():  # type: ignore[no-untyped-def]
        writes.append("charge")
        return "receipt"

    assert store.run_once("sample_request-123", effect) == "receipt"
    assert store.run_once("sample_request-123", effect) == "receipt"
    assert writes == ["charge"]

    def fail():  # type: ignore[no-untyped-def]
        raise ValueError("write not completed")

    with pytest.raises(ValueError):
        store.run_once("sample_request-456", fail)
    assert store.run_once("sample_request-456", effect) == "receipt"
    assert writes == ["charge", "charge"]


@pytest.mark.parametrize(
    "policy",
    [RetryPolicy(max_attempts=1), RetryPolicy(initial_delay_seconds=0)],
)
def test_valid_retry_policies(policy: RetryPolicy) -> None:
    assert policy.max_attempts >= 1


@pytest.mark.parametrize("bad", [0, -1])
def test_invalid_attempts(bad: int) -> None:
    with pytest.raises(ValueError):
        RetryPolicy(max_attempts=bad)


def test_deadline_rejects_late_result(sample_request: LLMRequest) -> None:
    c = Clock()

    class Slow(MockProvider):
        def generate(self, req: LLMRequest):  # type: ignore[no-untyped-def]
            c.sleep(10)
            return super().generate(req)

    with pytest.raises(RequestDeadlineExceededError):
        reliable(Slow(), c, total_timeout_seconds=2).generate(sample_request)


def test_fallback_model_override(sample_request: LLMRequest) -> None:
    primary = MockProvider(faults=[RateLimitError("429")])
    backup = Backup(default_text="other model")
    response = reliable(
        primary,
        Clock(),
        fallbacks=[backup],
        fallback_models={"backup": "different-model"},
        policy=RetryPolicy(max_attempts=1),
    ).generate(sample_request)
    assert response.model == "different-model"
    assert sample_request.model == "model-test"


def test_invalid_fallback_model_override() -> None:
    with pytest.raises(ValueError):
        ReliableProvider(MockProvider(), fallbacks=[Backup()], fallback_models={"missing": "model"})


def test_extreme_backoff_is_safely_capped() -> None:
    policy = RetryPolicy(
        initial_delay_seconds=1e300,
        max_delay_seconds=10,
        multiplier=1e300,
    )
    assert policy.delay_seconds(80, RateLimitError("429"), 1) == 10
