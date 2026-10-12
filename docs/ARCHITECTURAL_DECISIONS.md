# Architectural Decision Records (ADRs)

These are scoped design records for the first release candidate. Propose changes using a pull request with benchmarks and migration notes.

## ADR-001 — Eight independent handbook modules
**Decision:** Categories `01` through `08` describe reusable engineering disciplines, **not** sequential runtime phases. Patterns can compose SDK utilities across categories. **Reason:** prevents application-oriented duplicate implementations. **Tradeoff:** some features appear in more than one category conceptually; cross-reference instead of duplicating code.

## ADR-002 — SDK below examples
**Decision:** `engineering_patterns/`, `case_studies/`, benchmarks and browser UI depend on `src/applied_ai/`. The SDK must not import example scripts, web handlers, or benchmark runners. **Reason:** examples can be dropped without breaking Python integrations.

## ADR-003 — Explicit provider capabilities and authorization
**Decision:** a shared synchronous `generate()` contract, normalized exceptions, and explicit capability rejection; optional live provider use requires `--live` or playground opt-in. **Tradeoff:** native async and streaming are not claimed by the base protocol. Models and tools differ across providers.

## ADR-004 — Reliability is a wrapper, not implicit retries
**Decision:** Phase 2's `ReliableProvider` adds bounded retry, deadline, throttling, failover and other policies on demand. **Reason:** avoid surprise duplicate retries and preserve a deterministic base adapter.

## ADR-005 — Simulations are not external-model benchmarks
**Decision:** offline comparisons use controlled fixtures, deterministic fault sequences, and documented virtual timing. Real LangGraph and live LLM probes are separate opt-in paths. **Reason:** synthetic success rates are not production model accuracy measurements.

## ADR-006 — Generated code never runs in the playground process
**Decision:** the playground has a fixed example registry and no arbitrary code-execution endpoint. Math sandboxing is an optional separate Docker CLI path with disabled networking, resource restrictions and explicit operator opt-in. **Limit:** Docker execution is **not** a sufficiently reviewed boundary for hostile public submissions.

## ADR-007 — Release gates before tags
**Decision:** the repository may provide candidate bundles before a tag, but a release tag is created only after the genuine lockfile, a green supported-version CI matrix, dependency and secret scanning, and a recorded security review. **Reason:** prevents publishing "release-ready" labels without verification.
