# Phase 5 — D5 Implementation and Acceptance

**Goal:** Replace anecdotal "it works" claims with controlled, reproducible offline findings and separately disclosed live observations.

| Required item | Implemented evidence |
|---|---|
| Versioned experiment manifests | `experiments/configs/*.json`, validated by `load_manifest` |
| Representative synthetic datasets | `benchmarks/datasets/*.json` |
| Matched retry fault sequences | `benchmarks/runners/retry_benchmark.py` |
| Manual / SDK / real framework orchestration | `benchmarks/runners/orchestration_benchmark.py`; real LangGraph optional and unavailable when absent |
| Math: direct / tool / verify | `benchmarks/runners/math_benchmark.py` (restricted arithmetic interpreter, not Docker) |
| Accuracy, latency p50/p95, error rates | `src/applied_ai/experimentation/core.py` |
| Known usage/attempts and missing cost | Per-observation JSONL, summary, report; missing usage and cost reported N/A |
| Metadata and versioned input hashes | `metadata.json`, `manifest_snapshot.json`, dataset SHA-256 |
| Both positive and negative results | `report.md` and raw `results.jsonl` for each experiment |
| Live-provider variability | `scripts/run_live_benchmark.py` and explicit limitations in `benchmarks/README.md` |
| Offline test and reproduction | `tests/test_phase5_benchmarks.py`, `scripts/run_benchmarks.py` |

**Local offline verification for this artifact:** 152 tests passed; 1 opt-in live test skipped; handbook validated. Three benchmark suites ran and generated full evidence bundles. LangGraph and external provider tests were *not* run. Ruff/mypy and GitHub CI require a contributor environment with development dependencies installed.

**Not yet established:** a live-vs-live provider ranking; LangGraph performance baseline; real Docker sandbox comparative data; estimates of actual model response costs; statistically significant findings on any population of production requests.

## Baseline interpretation

- Retry: fixed, exponential and exponential+jitter matched all expected fixture recovery/failure outcomes; no-retry matched 3/7. Important: only 5/7 scenarios expect a successful response. A correct fail-fast result should not be conflated with completion rate.
- Orchestration: manual Python and SDK graph matched all four tiny reference tasks; LangGraph unavailable during the baseline, *not measured*.
- Math: direct 2/5, arithmetic tool 3/5, verification loop 4/5 for the curated fixtures. The tool refused the unsafe expression, and a scripted correction still failed on one case. These are NOT estimates of live LLM mathematical accuracy.

To finalize D5 independently, run lint/format/type checks and GitHub CI, then run the real LangGraph experiment using the optional extra. If you also run the opt-in live probe, publish it as a separate observational report with provider/model/date/settings and uncontrolled factors.
