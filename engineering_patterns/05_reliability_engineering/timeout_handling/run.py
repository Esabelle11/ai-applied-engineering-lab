"""Enforce a total deadline through the existing reliable provider wrapper."""

from applied_ai import LLMRequest, Message, MockProvider
from applied_ai.reliability import ReliableProvider


def main() -> None:
    provider = ReliableProvider(
        MockProvider(default_text="within deadline"), total_timeout_seconds=1
    )
    print(provider.generate(LLMRequest("mock", (Message("user", "hello"),))).text)


if __name__ == "__main__":
    main()
