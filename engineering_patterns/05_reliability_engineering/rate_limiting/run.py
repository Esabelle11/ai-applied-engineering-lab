"""Use a local token bucket before a request is admitted."""

from applied_ai.reliability import TokenBucketLimiter


def main() -> None:
    limiter = TokenBucketLimiter(10, burst=1)
    limiter.acquire()
    print("request admitted")


if __name__ == "__main__":
    main()
