"""Offline token usage tracking demonstration."""

from applied_ai import TokenUsage
from applied_ai.evaluation import token_total


def main() -> None:
    print(token_total(TokenUsage(input_tokens=3, output_tokens=2, total_tokens=5)))


if __name__ == "__main__":
    main()
