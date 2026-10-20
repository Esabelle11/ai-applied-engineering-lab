# Conversation Memory

Uses bounded in-memory recent-message context through the shared memory SDK.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/04_knowledge_and_context/conversation_memory/run.py
```

The implementation is deterministic and dependency-light. Production systems need appropriate tokenizers, semantic embedding models, durable storage, access control, and privacy policies.
