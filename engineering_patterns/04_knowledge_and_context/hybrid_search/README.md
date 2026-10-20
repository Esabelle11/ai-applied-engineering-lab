# Hybrid Search

Fuses lexical and vector rankings using deterministic reciprocal-rank fusion.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/04_knowledge_and_context/hybrid_search/run.py
```

The implementation is deterministic and dependency-light. Production systems need appropriate tokenizers, semantic embedding models, durable storage, access control, and privacy policies.
