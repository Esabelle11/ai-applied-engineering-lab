# Document Ingestion

Validates external ID/text records before they enter a retrieval index.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/04_knowledge_and_context/document_ingestion/run.py
```

The implementation is deterministic and dependency-light. Production systems need appropriate tokenizers, semantic embedding models, durable storage, access control, and privacy policies.
