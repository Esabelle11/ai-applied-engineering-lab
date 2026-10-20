"""Small deterministic graph with bounded steps and resumable in-memory snapshots."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from types import MappingProxyType

from applied_ai.orchestration.primitives import (
    Agent,
    AgentOutcome,
    ApprovalGate,
    ApprovalRequest,
    CheckpointStore,
    Handoff,
    LoopDecision,
    LoopResult,
    Plan,
    RecoveryResult,
    ToolRegistry,
    choose_route,
    execute_plan,
    handoff,
    merge_outcomes,
    run_agent,
    run_manual_loop,
    run_parallel,
    run_sequential,
    run_with_recovery,
)

__all__ = [
    "Agent",
    "AgentOutcome",
    "ApprovalGate",
    "ApprovalRequest",
    "CheckpointStore",
    "GraphNode",
    "GraphSnapshot",
    "Handoff",
    "LoopDecision",
    "LoopResult",
    "Plan",
    "RecoveryResult",
    "StateGraph",
    "ToolRegistry",
    "choose_route",
    "execute_plan",
    "handoff",
    "merge_outcomes",
    "run_agent",
    "run_manual_loop",
    "run_parallel",
    "run_sequential",
    "run_with_recovery",
]


@dataclass(frozen=True, slots=True)
class GraphSnapshot:
    next_node: str | None
    data: Mapping[str, str]
    history: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "data", MappingProxyType(dict(self.data)))

    @property
    def completed(self) -> bool:
        return self.next_node is None


@dataclass(frozen=True, slots=True)
class GraphNode:
    """Return a fresh mapping of updates and a next-node identifier or None."""

    run: Callable[[Mapping[str, str]], tuple[Mapping[str, str], str | None]]


class StateGraph:
    def __init__(self, nodes: Mapping[str, GraphNode], start: str) -> None:
        if not nodes or start not in nodes:
            raise ValueError("Start node must exist")
        self._nodes = dict(nodes)
        self.start = start

    def execute(
        self, state: Mapping[str, str] | GraphSnapshot, *, max_steps: int = 10
    ) -> GraphSnapshot:
        if max_steps < 1:
            raise ValueError("max_steps must be positive")
        snapshot = (
            state if isinstance(state, GraphSnapshot) else GraphSnapshot(self.start, dict(state))
        )
        current = snapshot.next_node
        data = dict(snapshot.data)
        history = list(snapshot.history)
        for _ in range(max_steps):
            if current is None:
                break
            if current not in self._nodes:
                raise ValueError(f"Unknown graph destination: {current}")
            updates, next_node = self._nodes[current].run(dict(data))
            # print("updates:", updates)
            # print("next_node:", next_node)
            if not all(isinstance(k, str) and isinstance(v, str) for k, v in updates.items()):
                raise TypeError("Graph state updates must map strings to strings")
            if next_node is not None and next_node not in self._nodes:
                raise ValueError(f"Unknown graph destination: {next_node}")
            data.update(updates)
            history.append(current)
            current = next_node
        return GraphSnapshot(current, data, tuple(history))
