"""Return a smaller safe result when a recoverable operation fails."""

from applied_ai.reliability import with_degradation


def main() -> None:
    def primary() -> str:
        raise ConnectionError("dependency unavailable")

    print(with_degradation(primary, lambda: "cached summary", recoverable=(ConnectionError,)))


if __name__ == "__main__":
    main()
