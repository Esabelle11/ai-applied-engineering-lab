"""Offline example: injected 429 error -> bounded retry -> success, then failover."""

from applied_ai import LLMRequest, Message, MockProvider
from applied_ai.core.exceptions import ProviderUnavailableError, RateLimitError
from applied_ai.reliability import ReliableProvider, RetryPolicy


def main() -> None:
    request = LLMRequest("mock-model", (Message("user", "What is retry backoff?"),))
    flaky = MockProvider(default_text="Recovered successfully.", faults=[RateLimitError("429")])
    resilient = ReliableProvider(
        flaky, policy=RetryPolicy(max_attempts=2, initial_delay_seconds=0, jitter=False)
    )
    response = resilient.generate(request)
    print(f"Retry: {response.text} | attempts={response.reliability.attempts}")

    offline = MockProvider(faults=[ProviderUnavailableError("503")])
    # MockProvider instances have the same name; label them for a demo.

    class NamedMock(MockProvider):
        @property
        def name(self) -> str:
            return "secondary-mock"

    alternative = NamedMock(default_text="Fallback succeeded.")
    failed = ReliableProvider(
        offline,
        fallbacks=[alternative],
        policy=RetryPolicy(max_attempts=1, initial_delay_seconds=0),
    )
    recovered = failed.generate(request)
    print(f"Fallback: {recovered.text} | failovers={recovered.reliability.failovers}")


if __name__ == "__main__":
    main()
