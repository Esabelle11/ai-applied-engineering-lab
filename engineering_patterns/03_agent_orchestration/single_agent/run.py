"""Run one bounded agent against an immutable input state."""

from __future__ import annotations

from applied_ai.orchestration import Agent, run_agent


def build_research_agent() -> Agent:
    def research(state: object) -> dict[str, str]:
        question = state["question"]  # type: ignore[index]
        return {"answer": f"Research result for: {question}"}

    return Agent("research", research)


def main() -> None:
    result = run_agent(build_research_agent(), {"question": "What is RAG?"})
    print(result.state["answer"])


if __name__ == "__main__":
    main()
