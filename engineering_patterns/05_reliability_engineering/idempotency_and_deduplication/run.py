"""Deduplicate a successful side effect using an explicit caller-owned key."""

from applied_ai.reliability import IdempotencyGuard


def main() -> None:
    guard = IdempotencyGuard()
    calls = 0

    def create() -> str:
        nonlocal calls
        calls += 1
        return "created"

    guard.run_once("order-1", create)
    print(guard.run_once("order-1", create), calls)


if __name__ == "__main__":
    main()
