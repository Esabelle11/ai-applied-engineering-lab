# Multimodal input

Defines validated text and image parts, then serializes them to an explicit OpenAI-compatible content payload. Image references are limited to HTTPS URLs or data URLs, and image detail is constrained to known values.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/02_model_integration/multimodal_input/run.py
```

The current core provider contract remains text-only. This pattern prepares and validates the payload boundary; a provider adapter must explicitly implement multimodal transport before it can send the payload.
