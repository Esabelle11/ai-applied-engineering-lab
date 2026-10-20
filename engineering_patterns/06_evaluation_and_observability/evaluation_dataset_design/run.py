"""Offline evaluation dataset design demonstration."""

from applied_ai.evaluation import DatasetItem


def main() -> None:
    print(DatasetItem("sentiment-1", "great", "positive"))


if __name__ == "__main__":
    main()
