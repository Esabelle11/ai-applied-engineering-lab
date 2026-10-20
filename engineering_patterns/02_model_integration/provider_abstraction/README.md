# Provider abstraction

Shows application code depending only on `LLMProvider.generate(LLMRequest)`, with concrete providers registered at composition time. The same `generate_reply()` function works with each registered implementation.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/02_model_integration/provider_abstraction/run.py
```

Provider abstraction normalizes the call boundary, not every capability. Streaming, tools, and multimodal input need explicit capability-aware paths.
