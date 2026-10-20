"""Offline agent evaluation demonstration."""

from applied_ai.evaluation import DatasetItem, score_dataset


def main() -> None:
    print(score_dataset((DatasetItem("a", "2+2", "4"),), lambda _: "4"))


if __name__ == "__main__":
    main()
