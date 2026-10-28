"""Offline replay and optional LangChain implementation of a policy assistant."""

from __future__ import annotations

import argparse
import json
from typing import Any


def run() -> dict[str, Any]:
    return {
        "offline": True,
        "tool": "search_policy",
        "evidence": "Refunds are available within 30 days with proof of purchase.",
        "draft": "Policy result: refunds are available within 30 days with proof of purchase.",
    }


def framework_run() -> dict[str, Any]:
    from langchain_core.runnables import RunnableLambda
    from langchain_core.tools import tool

    @tool
    def search_policy(topic: str) -> str:
        """Look up an approved support policy by topic."""
        policies = {"refund": "Refunds are available within 30 days with proof of purchase."}
        return policies.get(topic.lower(), "No approved policy was found.")

    evidence = search_policy.invoke({"topic": "refund"})
    draft = RunnableLambda(lambda text: f"Policy result: {text.lower()}").invoke(evidence)
    return {"offline": True, "tool": search_policy.name, "evidence": evidence, "draft": draft}


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--framework", action="store_true")
    args = parser.parse_args(argv)
    print(json.dumps(framework_run() if args.framework else run(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
