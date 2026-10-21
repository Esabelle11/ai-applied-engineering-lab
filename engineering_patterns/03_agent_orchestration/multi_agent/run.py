"""Compose specialized agents with an explicit shared state hand-off."""

from __future__ import annotations

from applied_ai.orchestration import Agent, run_sequential


def run_research_and_review(question: str) -> str:
    researcher = Agent("researcher", lambda state: {"draft": f"Draft: {state['question']}"})
    reviewer = Agent("reviewer", lambda state: {"answer": f"Reviewed {state['draft']}"})
    outcomes = run_sequential((researcher, reviewer), {"question": question})
    print("outcomes: ", outcomes)
    return str(outcomes[-1].state["answer"])


def main() -> None:
    print(run_research_and_review("Explain retrieval"))


if __name__ == "__main__":
    main()
