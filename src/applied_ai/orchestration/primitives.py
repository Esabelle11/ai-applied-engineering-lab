"""Small, deterministic orchestration primitives used by handbook patterns.

These utilities intentionally avoid hidden LLM calls, persistence, and side
effects. Applications supply agent functions and decide how to persist state.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

State = Mapping[str, Any]
AgentFunction = Callable[[State], Mapping[str, Any]]


def _frozen_state(state: Mapping[str, Any]) -> Mapping[str, Any]:
    return MappingProxyType(dict(state))


@dataclass(frozen=True, slots=True)
class Agent:
    name: str
    run: AgentFunction

    def __post_init__(self) -> None:
        if not self.name.strip() or not callable(self.run):
            raise ValueError("Agent needs a non-empty name and callable run function")


@dataclass(frozen=True, slots=True)
class AgentOutcome:
    agent: str
    state: Mapping[str, Any]

    def __post_init__(self) -> None:
        object.__setattr__(self, "state", _frozen_state(self.state))


def run_agent(agent: Agent, state: State) -> AgentOutcome:
    """Run one agent and merge its mapping of updates into a fresh state snapshot."""
    updates = agent.run(_frozen_state(state))
    if not isinstance(updates, Mapping) or not all(isinstance(key, str) for key in updates):
        raise TypeError("Agent updates must be a mapping with string keys")
    next_state = dict(state)
    next_state.update(updates)
    return AgentOutcome(agent.name, next_state)


def run_sequential(agents: Sequence[Agent], state: State) -> tuple[AgentOutcome, ...]:
    """Run agents in order; each one receives all prior updates."""
    if not agents:
        raise ValueError("At least one agent is required")
    outcomes: list[AgentOutcome] = []
    current: State = state
    for agent in agents:
        outcome = run_agent(agent, current)
        outcomes.append(outcome)
        current = outcome.state

    return tuple(outcomes)


async def run_parallel(
    agents: Sequence[Agent], state: State, *, max_concurrency: int = 3
) -> tuple[AgentOutcome, ...]:
    """Run independent agents concurrently; outcomes do not merge conflicting updates."""
    if not agents or max_concurrency < 1:
        raise ValueError("Agents must be present and max_concurrency must be positive")
    gate = asyncio.Semaphore(max_concurrency)

    async def execute(agent: Agent) -> AgentOutcome:
        async with gate:
            return await asyncio.to_thread(run_agent, agent, state)

    return tuple(await asyncio.gather(*(execute(agent) for agent in agents)))


def merge_outcomes(base: State, outcomes: Sequence[AgentOutcome]) -> Mapping[str, Any]:
    """Merge independent outcomes only when they do not write the same key differently."""
    merged = dict(base)
    written: dict[str, Any] = {}
    for outcome in outcomes:
        for key, value in outcome.state.items():
            if key in base:
                continue
            if key in written and written[key] != value:
                raise ValueError(f"Parallel agents conflict on state key: {key}")
            written[key] = value
            merged[key] = value
    return _frozen_state(merged)


def choose_route(state: State, routes: Sequence[tuple[str, Callable[[State], bool]]]) -> str:
    """Select exactly one explicit route, failing closed for none or multiple matches."""
    matches = [name for name, predicate in routes if predicate(_frozen_state(state))]
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one matching route; got {matches}")
    return matches[0]


@dataclass(frozen=True, slots=True)
class Handoff:
    from_agent: str
    to_agent: str
    state: Mapping[str, Any]

    def __post_init__(self) -> None:
        if (
            not self.from_agent.strip()
            or not self.to_agent.strip()
            or self.from_agent == self.to_agent
        ):
            raise ValueError("Handoff requires distinct, non-empty agent names")
        object.__setattr__(self, "state", _frozen_state(self.state))


def handoff(from_agent: str, to_agent: str, state: State) -> Handoff:
    return Handoff(from_agent, to_agent, state)


class CheckpointStore:
    """In-memory checkpoint storage keyed by caller-provided IDs."""

    def __init__(self) -> None:
        self._checkpoints: dict[str, Mapping[str, Any]] = {}

    def save(self, checkpoint_id: str, state: State) -> None:
        if not checkpoint_id.strip():
            raise ValueError("checkpoint_id must be non-empty")
        self._checkpoints[checkpoint_id] = _frozen_state(state)

    def load(self, checkpoint_id: str) -> Mapping[str, Any]:
        try:
            return _frozen_state(self._checkpoints[checkpoint_id])
        except KeyError as exc:
            raise KeyError(f"Unknown checkpoint: {checkpoint_id}") from exc


@dataclass(frozen=True, slots=True)
class ApprovalRequest:
    request_id: str
    action: str
    state: Mapping[str, Any]

    def __post_init__(self) -> None:
        if not self.request_id.strip() or not self.action.strip():
            raise ValueError("Approval request ID and action must be non-empty")
        object.__setattr__(self, "state", _frozen_state(self.state))


class ApprovalGate:
    def __init__(self) -> None:
        self._decisions: dict[str, bool] = {}

    def request(self, request_id: str, action: str, state: State) -> ApprovalRequest:
        if request_id in self._decisions:
            raise ValueError(f"Approval already decided: {request_id}")
        return ApprovalRequest(request_id, action, state)

    def decide(self, request_id: str, approved: bool) -> None:
        if request_id in self._decisions:
            raise ValueError(f"Approval already decided: {request_id}")
        self._decisions[request_id] = approved

    def approved(self, request_id: str) -> bool:
        if request_id not in self._decisions:
            raise ValueError(f"Approval pending: {request_id}")
        return self._decisions[request_id]


@dataclass(frozen=True, slots=True)
class LoopDecision:
    action: str
    updates: Mapping[str, Any]
    completed: bool = False

    def __post_init__(self) -> None:
        if not self.action.strip() or not isinstance(self.updates, Mapping):
            raise ValueError("Loop decision needs an action and updates mapping")


@dataclass(frozen=True, slots=True)
class LoopResult:
    state: Mapping[str, Any]
    actions: tuple[str, ...]
    completed: bool

    def __post_init__(self) -> None:
        object.__setattr__(self, "state", _frozen_state(self.state))


def run_manual_loop(
    decide: Callable[[State], LoopDecision], state: State, *, max_steps: int = 5
) -> LoopResult:
    if max_steps < 1:
        raise ValueError("max_steps must be positive")
    current = dict(state)
    actions: list[str] = []
    for _ in range(max_steps):
        decision = decide(_frozen_state(current))
        current.update(decision.updates)
        actions.append(decision.action)
        if decision.completed:
            return LoopResult(current, tuple(actions), True)
    return LoopResult(current, tuple(actions), False)


@dataclass(frozen=True, slots=True)
class Plan:
    steps: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.steps or any(not step.strip() for step in self.steps):
            raise ValueError("Plan requires one or more non-empty steps")


def execute_plan(
    plan: Plan, executor: Callable[[str, State], Mapping[str, Any]], state: State
) -> Mapping[str, Any]:
    """Execute a caller-owned plan step by step and return the resulting state."""
    current = dict(state)
    for step in plan.steps:
        updates = executor(step, _frozen_state(current))
        if not isinstance(updates, Mapping):
            raise TypeError("Plan executor must return a mapping")
        current.update(updates)
    return _frozen_state(current)


class ToolRegistry:
    """Explicitly registered synchronous tools for orchestrated workflows."""

    def __init__(self) -> None:
        self._tools: dict[str, Callable[..., Any]] = {}

    def register(self, name: str, tool: Callable[..., Any]) -> None:
        if not name.isidentifier() or not callable(tool) or name in self._tools:
            raise ValueError("Tools need a unique identifier and callable")
        self._tools[name] = tool

    def invoke(self, name: str, /, **arguments: Any) -> Any:
        try:
            return self._tools[name](**arguments)
        except KeyError as exc:
            raise PermissionError(f"Tool is not registered: {name}") from exc


@dataclass(frozen=True, slots=True)
class RecoveryResult:
    value: Any
    attempts: int
    errors: tuple[str, ...]


def run_with_recovery(
    operation: Callable[[], Any],
    *,
    max_attempts: int = 2,
    retryable: tuple[type[Exception], ...] = (Exception,),
) -> RecoveryResult:
    """Retry a caller-owned operation a bounded number of times and retain error types."""
    if max_attempts < 1 or not retryable:
        raise ValueError("max_attempts and retryable exceptions are required")
    errors: list[str] = []
    for attempt in range(1, max_attempts + 1):
        try:
            return RecoveryResult(operation(), attempt, tuple(errors))
        except retryable as exc:
            errors.append(type(exc).__name__)
            if attempt == max_attempts:
                raise
    raise AssertionError("unreachable")
