# Embedding Generation

Creates deterministic hash embeddings for offline experiments; it is not a semantic embedding model.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/04_knowledge_and_context/embedding_generation/run.py
```

The implementation is deterministic and dependency-light. Production systems need appropriate tokenizers, semantic embedding models, durable storage, access control, and privacy policies.
