"""Offline replay and optional LangGraph specialist-routing workflow."""

from __future__ import annotations

import argparse
import json
from typing import Any, TypedDict


def run() -> dict[str, Any]:
    return {
        "offline": True,
        "route": "billing",
        "queue": "billing-review",
        "message": "I was charged twice.",
    }


def framework_run() -> dict[str, Any]:
    from langgraph.graph import END, START, StateGraph

    class Intake(TypedDict, total=False):
        message: str
        route: str
        queue: str

    def classify(state: Intake) -> Intake:
        route = "billing" if "charged" in state["message"].lower() else "technical"
        return {"route": route}

    def billing(_: Intake) -> Intake:
        return {"queue": "billing-review"}

    def technical(_: Intake) -> Intake:
        return {"queue": "technical-review"}

    graph = StateGraph(Intake)
    graph.add_node("classify", classify)
    graph.add_node("billing", billing)
    graph.add_node("technical", technical)
    graph.add_edge(START, "classify")
    graph.add_conditional_edges(
        "classify", lambda state: state["route"], {"billing": "billing", "technical": "technical"}
    )
    graph.add_edge("billing", END)
    graph.add_edge("technical", END)
    result = graph.compile().invoke({"message": "I was charged twice."})
    return {"offline": True, **result}


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--framework", action="store_true")
    args = parser.parse_args(argv)
    print(json.dumps(framework_run() if args.framework else run(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
