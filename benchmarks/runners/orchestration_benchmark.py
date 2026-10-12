"""Matched deterministic node logic: Python manual, SDK StateGraph, optional LangGraph."""

from __future__ import annotations

import importlib.util
import json
import time
from pathlib import Path
from typing import Any, TypedDict

from applied_ai.experimentation import ExperimentManifest, Observation
from applied_ai.orchestration import GraphNode, StateGraph


def _prepare(state: dict[str, str]) -> dict[str, str]:
    return {"topic": " ".join(state["topic"].strip().lower().split())}


def _optimist(state: dict[str, str]) -> dict[str, str]:
    return {"pro": f"benefit({state['topic']})"}


def _skeptic(state: dict[str, str]) -> dict[str, str]:
    return {"con": f"risk({state['topic']})"}


def _conclude(state: dict[str, str]) -> dict[str, str]:
    return {"final": f"{state['pro']} / {state['con']}"}


OPERATIONS = ("prepare", "optimist", "skeptic", "conclude")
FN = {"prepare": _prepare, "optimist": _optimist, "skeptic": _skeptic, "conclude": _conclude}


def manual(topic: str) -> str:
    state = {"topic": topic}
    for name in OPERATIONS:
        state.update(FN[name](state))
    return state["final"]


def sdk_graph(topic: str) -> str:
    nodes = {}
    for index, name in enumerate(OPERATIONS):
        nxt = OPERATIONS[index + 1] if index + 1 < len(OPERATIONS) else None

        def node(state: Any, action: str = name, destination: str | None = nxt):
            return FN[action](dict(state)), destination

        nodes[name] = GraphNode(node)
    snapshot = StateGraph(nodes, OPERATIONS[0]).execute({"topic": topic}, max_steps=10)
    if not snapshot.completed or snapshot.history != OPERATIONS:
        raise ValueError("Incomplete SDK graph")
    return snapshot.data["final"]


class DebateState(TypedDict, total=False):
    topic: str
    pro: str
    con: str
    final: str


def langgraph(topic: str) -> str:
    """Uses real optional dependency, not a hand-rolled imitation."""
    from langgraph.graph import END, START  # type: ignore[import-not-found]
    from langgraph.graph import StateGraph as LangStateGraph

    graph = LangStateGraph(DebateState)
    for name in OPERATIONS:

        def node(state: DebateState, action: str = name) -> dict[str, str]:
            return FN[action](dict(state))

        graph.add_node(name, node)
    graph.add_edge(START, OPERATIONS[0])
    for first, second in zip(OPERATIONS[:-1], OPERATIONS[1:], strict=True):
        graph.add_edge(first, second)
    graph.add_edge(OPERATIONS[-1], END)
    return graph.compile().invoke({"topic": topic})["final"]


def run(spec: ExperimentManifest, dataset: Path) -> list[Observation]:
    cases = json.loads(dataset.read_text(encoding="utf-8"))
    strategies = {"manual_python": manual, "sdk_state_graph": sdk_graph, "langgraph": langgraph}
    if set(strategies) != set(spec.implementations):
        raise ValueError("Orchestration manifest strategies mismatch")
    has_langgraph = importlib.util.find_spec("langgraph") is not None
    rows: list[Observation] = []
    for repeat in range(spec.repetitions):
        for case in cases:
            for name in spec.implementations:
                if name == "langgraph" and not has_langgraph:
                    rows.append(
                        Observation(
                            spec.id,
                            case["id"],
                            name,
                            repeat,
                            "unavailable",
                            None,
                            None,
                            "unavailable",
                            note="Install optional benchmark extra to compare real LangGraph",
                        )
                    )
                    continue
                start = time.perf_counter()
                try:
                    result = strategies[name](case["topic"])
                except Exception as exc:
                    rows.append(
                        Observation(
                            spec.id,
                            case["id"],
                            name,
                            repeat,
                            "error",
                            False,
                            time.perf_counter() - start,
                            "observed_wall",
                            error_category=type(exc).__name__,
                        )
                    )
                else:
                    rows.append(
                        Observation(
                            spec.id,
                            case["id"],
                            name,
                            repeat,
                            "completed",
                            result == case["expected"],
                            time.perf_counter() - start,
                            "observed_wall",
                        )
                    )
    return rows
