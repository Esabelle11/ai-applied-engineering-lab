"""Offline replay and optional LangChain bounded tool loop."""

from __future__ import annotations

import argparse
import json
from typing import Any


def run() -> dict[str, Any]:
    return {"offline": True, "steps": [6, 7], "answer": "6 + 7 = 13", "max_steps": 2}


def framework_run() -> dict[str, Any]:
    from langchain_core.runnables import RunnableLambda
    from langchain_core.tools import tool

    @tool
    def add(left: int, right: int) -> int:
        """Add two approved integer values."""
        return left + right

    calls = ((1, 5), (2, 5))
    results = [add.invoke({"left": left, "right": right}) for left, right in calls]
    answer = RunnableLambda(lambda values: f"{values[0]} + {values[1]} = {sum(values)}").invoke(
        results
    )
    return {"offline": True, "steps": results, "answer": answer, "max_steps": len(calls)}


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--framework", action="store_true")
    args = parser.parse_args(argv)
    print(json.dumps(framework_run() if args.framework else run(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
