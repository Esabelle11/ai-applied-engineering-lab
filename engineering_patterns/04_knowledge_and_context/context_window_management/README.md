# Context Window Management

Builds a fixed-size context window and reports exactly which sources were omitted.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/04_knowledge_and_context/context_window_management/run.py
```

The implementation is deterministic and dependency-light. Production systems need appropriate tokenizers, semantic embedding models, durable storage, access control, and privacy policies.
