# Phase 2 — Reliability Foundation (D2)

**Scope:** opt-in synchronous reliability wrapper over Phase 1 provider-neutral API.

## Implemented

- [x] Retryable classifications inherited from `LLMError`: 429, 408/timeout, connection, 409/425, 5xx. Authentication, invalid request, refusal, and malformed output are not retryable.
- [x] Bounded attempts, exponential backoff, jitter, and explicit `Retry-After`.
- [x] Request deadline; remaining budget propagated using new `LLMRequest.timeout_seconds` to the HTTP adapter.
- [x] Optional local token-bucket limiter and concurrency semaphore.
- [x] Explicit fallback chain; structured-output capability verified before each provider.
- [x] Optional circuit breaker with single half-open probe.
- [x] Local response telemetry: total attempts, failovers, elapsed time, error categories. Original response usage and token counts preserved.
- [x] Deterministic failure-injection, HTTP mock, timeout, and idempotent side-effect tests.

## Usage

```python
from applied_ai import LLMRequest, Message, MockProvider, ReliableProvider, RetryPolicy
from applied_ai.core.exceptions import RateLimitError

provider = ReliableProvider(
    MockProvider(default_text="ok", faults=[RateLimitError("rate limited")]),
    policy=RetryPolicy(max_attempts=2, initial_delay_seconds=0),
)
print(provider.generate(LLMRequest("mock", (Message("user", "Hello"),))).text)
```

## Important design boundaries

- Provider adapters have no hidden retry loop; only the explicit wrapper retries.
- `max_attempts` is **total tries per provider**, including the first try.
- HTTP requests can overrun provider/network-level limits by small transport overhead; strict hard-kill deadlines need isolated execution.
- The wrapper can reject late synchronous results but cannot preempt a blocking custom provider; adapters must implement per-attempt timeouts.
- Provider/model fallback must be explicitly enabled (`fallback_models` maps backup provider names to their own model IDs) and may change semantic behavior.
- `RetryExhaustedError.last_error` exposes the final normalized error. Non-retryable errors propagate unchanged.
- `CircuitBreaker` counts retryable failures only; circuit opening can short-circuit an active retry series.
- The rate limiter, breaker, and idempotency guard are **in-process** controls, not globally consistent.
- No automatic retry of tool side effects is implemented; `IdempotencyGuard` demonstrates safe deduplication in one process only.
- Costs are not guessed; actual reported usage stays attached to the successful `LLMResponse`.
- Live smoke test remains explicitly opt-in.

## Development commands

```bash
uv lock
uv sync --locked --group dev --extra openai
uv run --locked pytest -q
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked mypy src
uv run --locked python scripts/validate_patterns.py
uv run --locked python engineering_patterns/05_reliability_engineering/retry_mechanisms/run.py
```

Check GitHub CI after pushing; a local test run alone is not proof that CI has passed.
