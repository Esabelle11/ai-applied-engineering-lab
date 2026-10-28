# Retry, Deadline, and Fallback — Reliability pattern

## Problem
Transient API failures (429, 5xx, connections, timeouts) must not automatically fail
a request, but infinite retries can multiply cost and latency.

## Mechanism
`ReliableProvider` wraps any `LLMProvider`; underlying adapters remain
**one HTTP request per `generate()` call**. It retries only errors marked
`retryable`, respects `Retry-After`, propagates a remaining-time budget, and
optionally fails over to a *different, explicitly configured* provider.
It never silently ignores structured-output requirements.

## Run offline

```bash
uv run --locked python engineering_patterns/05_reliability_engineering/retry_mechanisms/run.py
```

Expected deterministic results:

```text
Retry: Recovered successfully. | attempts=2
Fallback: Fallback succeeded. | failovers=1
```

## Production use

```python
from applied_ai import ReliableProvider, RetryPolicy

provider = ReliableProvider(
    primary,
    fallbacks=[backup],
    fallback_models={"backup": "backup-model-id"},
    policy=RetryPolicy(max_attempts=3, jitter=True),
    total_timeout_seconds=20,
)
response = provider.generate(request)
print(response.reliability)
```

## Tradeoffs and failure modes
- 401, 403, malformed structured outputs, invalid requests, and model refusals do **not** retry.
- OpenAI honors a per-request transport timeout bounded by remaining total time. A
  custom sync backend must honor `request.timeout_seconds`; the wrapper cannot
  interrupt an arbitrary blocking function, so hard isolation needs an external worker.
- Fallback is opt-in. It cannot guarantee equivalent output quality or model features.
- Retry-After longer than the deadline fails fast rather than ignoring the server.
- `TokenBucketLimiter`, `ConcurrencyLimiter`, and `CircuitBreaker` are process-local.
  Multi-process services need shared coordination; provider-side quotas also apply.
- Do **not** replay tool writes just because an LLM call failed. A basic in-process
  `IdempotencyGuard` exists for educational examples, not distributed exactly-once semantics.

## Validation
See `tests/test_reliability.py` and `tests/test_openai_reliability_http.py`.
The tests inject failures without real API calls, including exhaustion, deadlines,
provider failover, circuit states, side-effect deduplication, and 429 headers.
