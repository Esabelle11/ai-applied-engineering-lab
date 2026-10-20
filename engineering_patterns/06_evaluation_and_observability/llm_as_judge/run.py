"""Offline llm as judge demonstration."""

from applied_ai.evaluation import judge_response


def main() -> None:
    print(judge_response("A concise answer.", lambda answer: len(answer.split()) <= 4))


if __name__ == "__main__":
    main()
