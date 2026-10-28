"""Offline replay and optional LangGraph human-review boundary."""

from __future__ import annotations

import argparse
import json
from typing import Any, TypedDict


def run() -> dict[str, Any]:
    return {
        "offline": True,
        "draft": "Request a refund for duplicate charge.",
        "outcome": "AWAITING_HUMAN_REVIEW",
    }


def framework_run() -> dict[str, Any]:
    from langgraph.graph import END, START, StateGraph

    class ReviewState(TypedDict, total=False):
        request: str
        draft: str
        approved: bool
        outcome: str

    def draft(state: ReviewState) -> ReviewState:
        return {"draft": f"Draft response: {state['request']}"}

    def review(state: ReviewState) -> ReviewState:
        outcome = (
            "APPROVED_FOR_EXTERNAL_ACTION" if state.get("approved") else "AWAITING_HUMAN_REVIEW"
        )
        return {"outcome": outcome}

    graph = StateGraph(ReviewState)
    graph.add_node("draft", draft)
    graph.add_node("review", review)
    graph.add_edge(START, "draft")
    graph.add_edge("draft", "review")
    graph.add_edge("review", END)
    result = graph.compile().invoke({"request": "Request a refund for duplicate charge."})
    return {"offline": True, **result}


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--framework", action="store_true")
    args = parser.parse_args(argv)
    print(json.dumps(framework_run() if args.framework else run(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
