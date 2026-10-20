# Retrieval Quality

Calculates labelled precision@k and recall@k for a retrieval result.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/04_knowledge_and_context/retrieval_quality/run.py
```

The implementation is deterministic and dependency-light. Production systems need appropriate tokenizers, semantic embedding models, durable storage, access control, and privacy policies.
