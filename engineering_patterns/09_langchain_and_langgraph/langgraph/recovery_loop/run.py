"""Offline replay and optional LangGraph validation/recovery loop."""

from __future__ import annotations

import argparse
import json
from typing import Any, TypedDict


def run() -> dict[str, Any]:
    return {"offline": True, "attempts": 2, "value": "valid", "outcome": "ACCEPTED"}


def framework_run() -> dict[str, Any]:
    from langgraph.graph import END, START, StateGraph

    class RecoveryState(TypedDict, total=False):
        attempts: int
        value: str
        outcome: str

    def produce(state: RecoveryState) -> RecoveryState:
        attempt = state.get("attempts", 0) + 1
        return {"attempts": attempt, "value": "valid" if attempt == 2 else "invalid"}

    def validate(state: RecoveryState) -> RecoveryState:
        return {"outcome": "ACCEPTED" if state["value"] == "valid" else "RETRY"}

    # Use a module-resolvable annotation: LangGraph inspects branch callables
    # with get_type_hints(), while RecoveryState is scoped to this demo function.
    def next_step(state: dict[str, Any]) -> str:
        return "produce" if state["outcome"] == "RETRY" and state["attempts"] < 2 else END

    graph = StateGraph(RecoveryState)
    graph.add_node("produce", produce)
    graph.add_node("validate", validate)
    graph.add_edge(START, "produce")
    graph.add_edge("produce", "validate")
    graph.add_conditional_edges("validate", next_step, {"produce": "produce", END: END})
    result = graph.compile().invoke({})
    return {"offline": True, **result}


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--framework", action="store_true")
    args = parser.parse_args(argv)
    print(json.dumps(framework_run() if args.framework else run(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
