"""Offline latency benchmarking demonstration."""

from applied_ai.evaluation import benchmark


def main() -> None:
    print(benchmark(lambda: sum(range(10))))


if __name__ == "__main__":
    main()
