# Changelog

## [0.8.0] — Release candidate (2026-10-12)

- Established pre-1.0 public API, compatibility policy, and explicit architectural decision records.
- Added deterministic generators for the pattern catalog and public SDK API reference.
- Added release metadata checks, offline secret-pattern checks, tests and contribution templates.
- Extended GitHub CI matrix documentation checks; configured dependency/secret scanning and tag verification workflows.
- Documented unresolved sandbox/public-hosting security risks, the release gate and a manual tag/runbook.
- **Not yet a tagged release:** a genuine `uv.lock`, green GitHub CI and external security scan are still required.

## [0.7.0] — Interactive playground (2026-10-12)

- Added localhost-only interactive playground with handbook discovery, curated examples, and comparisons.
- Added optional playground extra, bearer-token checks, local quotas and live opt-in controls.
- Preserved SDK and offline CLI flows; no arbitrary code execution endpoint.

## [0.5.0] — Case studies

- Five SDK-composed reference case studies and `.env`-selected mock/OpenRouter/OpenAI/Anthropic/Google/Ollama providers.
- Opt-in Docker Python execution example, disabled in the browser.

## [0.4.0] — Engineering patterns

- Published offline examples across all eight engineering categories, supported by shared SDK patterns.

## [0.3.0] — Reliability foundation

- Added reliability wrapper for bounded retry/backoff, deadlines, fallback, rate limits and circuit protection.

## [0.2.0] — Core SDK

- Added provider-neutral generation contracts, mock and OpenAI adapter, structured-output handling, error normalization and tests.

## [0.1.0] — Foundation

- Added installable project scaffold, eight categories, reusable pattern template and offline testing foundation.
