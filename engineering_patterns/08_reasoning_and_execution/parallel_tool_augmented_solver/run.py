"""Offline demonstration of parallel tool-use loops and consensus."""

from __future__ import annotations

from applied_ai.execution import SandboxPool
from applied_ai.reasoning import ModelTurn, ToolCall, ToolLoop, majority_consensus


class Calculator:
    def execute(self, value: int) -> str:
        return str(value * 7)

    def reset(self) -> None:
        pass

    def close(self) -> None:
        pass


def solve(attempt: int, pool: SandboxPool) -> str:
    calculator = pool.lease()
    with calculator as leased:

        def model(messages):
            if len(messages) == 1:
                proposed = 6 if attempt != 2 else 5
                return ModelTurn(tool_calls=(ToolCall("calculate", {"value": proposed}),))
            return ModelTurn(f"verified:{messages[-1].content}")

        result = ToolLoop(model, {"calculate": lambda args: leased.execute(args["value"])}).run(
            "Compute the answer and verify it with the calculator."
        )
        return result.answer or "no-answer"


def main() -> None:
    with SandboxPool((Calculator(), Calculator())) as pool:
        answers = tuple(solve(index, pool) for index in range(3))
    print("Attempts:", answers)
    print("Consensus:", majority_consensus(answers).answer)


if __name__ == "__main__":
    main()
