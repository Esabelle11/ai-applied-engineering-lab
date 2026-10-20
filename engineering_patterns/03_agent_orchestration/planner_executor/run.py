"""Separate a declared plan from deterministic step execution."""

from __future__ import annotations

from applied_ai.orchestration import Plan, execute_plan


def execute_research_plan(question: str) -> str:
    plan = Plan(("retrieve", "compose"))

    def executor(step: str, state: object) -> dict[str, str]:
        if step == "retrieve":
            return {"sources": f"sources for {state['question']}"}  # type: ignore[index]
        if step == "compose":
            return {"answer": f"Answer using {state['sources']}"}  # type: ignore[index]
        raise ValueError(f"Unknown plan step: {step}")

    return str(execute_plan(plan, executor, {"question": question})["answer"])


def main() -> None:
    print(execute_research_plan("What is retrieval?"))


if __name__ == "__main__":
    main()
