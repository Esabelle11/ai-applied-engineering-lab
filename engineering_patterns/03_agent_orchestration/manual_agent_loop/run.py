"""Run a caller-controlled agent loop with a finite step budget."""

from __future__ import annotations

from applied_ai.orchestration import LoopDecision, run_manual_loop


def solve_counter(start: int, target: int) -> int:
    def decide(state: object) -> LoopDecision:
        current = state["count"]  # type: ignore[index]
        if current >= target:
            return LoopDecision("finish", {"answer": current}, completed=True)
        return LoopDecision("increment", {"count": current + 1})

    result = run_manual_loop(decide, {"count": start}, max_steps=target - start + 1)
    print("result: ", result)
    if not result.completed:
        raise RuntimeError("Loop did not finish within its budget")
    return int(result.state["answer"])


def main() -> None:
    print(solve_counter(0, 3))


if __name__ == "__main__":
    main()
