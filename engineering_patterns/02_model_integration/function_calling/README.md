# Function calling

Defines an allowlisted `ToolSpec`, validates model-supplied JSON arguments against its schema, and invokes only the matching registered callable. Unknown tool names and invalid arguments fail before execution.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/02_model_integration/function_calling/run.py
```

This is the execution boundary after a provider has produced a tool call. It does not grant a model arbitrary process, network, or filesystem access.
