"""Classify normalized failures into retry policy inputs."""

from applied_ai.core.exceptions import RateLimitError
from applied_ai.reliability import classify_error


def main() -> None:
    print(classify_error(RateLimitError("slow down")))


if __name__ == "__main__":
    main()
