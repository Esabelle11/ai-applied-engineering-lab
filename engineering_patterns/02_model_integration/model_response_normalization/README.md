# Model response normalization

Converts a provider payload into the shared `LLMResponse` and `TokenUsage` contracts only after validating observed field types. It keeps provider and model identifiers explicit instead of hiding where a response came from.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/02_model_integration/model_response_normalization/run.py
```

Normalization makes response handling consistent; it does not prove that provider usage or finish reasons are comparable across APIs.
