"""Offline token optimization demonstration."""

from applied_ai.optimization import estimate_tokens


def main() -> None:
    print(estimate_tokens("Use fewer prompt tokens."))


if __name__ == "__main__":
    main()
