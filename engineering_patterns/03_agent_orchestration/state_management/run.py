"""Show immutable state snapshots between agent transitions."""

from __future__ import annotations

from applied_ai.orchestration import Agent, run_agent


def transition(state: dict[str, object]) -> tuple[dict[str, object], dict[str, object]]:
    outcome = run_agent(Agent("add_status", lambda _: {"status": "ready"}), state)
    return state, dict(outcome.state)


def main() -> None:
    initial, next_state = transition({"task": "answer"})
    print(f"initial={initial}; next={next_state}")


if __name__ == "__main__":
    main()
