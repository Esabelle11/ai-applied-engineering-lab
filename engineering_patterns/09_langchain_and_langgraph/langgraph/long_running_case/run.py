"""Offline replay and optional LangGraph staged case workflow."""

from __future__ import annotations

import argparse
import json
from typing import Any, TypedDict


def run() -> dict[str, Any]:
    return {
        "offline": True,
        "case_id": "case-104",
        "history": ["intake", "research", "review", "follow_up"],
        "outcome": "READY_FOR_FOLLOW_UP",
    }


def framework_run() -> dict[str, Any]:
    from langgraph.graph import END, START, StateGraph

    class CaseState(TypedDict, total=False):
        case_id: str
        history: list[str]
        evidence: str
        outcome: str

    def stage(name: str, update: dict[str, str] | None = None):
        def advance(state: CaseState) -> CaseState:
            return {"history": [*state.get("history", []), name], **(update or {})}

        return advance

    graph = StateGraph(CaseState)
    graph.add_node("intake", stage("intake"))
    graph.add_node("research", stage("research", {"evidence": "approved local record"}))
    graph.add_node("review", stage("review"))
    graph.add_node("follow_up", stage("follow_up", {"outcome": "READY_FOR_FOLLOW_UP"}))
    graph.add_edge(START, "intake")
    graph.add_edge("intake", "research")
    graph.add_edge("research", "review")
    graph.add_edge("review", "follow_up")
    graph.add_edge("follow_up", END)
    result = graph.compile().invoke({"case_id": "case-104"})
    return {"offline": True, **result}


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--framework", action="store_true")
    args = parser.parse_args(argv)
    print(json.dumps(framework_run() if args.framework else run(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
