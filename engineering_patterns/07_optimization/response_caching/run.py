"""Executable, offline Applied AI handbook pattern."""

from applied_ai import LLMRequest, Message, MockProvider
from applied_ai.optimization import CachingProvider


def main() -> None:
    backend = MockProvider(default_text="Cached answer")
    provider = CachingProvider(backend, ttl_seconds=60)
    request = LLMRequest("mock", (Message("user", "Explain caching"),))
    first = provider.generate_with_cache_info(request)
    second = provider.generate_with_cache_info(request)
    print(f"first_hit={first.hit}, second_hit={second.hit}, underlying_calls={backend.call_count}")


if __name__ == "__main__":
    main()
