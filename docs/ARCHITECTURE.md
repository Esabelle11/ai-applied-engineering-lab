# Architecture

The nine `engineering_patterns/` categories are **independent** learning and
implementation areas. They are not an execution sequence and do not import
one another. The `src/applied_ai/` package will hold shared reusable interfaces
and utilities. A concrete pattern can import this package; case studies will
later compose several patterns into complete applications.

```text
engineering_patterns/  ->  src/applied_ai/  (when shared code is needed)
       |                       |
       +---- tests/ -----------+
                |
             CI / build
```

## Ownership

- `engineering_patterns`: approachable examples, instructions, alternatives,
  failure modes, and reproducible experiments.
- `src/applied_ai`: importable shared code and stable contracts.
- `tests`: deterministic regression and validation checks.
- `scripts`: development automation and metadata checks.
- `docs`: architecture and accepted technical decisions.

## Components

- Provider protocols and model integration.
- Explicit retry, backoff, timeouts, fallbacks, and rate limiting.
- Runnable patterns across nine categories.
- Case studies from Autonomous Debate, Prompt Forge, WhyBuddy,
  CitizenAssist, and Loop Tool Agent.
- Deterministic tests and validation tooling.

Do not introduce LLM model calls, provider secrets, or untrusted code execution
into the foundation smoke tests.


## Provider-neutral interface

`LLMRequest` holds a model and immutable text messages. An `LLMProvider`
implements `generate(request) -> LLMResponse`. The mock and OpenAI adapter
normalize usage and categorized errors; neither retries implicitly. Structured
output requires `StructuredOutputSpec` and explicit provider capability support.
The SDK does not depend on the executable handbook.

## Opt-in reliability decorator

`ReliableProvider` in `src/applied_ai/reliability/` implements the existing
`LLMProvider` protocol. The provider itself remains single-attempt; the wrapper
adds explicitly bounded retries, deadlines, optional failover, local rate and
concurrency limits, and circuit breaking. The wrapper preserves response usage
and attaches `ReliabilityStats` without logging prompt content.

Provider adapters must honor `LLMRequest.timeout_seconds` to actually interrupt
blocking I/O. The wrapper alone cannot preempt arbitrary synchronous code.
See [architectural decisions](ARCHITECTURAL_DECISIONS.md) for design and risk boundaries.
