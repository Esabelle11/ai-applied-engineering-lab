"""Choose exactly one workflow branch from explicit predicates."""

from __future__ import annotations

from applied_ai.orchestration import choose_route


def route_ticket(priority: str) -> str:
    return choose_route(
        {"priority": priority},
        (
            ("urgent_queue", lambda state: state["priority"] == "urgent"),
            ("standard_queue", lambda state: state["priority"] == "standard"),
        ),
    )


def main() -> None:
    print(route_ticket("urgent"))


if __name__ == "__main__":
    main()
