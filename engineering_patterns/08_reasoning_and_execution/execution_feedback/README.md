# Execution Feedback

This pattern demonstrates bounded execution feedback using the shared reasoning SDK.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/08_reasoning_and_execution/execution_feedback/run.py
```

Generated code is never executed in the application process; use the isolated sandbox boundary for execution workloads.
