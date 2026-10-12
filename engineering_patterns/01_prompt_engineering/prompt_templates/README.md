# Prompt Templates — Offline Demonstration

**Goal:** demonstrate deterministic prompt composition independently from any
paid model or provider. This is **not a live LLM call**.

```bash
uv run --offline --locked python engineering_patterns/01_prompt_engineering/prompt_templates/run.py
```

Expected output:

```text
Explain retrieval-augmented generation to a beginner in 2 sentences.
```

## Tradeoffs

Python's `string.Template` is useful for simple placeholders but does not
validate a complete schema or protect against untrusted prompt injection.
Additional prompt orchestration and output-validation patterns are future work.
