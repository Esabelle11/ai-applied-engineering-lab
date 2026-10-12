# Changelog

## [0.8.0] — Phase 7 release candidate (2026-10-12)

- Established pre-1.0 public API, compatibility policy, and explicit architectural decision records.
- Added deterministic generators for the pattern catalog and public SDK API reference.
- Added release metadata checks, offline secret-pattern checks, tests and contribution templates.
- Extended GitHub CI matrix documentation checks; configured dependency/secret scanning and tag verification workflows.
- Documented unresolved sandbox/public-hosting security risks, the release gate and a manual tag/runbook.
- **Not yet a tagged release:** a genuine `uv.lock`, green GitHub CI and external security scan are still required.

## [0.7.0] — Phase 6 (2026-10-12)

- Added localhost-only interactive playground with handbook discovery, curated examples, comparisons and evidence viewer.
- Added optional playground extra, bearer-token checks, local quotas and live opt-in controls.
- Preserved SDK and offline CLI flows; no arbitrary code execution endpoint.

## [0.6.0] — Phase 5

- Added deterministic retry, orchestration and arithmetic experiments with synthetic datasets and provenance hashes.
- Added optional real LangGraph and live provider probes, clearly separated from synthetic findings.

## [0.5.0] — Phase 4

- Five SDK-composed reference case studies and `.env`-selected mock/OpenRouter/OpenAI/Anthropic/Google/Ollama providers.
- Opt-in Docker Python math sandbox, disabled in browser.

## [0.4.0] — Phase 3

- Published offline examples across all eight engineering categories, supported by shared SDK patterns.

## [0.3.0] — Phase 2

- Added reliability wrapper for bounded retry/backoff, deadlines, fallback, rate limits and circuit protection.

## [0.2.0] — Phase 1

- Added provider-neutral generation contracts, mock and OpenAI adapter, structured-output handling, error normalization and tests.

## [0.1.0] — Phase 0

- Added installable project scaffold, eight categories, reusable pattern template and offline testing foundation.
