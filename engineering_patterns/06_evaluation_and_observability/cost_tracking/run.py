"""Offline cost tracking demonstration."""

from applied_ai import TokenUsage
from applied_ai.evaluation import estimate_cost


def main() -> None:
    print(
        estimate_cost(
            TokenUsage(input_tokens=3, output_tokens=2), input_per_token=0.01, output_per_token=0.02
        )
    )


if __name__ == "__main__":
    main()
