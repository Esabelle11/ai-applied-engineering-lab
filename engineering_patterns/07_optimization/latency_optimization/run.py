"""Offline latency optimization demonstration."""

from applied_ai.optimization import ModelOption, fastest_qualified


def main() -> None:
    print(
        fastest_qualified(
            (ModelOption("fast", 30, 0.02, 0.8), ModelOption("slow", 80, 0.01, 0.9)),
            minimum_quality=0.8,
        ).name
    )


if __name__ == "__main__":
    main()
