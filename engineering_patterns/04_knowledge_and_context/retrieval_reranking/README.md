# Retrieval Reranking

Reranks candidates by explicit query-term overlap with stable tie-breaking.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/04_knowledge_and_context/retrieval_reranking/run.py
```

The implementation is deterministic and dependency-light. Production systems need appropriate tokenizers, semantic embedding models, durable storage, access control, and privacy policies.
