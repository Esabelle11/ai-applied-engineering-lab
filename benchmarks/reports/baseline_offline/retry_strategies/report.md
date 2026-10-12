# retry_strategies — controlled experiment

**Question:** Which bounded retry policy recovers from the same synthetic failure sequences?

**Hypothesis (not assumed true):** Backoff-enabled policies recover more transient cases than single attempts, at the cost of higher simulated delay.

**Manifest version:** 1.0.0; **unique dataset cases:** 7; **repeat runs:** 5; **seed:** 1234

**Evidence scope:** offline synthetic/fixture results; not evidence of live model quality or production throughput.

## Controlled conditions

- Same ordered transient and permanent faults for every strategy
- Identical MockProvider request and token fixtures
- One simulated provider call takes 0.020 seconds
- No real sleeping; deterministic virtual clock
- Max attempts: 1 for no_retry and 3 for other strategies
- Deterministic jitter fraction 0.5; fixed/exponential begin at 0.1 s
- Identical Retry-After constraints

## Results

| Implementation | Completed | Correct | p50 (s) | p95 (s) | Errors | Attempts mean | Tokens known | Cost USD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| exponential | 0.714 | 1.000 | 0.360 | 0.440 | 0.286 | 2.143 | 500 | N/A |
| exponential_jitter | 0.714 | 1.000 | 0.210 | 0.440 | 0.286 | 2.143 | 500 | N/A |
| fixed | 0.714 | 1.000 | 0.260 | 0.440 | 0.286 | 2.143 | 500 | N/A |
| no_retry | 0.143 | 0.429 | 0.020 | 0.020 | 0.857 | 1 | 100 | N/A |

Latency types by implementation:

- `exponential`: simulated
- `exponential_jitter`: simulated
- `fixed`: simulated
- `no_retry`: simulated

## Negative results and failures

- `no_retry` on `rate_limit_once`: outcome=error, correct=False, error=retry_exhausted
- `no_retry` on `service_unavailable_twice`: outcome=error, correct=False, error=retry_exhausted
- `no_retry` on `timeout_twice`: outcome=error, correct=False, error=retry_exhausted
- `no_retry` on `retry_after_once`: outcome=error, correct=False, error=retry_exhausted
- `no_retry` on `authentication_denied`: outcome=error, correct=True, error=authentication
- `fixed` on `authentication_denied`: outcome=error, correct=True, error=authentication
- `exponential` on `authentication_denied`: outcome=error, correct=True, error=authentication
- `exponential_jitter` on `authentication_denied`: outcome=error, correct=True, error=authentication
- `no_retry` on `service_persistently_down`: outcome=error, correct=True, error=retry_exhausted
- `fixed` on `service_persistently_down`: outcome=error, correct=True, error=retry_exhausted
- `exponential` on `service_persistently_down`: outcome=error, correct=True, error=retry_exhausted
- `exponential_jitter` on `service_persistently_down`: outcome=error, correct=True, error=retry_exhausted
- … 48 additional repeated failures in results.jsonl

## Limitations

- Latency is virtual clock time, NOT actual network or backend latency.
- NoRetry has a different max_attempts by design; only the other three compare delay strategies at the same limit.
- Expected failure is scored correct only when the fixture expects an error; this is not model answer accuracy.
- Fixed fixtures cannot establish real-world optimal delay settings or provider availability.
- Repeated runs of the same fixed fixtures are **not independent samples**; do not infer statistical significance.
- Percentiles use linear interpolation over recorded observations. Small samples make tail estimates unstable.
- Token/cost aggregates are reported only for measured or explicitly fixture-defined usage; missing is N/A, not zero.
- Inspect `results.jsonl`, `summary.json`, `metadata.json` and the exact dataset/manifest hashes to reproduce claims.

## Reproduction

`uv run --locked python scripts/run_benchmarks.py --experiment retry_strategies`
