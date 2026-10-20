"""Calculate deterministic full jitter for a retry delay."""

from applied_ai.reliability import full_jitter


def main() -> None:
    print(full_jitter(4.0, 0.25))


if __name__ == "__main__":
    main()
