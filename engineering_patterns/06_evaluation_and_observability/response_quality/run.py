"""Executable, offline Applied AI handbook pattern."""

from applied_ai.evaluation import EvalCase, evaluate


def main() -> None:
    cases = [EvalCase("6*7", "42"), EvalCase("2+2", "4"), EvalCase("9-3", "6")]
    answers = {"6*7": "42", "2+2": " 4 ", "9-3": "5"}
    report = evaluate(cases, lambda query: answers[query])
    print(f"Exact match: {report.passed}/{report.total}; accuracy={report.accuracy:.3f}")


if __name__ == "__main__":
    main()
