# Prompt versioning

Stores immutable named prompt versions and requires an explicit activation step before rendering. `PromptRegistry` prevents accidental overwrite of a published version and reuses the SDK's strict `PromptTemplate` renderer.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/01_prompt_engineering/prompt_versioning/run.py
```

The registry is intentionally in-memory. Production deployments should persist versions, review changes, and associate evaluations with the selected version.
