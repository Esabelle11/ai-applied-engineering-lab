"""Offline cost aware routing demonstration."""

from applied_ai.optimization import ModelOption, cheapest_qualified


def main() -> None:
    print(
        cheapest_qualified(
            (ModelOption("fast", 30, 0.02, 0.8), ModelOption("cheap", 80, 0.01, 0.8)),
            minimum_quality=0.8,
        ).name
    )


if __name__ == "__main__":
    main()
