# Prompt-injection defense

Separates trusted task instructions from untrusted content, screens for a small set of obvious override phrases, and returns an auditable allow/block decision. Allowed content is enclosed in an explicit data boundary.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/01_prompt_engineering/prompt_injection_defense/run.py
```

The heuristic is deliberately conservative and incomplete. Real systems need layered controls: tool permissions, data isolation, output validation, and adversarial evaluation.
