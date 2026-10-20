# Vector Retrieval

Retrieves documents by cosine similarity over deterministic hash embeddings.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/04_knowledge_and_context/vector_retrieval/run.py
```

The implementation is deterministic and dependency-light. Production systems need appropriate tokenizers, semantic embedding models, durable storage, access control, and privacy policies.
