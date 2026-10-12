# math_strategies — controlled experiment

**Question:** Under identical synthetic arithmetic prompts, how do direct answers, tool execution and verification behave?

**Hypothesis (not assumed true):** A bounded independent verification loop or arithmetic tool improves accuracy on some scripted mistakes, but each can also fail.

**Manifest version:** 1.0.0; **unique dataset cases:** 5; **repeat runs:** 5; **seed:** 1234

**Evidence scope:** offline synthetic/fixture results; not evidence of live model quality or production throughput.

## Controlled conditions

- Same five arithmetic questions with independently checked integer answers
- Same synthetic first answer for direct and verification strategies
- Mock model text is fixed by fixture; no API calls
- Tool evaluates only a restricted integer arithmetic AST, never arbitrary Python
- Maximum 2 model calls for verification; other strategies use 1
- Simulated per-model latency 0.020 s and per verification/tool step 0.003/0.004 s

## Results

| Implementation | Completed | Correct | p50 (s) | p95 (s) | Errors | Attempts mean | Tokens known | Cost USD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| arithmetic_tool | 0.800 | 0.600 | 0.024 | 0.024 | 0.200 | 1 | 300 | N/A |
| direct | 1.000 | 0.400 | 0.020 | 0.020 | 0.000 | 1 | 300 | N/A |
| verification_loop | 1.000 | 0.800 | 0.046 | 0.046 | 0.000 | 1.600 | 480 | N/A |

Latency types by implementation:

- `arithmetic_tool`: simulated
- `direct`: simulated
- `verification_loop`: simulated

## Negative results and failures

- `direct` on `math_01`: outcome=completed, correct=False, error=none
- `direct` on `math_03`: outcome=completed, correct=False, error=none
- `arithmetic_tool` on `math_03`: outcome=completed, correct=False, error=none
- `verification_loop` on `math_03`: outcome=completed, correct=False, error=none
- `direct` on `math_04`: outcome=completed, correct=False, error=none
- `arithmetic_tool` on `math_04`: outcome=error, correct=False, error=invalid_tool_expression
- `direct` on `math_01`: outcome=completed, correct=False, error=none
- `direct` on `math_03`: outcome=completed, correct=False, error=none
- `arithmetic_tool` on `math_03`: outcome=completed, correct=False, error=none
- `verification_loop` on `math_03`: outcome=completed, correct=False, error=none
- `direct` on `math_04`: outcome=completed, correct=False, error=none
- `arithmetic_tool` on `math_04`: outcome=error, correct=False, error=invalid_tool_expression
- … 18 additional repeated failures in results.jsonl

## Limitations

- Mock responses are deliberately scripted; results do not measure model intelligence or reasoning ability.
- The local arithmetic interpreter is not the Phase 4 Docker Python sandbox and does not execute model-generated Python.
- Independent verification checks arithmetic, not proof validity or semantic reasoning.
- Corrected answers are synthetic; improvements are a property of these fixtures, not LLM skill.
- Token counts are fixture-defined and are not billed usage; costs are unknown (N/A).
- Repeated runs of the same fixed fixtures are **not independent samples**; do not infer statistical significance.
- Percentiles use linear interpolation over recorded observations. Small samples make tail estimates unstable.
- Token/cost aggregates are reported only for measured or explicitly fixture-defined usage; missing is N/A, not zero.
- Inspect `results.jsonl`, `summary.json`, `metadata.json` and the exact dataset/manifest hashes to reproduce claims.

## Reproduction

`uv run --locked python scripts/run_benchmarks.py --experiment math_strategies`
