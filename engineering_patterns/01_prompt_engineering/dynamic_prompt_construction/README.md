# Dynamic prompt construction

Builds a prompt from named, prioritized context sections under a fixed character budget. `DynamicPrompt` records both included and omitted section names, so context loss is visible instead of silent.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/01_prompt_engineering/dynamic_prompt_construction/run.py
```

This demonstrates character budgeting, not model-token counting. A production integration should use the target model's tokenizer.
