"""Require a durable explicit approval decision before a sensitive action."""

from __future__ import annotations

from applied_ai.orchestration import ApprovalGate


def request_then_apply(approved: bool) -> str:
    gate = ApprovalGate()
    request = gate.request(
        "deploy-1", "deploy production configuration", {"environment": "production"}
    )
    gate.decide(request.request_id, approved)
    return "applied" if gate.approved(request.request_id) else "rejected"


def main() -> None:
    print(request_then_apply(True))


if __name__ == "__main__":
    main()
