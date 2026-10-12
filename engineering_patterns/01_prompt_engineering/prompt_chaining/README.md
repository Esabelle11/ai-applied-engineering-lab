# Sequential prompt chaining

## Problem and context
Illustrate a reusable prompt engineering engineering capability without paid API calls. The example uses deterministic offline data and the shared `applied_ai` SDK.

## Mechanism and implementation
A series of named prompts passes the previous response to the next template. A strict variable template avoids unrestricted Python format expressions.

## Run offline

```bash
uv run --locked python engineering_patterns/01_prompt_engineering/prompt_chaining/run.py
```

## Alternatives and tradeoffs
Model errors propagate; there are no hidden retries. Earlier hallucinations can contaminate later steps. User-provided variables are not automatically protected against prompt injection.

## Failure modes
Invalid configuration or unsupported capabilities raise exceptions. No hidden network calls, retries or quality guarantees are introduced in these demonstrations. Refer to the runnable tests for the negative paths.

## Validation and comparison
- Contract, success and failure tests: `tests/test_phase3_patterns.py`.
- No measured performance comparison is claimed. Phase 5 will introduce controlled benchmark reports.
- CLI example should run without credentials after project installation.

## Reuse
Uses canonical code in `src/applied_ai/` rather than maintaining duplicate implementation logic in the handbook.
