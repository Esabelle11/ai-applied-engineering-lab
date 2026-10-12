# orchestration_comparison — controlled experiment

**Question:** Do manual Python, the Lab StateGraph, and real LangGraph preserve identical deterministic outputs?

**Hypothesis (not assumed true):** All implementations preserve the same data flow for matched four-node tasks, with different framework overhead.

**Manifest version:** 1.0.0; **unique dataset cases:** 4; **repeat runs:** 5; **seed:** 1234

**Evidence scope:** offline synthetic/fixture results; not evidence of live model quality or production throughput.

## Controlled conditions

- Same topic fixtures and four deterministic shared node functions
- Sequential node execution and no actual LLM calls
- Concurrency=1; repeated identical cases
- Measured local wall time is workload/platform dependent
- LangGraph only runs if the optional official package is installed

## Results

| Implementation | Completed | Correct | p50 (s) | p95 (s) | Errors | Attempts mean | Tokens known | Cost USD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| langgraph | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| manual_python | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | N/A | N/A | N/A |
| sdk_state_graph | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | N/A | N/A | N/A |

Latency types by implementation:

- `langgraph`: unavailable
- `manual_python`: observed_wall
- `sdk_state_graph`: observed_wall

## Negative results and failures

- None observed in these fixture cases; this does not establish general reliability.

## Limitations

- All steps are deterministic mocked agent functions, not full LLM agent quality or coordination.
- Repeated microbenchmark wall-clock times are not statistically significant or portable across machines.
- LangGraph is genuinely optional; without installation it is unavailable, never silently replaced by the SDK graph.
- No checkpoint persistence, model calls, tool latency, or agent concurrency are studied.
- Repeated runs of the same fixed fixtures are **not independent samples**; do not infer statistical significance.
- Percentiles use linear interpolation over recorded observations. Small samples make tail estimates unstable.
- Token/cost aggregates are reported only for measured or explicitly fixture-defined usage; missing is N/A, not zero.
- Inspect `results.jsonl`, `summary.json`, `metadata.json` and the exact dataset/manifest hashes to reproduce claims.

## Reproduction

`uv run --locked python scripts/run_benchmarks.py --experiment orchestration_comparison`
