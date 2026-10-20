# Streaming responses

Defines a small `TextStreamingProvider` protocol and `StreamChunk` contract. `collect_stream()` rejects out-of-order or unterminated streams, while `MockStreamingProvider` provides a deterministic offline source for tests.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/02_model_integration/streaming_responses/run.py
```

This establishes the streaming contract but does not yet add server-sent-event transport to the live provider adapters. That integration should preserve provider cancellation, timeout, and final usage semantics.
