# Public Python SDK API — 0.8.0

Generated from `applied_ai.__all__` using `scripts/generate_api_reference.py`.
Exports listed here are the supported import surface for the current pre-1.0 release.
Other modules are experimental unless explicitly documented.

## Shared request/response

### `LLMRequest`

Defined in [`applied_ai.core.requests`](../src/applied_ai/core/requests.py).

LLMRequest(model: 'str', messages: 'tuple[Message, ...]', max_output_tokens: 'int \| None' = None, temperature: 'float \| None' = None, response_format: 'StructuredOutputSpec \| None' = None, timeout_seconds: 'float \| None' = None)

```python
LLMRequest(model: 'str', messages: 'tuple[Message, ...]', max_output_tokens: 'int | None' = None, temperature: 'float | None' = None, response_format: 'StructuredOutputSpec | None' = None, timeout_seconds: 'float | None' = None) -> None
```

### `LLMResponse`

Defined in [`applied_ai.core.responses`](../src/applied_ai/core/responses.py).

LLMResponse(text: 'str', model: 'str', provider: 'str', request_id: 'str \| None' = None, finish_reason: 'str \| None' = None, usage: 'TokenUsage \| None' = None, latency_seconds: 'float \| None' = None, parsed_output: 'dict[str, Any] \| None' = None, reliability: 'ReliabilityStats \| None' = None)

```python
LLMResponse(text: 'str', model: 'str', provider: 'str', request_id: 'str | None' = None, finish_reason: 'str | None' = None, usage: 'TokenUsage | None' = None, latency_seconds: 'float | None' = None, parsed_output: 'dict[str, Any] | None' = None, reliability: 'ReliabilityStats | None' = None) -> None
```

### `Message`

Defined in [`applied_ai.core.messages`](../src/applied_ai/core/messages.py).

Message(role: 'Role', content: 'str')

```python
Message(role: 'Role', content: 'str') -> None
```

### `ProviderCapabilities`

Defined in [`applied_ai.core.capabilities`](../src/applied_ai/core/capabilities.py).

ProviderCapabilities(synchronous_generation: bool = True, structured_output: bool = False, streaming: bool = False, tools: bool = False)

```python
ProviderCapabilities(synchronous_generation: bool = True, structured_output: bool = False, streaming: bool = False, tools: bool = False) -> None
```

### `StructuredOutputSpec`

Defined in [`applied_ai.core.requests`](../src/applied_ai/core/requests.py).

Object JSON Schema for API-enforced and locally validated JSON output.

```python
StructuredOutputSpec(name: 'str', schema: 'Mapping[str, Any]', strict: 'bool' = True) -> None
```

### `TokenUsage`

Defined in [`applied_ai.core.responses`](../src/applied_ai/core/responses.py).

TokenUsage(input_tokens: 'int \| None' = None, output_tokens: 'int \| None' = None, total_tokens: 'int \| None' = None)

```python
TokenUsage(input_tokens: 'int | None' = None, output_tokens: 'int | None' = None, total_tokens: 'int | None' = None) -> None
```

## Provider abstraction

### `LLMProvider`

Defined in [`applied_ai.core.protocols`](../src/applied_ai/core/protocols.py).

Base class for protocol classes.

```python
LLMProvider(*args, **kwargs)
```

### `MockProvider`

Defined in [`applied_ai.providers.mock`](../src/applied_ai/providers/mock.py).

Return fixed responses and raise scripted errors in call order, without network access.

```python
MockProvider(*, default_text: 'str' = 'Mock response', responses: 'Mapping[str, str] | None' = None, faults: 'Sequence[LLMError]' = (), usage: 'TokenUsage | None' = None, supports_structured_output: 'bool' = True) -> 'None'
```

### `ProviderFactory`

Defined in [`applied_ai.providers.factory`](../src/applied_ai/providers/factory.py).

No public class-level docstring; inspect implementation.

```python
ProviderFactory(*, env: 'Mapping[str, str] | None' = None, dotenv: 'Path | str' = '.env') -> 'None'
```

## Reliability

### `LLMError`

Defined in [`applied_ai.core.exceptions`](../src/applied_ai/core/exceptions.py).

Base error with safe diagnostic metadata for future reliability policies.

```python
LLMError(message: 'str', *, provider: 'str | None' = None, status_code: 'int | None' = None, request_id: 'str | None' = None, retry_after_seconds: 'float | None' = None) -> 'None'
```

### `ReliableProvider`

Defined in [`applied_ai.reliability.provider`](../src/applied_ai/reliability/provider.py).

Opt-in retry/failover decorator; one attempt per underlying provider call.

```python
ReliableProvider(primary: 'LLMProvider', *, fallbacks: 'Sequence[LLMProvider]' = (), fallback_models: 'Mapping[str, str] | None' = None, policy: 'RetryPolicy | None' = None, total_timeout_seconds: 'float' = 30.0, rate_limiter: 'TokenBucketLimiter | None' = None, concurrency_limiter: 'ConcurrencyLimiter | None' = None, circuits: 'Mapping[str, CircuitBreaker] | None' = None, clock: 'Callable[[], float]' = <built-in function monotonic>, sleep: 'Callable[[float], None]' = <built-in function sleep>, random_fraction: 'Callable[[], float]' = <random callable>) -> 'None'
```

### `RetryPolicy`

Defined in [`applied_ai.reliability.policy`](../src/applied_ai/reliability/policy.py).

RetryPolicy(max_attempts: 'int' = 3, initial_delay_seconds: 'float' = 0.25, max_delay_seconds: 'float' = 5.0, multiplier: 'float' = 2.0, jitter: 'bool' = True)

```python
RetryPolicy(max_attempts: 'int' = 3, initial_delay_seconds: 'float' = 0.25, max_delay_seconds: 'float' = 5.0, multiplier: 'float' = 2.0, jitter: 'bool' = True) -> None
```

## Configuration

### `RuntimeConfig`

Defined in [`applied_ai.config`](../src/applied_ai/config.py).

Validated non-secret settings. No .env or API keys are loaded here.

```python
RuntimeConfig(environment: 'str' = 'development', log_level: 'str' = 'INFO', request_timeout_seconds: 'float' = 30.0, max_retries: 'int' = 3) -> None
```

## Minimal offline example

```python
from applied_ai import LLMRequest, Message, MockProvider

response = MockProvider(default_text="Hello!").generate(
    LLMRequest("mock-model", (Message("user", "Hi"),))
)
print(response.text)
```

Live providers require credentials and explicit opt-in in the examples. Availability, JSON-schema support, and models vary by provider.
