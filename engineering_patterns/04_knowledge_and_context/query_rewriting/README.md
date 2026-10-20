# Query Rewriting

Removes common conversational filler while preserving concrete retrieval terms.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/04_knowledge_and_context/query_rewriting/run.py
```

The implementation is deterministic and dependency-light. Production systems need appropriate tokenizers, semantic embedding models, durable storage, access control, and privacy policies.
