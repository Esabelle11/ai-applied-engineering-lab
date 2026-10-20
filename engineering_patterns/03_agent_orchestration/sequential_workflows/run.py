"""Execute dependent workflow steps in a declared order."""

from __future__ import annotations

from applied_ai.orchestration import Agent, run_sequential


def publish_summary(text: str) -> str:
    summarize = Agent("summarize", lambda state: {"summary": str(state["text"]).split(".")[0]})
    format_result = Agent("format", lambda state: {"published": f"Summary: {state['summary']}"})
    return str(run_sequential((summarize, format_result), {"text": text})[-1].state["published"])


def main() -> None:
    print(publish_summary("RAG retrieves context. It then grounds an answer."))


if __name__ == "__main__":
    main()
