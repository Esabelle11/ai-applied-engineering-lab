"""Route a real stateful handoff from triage to a billing specialist."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from applied_ai.orchestration import Handoff, handoff

State = Mapping[str, Any]
Specialist = Callable[[State], str]


def billing_specialist(state: State) -> str:
    """Handle the state that triage transferred to the billing team."""
    question = state["question"]
    return f"Billing specialist received the case and will investigate: {question}"


def data_specialist(state: State) -> str:
    """Handle the state that triage transferred to the billing team."""
    question = state["question"]
    return f"Data Specialist received: {question}"


SPECIALISTS: dict[str, Specialist] = {
    "billing_specialist": billing_specialist,
    "data_specialist": data_specialist,
}


def dispatch(transfer: Handoff) -> str:
    """Invoke the receiving agent named by the handoff."""
    try:
        specialist = SPECIALISTS[transfer.to_agent]
    except KeyError as exc:
        raise RuntimeError(f"No agent registered for {transfer.to_agent!r}") from exc
    print(f"[handoff] {transfer.from_agent} -> {transfer.to_agent}")
    print(f"[handoff state] {dict(transfer.state)}")
    return specialist(transfer.state)


def escalate_to_specialist(question: str) -> str:
    transfer = handoff("triage", "billing_specialist", {"question": question, "reason": "billing"})
    return dispatch(transfer)


def escalate_to_data_specialist(question: str) -> str:
    transfer = handoff(
        "document", "data_specialist", {"question": question, "reason": "data null issue"}
    )
    return dispatch(transfer)


def main() -> None:
    print(escalate_to_specialist("Why was I charged twice?"))
    print("=" * 20)
    print(escalate_to_data_specialist("The customer field is null"))


if __name__ == "__main__":
    main()
