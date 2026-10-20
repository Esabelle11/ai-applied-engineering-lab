# Local model inference

Uses the existing Ollama adapter behind the common `LLMProvider` contract. The default is an offline `MockProvider`; a local HTTP server is contacted only when a caller explicitly requests live mode.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/02_model_integration/local_model_inference/run.py
```

A production caller should set a model ID, time budget, and explicit local-server policy. Local hosting does not itself make inference private or safe.
