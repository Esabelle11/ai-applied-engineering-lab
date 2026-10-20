"""Use a narrow, explicitly registered tool boundary from an agent workflow."""

from __future__ import annotations

from applied_ai.orchestration import ToolRegistry


def calculate(expression: str) -> int:
    registry = ToolRegistry()
    registry.register("add", lambda left, right: left + right)
    if expression != "2+2":
        raise ValueError("Demo only supports the explicit expression 2+2")
    return int(registry.invoke("add", left=2, right=2))


def main() -> None:
    print(calculate("2+2"))


if __name__ == "__main__":
    main()
