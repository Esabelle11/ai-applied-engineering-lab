# Execution Failure Recovery

This pattern demonstrates bounded execution failure recovery using the shared reasoning SDK.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/08_reasoning_and_execution/execution_failure_recovery/run.py
```

Generated code is never executed in the application process; use the isolated sandbox boundary for execution workloads.
