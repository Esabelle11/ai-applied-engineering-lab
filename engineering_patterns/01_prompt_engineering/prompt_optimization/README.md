# Prompt optimization

Compares explicit `PromptCandidate` values using a caller-supplied quality score and an explicit length penalty. It returns every score and the winning prompt, avoiding hidden optimizer behavior.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/01_prompt_engineering/prompt_optimization/run.py
```

The quality scorer is the important part of a real optimization loop: it should come from held-out evaluation cases, not a subjective one-off judgment.
