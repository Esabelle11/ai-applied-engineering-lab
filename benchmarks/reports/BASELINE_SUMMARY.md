# Phase 5: Offline Baseline — Synthetic Fixtures Only

Source: `benchmarks/reports/baseline_offline/`. Reproduce with `python scripts/run_benchmarks.py` after installing the package.

| Study | Outcomes under the fixed synthetic fixtures | Caveat |
|---|---|---|
| Retry | Expected-outcome match: no-retry 3/7; fixed 7/7; exponential 7/7; exp+jitter 7/7 | Virtual times, not production retry effectiveness |
| Debate workflow | Manual Python 4/4 and Lab StateGraph 4/4 correct; LangGraph not installed | Deterministic operations without actual LLMs; cannot rank framework performance |
| Math | Direct 2/5, arithmetic tool 3/5, verify 4/5 correct | Scripted responses, not real reasoning accuracy; no Docker execution |

Five repeats for every fixture are deliberately **not independent observations** and must not be treated as sample size 25–35 in a statistical analysis. In particular, zero benchmark errors does not prove an implementation is fault-free. The deliberately incorrect math proposals and unrecoverable retry scenarios are recorded in the individual raw `results.jsonl` files.

Usage numbers labeled `fixture` are not provider bills. Costs `N/A` mean unknown. Retry times labeled `simulated` are virtual-clock totals. Orchestration timings labeled `observed_wall` are platform-dependent local microbenchmarks that should not be compared across different machines.

See each individual `report.md`, `metadata.json`, `manifest_snapshot.json` and input SHA-256 hashes for full provenance and limitations.
