"""Retry a transient provider failure through the shared reliability wrapper."""

from applied_ai import LLMRequest, Message, MockProvider
from applied_ai.core.exceptions import ProviderUnavailableError
from applied_ai.reliability import ReliableProvider, RetryPolicy


def main() -> None:
    provider = ReliableProvider(
        MockProvider(default_text="recovered", faults=(ProviderUnavailableError("temporary"),)),
        policy=RetryPolicy(max_attempts=2, initial_delay_seconds=0),
    )
    print(provider.generate(LLMRequest("mock", (Message("user", "hello"),))).text)


if __name__ == "__main__":
    main()
