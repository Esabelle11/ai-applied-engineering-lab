from __future__ import annotations

import asyncio

import pytest

from applied_ai.orchestration import (
    Agent,
    ApprovalGate,
    CheckpointStore,
    LoopDecision,
    Plan,
    ToolRegistry,
    choose_route,
    execute_plan,
    handoff,
    merge_outcomes,
    run_manual_loop,
    run_parallel,
    run_sequential,
    run_with_recovery,
)


def test_agent_and_sequential_workflow_keep_prior_state() -> None:
    first = Agent("first", lambda state: {"draft": state["question"]})
    second = Agent("second", lambda state: {"answer": f"ok: {state['draft']}"})
    initial = {"question": "RAG"}
    outcomes = run_sequential((first, second), initial)
    assert outcomes[-1].state["answer"] == "ok: RAG"
    assert initial == {"question": "RAG"}


def test_parallel_merge_rejects_conflicting_updates() -> None:
    agents = (Agent("one", lambda _: {"answer": "one"}), Agent("two", lambda _: {"answer": "two"}))
    outcomes = asyncio.run(run_parallel(agents, {}, max_concurrency=2))
    with pytest.raises(ValueError, match="conflict"):
        merge_outcomes({}, outcomes)


def test_route_handoff_and_checkpoint_are_explicit() -> None:
    assert choose_route({"urgent": True}, (("urgent", lambda state: bool(state["urgent"])), ("normal", lambda _: False))) == "urgent"
    assert handoff("triage", "specialist", {"case": "1"}).to_agent == "specialist"
    store = CheckpointStore()
    store.save("one", {"stage": "review"})
    restored = store.load("one")
    with pytest.raises(TypeError):
        restored["stage"] = "changed"  # type: ignore[index]
    assert store.load("one")["stage"] == "review"


def test_manual_loop_plan_tools_approval_and_recovery() -> None:
    result = run_manual_loop(
        lambda state: LoopDecision("finish", {"answer": state["input"]}, completed=True), {"input": "ok"}
    )
    assert result.completed and result.state["answer"] == "ok"
    assert execute_plan(Plan(("one",)), lambda step, _: {step: "done"}, {})["one"] == "done"

    tools = ToolRegistry()
    tools.register("echo", lambda value: value)
    assert tools.invoke("echo", value="ok") == "ok"
    with pytest.raises(PermissionError):
        tools.invoke("missing")

    gate = ApprovalGate()
    request = gate.request("request", "deploy", {})
    with pytest.raises(ValueError, match="pending"):
        gate.approved(request.request_id)
    gate.decide(request.request_id, True)
    assert gate.approved(request.request_id)

    calls = 0

    def operation() -> str:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise ConnectionError("temporary")
        return "done"

    recovered = run_with_recovery(operation, max_attempts=2, retryable=(ConnectionError,))
    assert (recovered.value, recovered.attempts, recovered.errors) == ("done", 2, ("ConnectionError",))
