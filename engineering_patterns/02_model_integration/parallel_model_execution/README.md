# Parallel model execution

Executes independent synchronous provider calls through bounded worker threads and returns results in the original call order. It makes concurrency a caller-specified limit rather than an accidental side effect.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/02_model_integration/parallel_model_execution/run.py
```

Providers must be thread-safe before they are used here. Parallel calls can increase rate-limit pressure and cost.
