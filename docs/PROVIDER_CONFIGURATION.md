# Switching LLM providers from `.env` (Phase 4)

All five case studies share `ProviderFactory`, so selecting a provider never requires modifying their Python source.

1. `cp .env.example .env`
2. Choose **one** `AI_LAB_PROVIDER`; set its `AI_LAB_MODEL` to a real model ID supported by the chosen backend.
3. Add that provider's API key when required. `.env` is gitignored; never commit or paste secrets into issues.
4. Run any case study with `--live` to authorize actual API/network access. Without `--live`, mock is the only permitted provider. Plain tests remain offline.

| `AI_LAB_PROVIDER` | Credential environment key | Sample model ID | Endpoint |
|---|---|---|---|
| `mock` (default) | none | `mock-model` | none |
| `openrouter` | `OPENROUTER_API_KEY` | `nvidia/nemotron-3.5-lightning:free` | OpenRouter chat completions |
| `openai` | `OPENAI_API_KEY` | `gpt-4.1-mini` | OpenAI Responses API (existing Phase 1) |
| `anthropic` | `ANTHROPIC_API_KEY` | `claude-haiku-4-5` | Anthropic Messages API |
| `google` | `GOOGLE_API_KEY` or `GEMINI_API_KEY` | `gemini-3.5-flash` | Gemini generateContent |
| `ollama` | none | `llama3.2` | local `http://127.0.0.1:11434/api/chat` |

Example OpenRouter `.env` **(do not commit an actual key):**

```dotenv
AI_LAB_PROVIDER=openrouter
AI_LAB_MODEL=nvidia/nemotron-3.5-lightning:free
OPENROUTER_API_KEY=replace_with_your_key
APP_REQUEST_TIMEOUT_SECONDS=30
```

```sh
uv sync --group dev --extra providers
uv run python -m case_studies.whybuddy.run --live
```

The free model ID was checked on OpenRouter in October 2026, but **free availability, model routing, quotas, and pricing can change**. Free accounts have limits; an API key is still required. Double-check at [OpenRouter model page](https://openrouter.ai/nvidia/nemotron-3.5-lightning:free) and [pricing](https://openrouter.ai/pricing) before running examples. We do **not** guarantee a model is currently free, available, suitable for tool use, or compatible with structured output. Paid-provider calls can incur charges.

## Capabilities and limitations

- All new adapters expose the existing synchronous `LLMProvider.generate()` contract and normalized `LLMResponse`.
- Token counts are populated only when the provider reports them; do not invent cost data.
- New OpenRouter, Anthropic, Google, and Ollama adapters intentionally declare **no structured-output capability**, because enforced JSON schema is provider/model-specific. Requests containing `response_format` fail with `CapabilityNotSupportedError` rather than silently downgrade.
- Existing `OpenAIProvider` retains its tested structured-output support via OpenAI Responses API.
- Streaming, native async HTTP, multimodal tools, and model-specific JSON schema adaptation are out of scope.
- Existing `ReliableProvider` from Phase 2 can wrap any provider, but is not automatically turned on: retries may consume rate limits or credits. Avoid overlapping retry policies.
- `.env` uses a minimal parser for simple `KEY=value` and quoted values, with environment variables taking precedence. It doesn't support shell interpolation; never run `.env` as a shell script.
- Ollama permits only loopback HTTP URLs for this demo. No remote endpoint or credentials are sent to arbitrary hosts.
- Avoid sending private material or production records into public inference endpoints; review provider data-handling policies yourself.

## Sources

- [OpenRouter chat completions](https://openrouter.ai/docs/api/api-reference/chat/send-chat-completion-request)
- [OpenRouter free model](https://openrouter.ai/nvidia/nemotron-3.5-lightning:free)
- [OpenRouter free-tier limits](https://openrouter.ai/pricing)
- [Anthropic Messages API](https://docs.anthropic.com/en/api/messages)
- [Google generateContent API](https://ai.google.dev/gemini-api/docs/generate-content)
- [Ollama API](https://docs.ollama.com/api)
