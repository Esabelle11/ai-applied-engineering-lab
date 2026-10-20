# Text Chunking

Creates bounded, overlapping character chunks so source text is not silently discarded.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/04_knowledge_and_context/text_chunking/run.py
```

The implementation is deterministic and dependency-light. Production systems need appropriate tokenizers, semantic embedding models, durable storage, access control, and privacy policies.
