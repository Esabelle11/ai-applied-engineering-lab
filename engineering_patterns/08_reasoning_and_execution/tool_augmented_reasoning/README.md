# Tool Augmented Reasoning

This pattern demonstrates bounded tool augmented reasoning using the shared reasoning SDK.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/08_reasoning_and_execution/tool_augmented_reasoning/run.py
```

Generated code is never executed in the application process; use the isolated sandbox boundary for execution workloads.
