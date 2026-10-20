"""Offline quality cost tradeoffs demonstration."""

from applied_ai.optimization import ModelOption, pareto_frontier


def main() -> None:
    print(
        [
            option.name
            for option in pareto_frontier(
                (
                    ModelOption("cheap", 50, 0.01, 0.7),
                    ModelOption("better", 70, 0.02, 0.9),
                    ModelOption("bad", 60, 0.03, 0.6),
                )
            )
        ]
    )


if __name__ == "__main__":
    main()
