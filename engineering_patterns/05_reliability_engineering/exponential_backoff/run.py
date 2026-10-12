"""Executable, offline Applied AI handbook pattern."""

from applied_ai.core.exceptions import RateLimitError
from applied_ai.reliability import RetryPolicy


def main() -> None:
    error = RateLimitError("synthetic failure")
    exponential = RetryPolicy(
        initial_delay_seconds=0.5, multiplier=2, max_delay_seconds=3, jitter=False
    )
    constant = RetryPolicy(
        initial_delay_seconds=0.5, multiplier=1, max_delay_seconds=3, jitter=False
    )
    for name, policy in (("fixed", constant), ("exponential", exponential)):
        values = [policy.delay_seconds(i, error, 0.5) for i in range(1, 5)]
        print(f"{name}: {values}")


if __name__ == "__main__":
    main()
