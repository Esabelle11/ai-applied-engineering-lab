"""Open a circuit after transient failures and reject further calls."""

from applied_ai.reliability import CircuitBreaker


def main() -> None:
    breaker = CircuitBreaker(failure_threshold=1, reset_timeout_seconds=10)
    breaker.before_call()
    breaker.record_failure()
    print(breaker.state)


if __name__ == "__main__":
    main()
