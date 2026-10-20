# Long Term Memory

Stores explicit facts in an in-memory lexical retrieval store without hidden persistence.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/04_knowledge_and_context/long_term_memory/run.py
```

The implementation is deterministic and dependency-light. Production systems need appropriate tokenizers, semantic embedding models, durable storage, access control, and privacy policies.
