# Prompt evaluation

Runs a prompt builder against labelled test cases through the common provider interface and reports passed cases, failures, and accuracy. The offline example uses `MockProvider`, so it is repeatable without API credentials.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/01_prompt_engineering/prompt_evaluation/run.py
```

Exact-match evaluation is useful for deterministic tasks but is not a general measure of factuality, safety, or response quality.
