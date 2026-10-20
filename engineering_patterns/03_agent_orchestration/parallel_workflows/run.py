"""Run independent workflow branches concurrently and merge non-conflicting results."""

from __future__ import annotations

import asyncio

from applied_ai.orchestration import Agent, merge_outcomes, run_parallel


async def analyze_in_parallel(question: str) -> dict[str, object]:
    agents = (
        Agent("facts", lambda state: {"facts": f"facts for {state['question']}"}),
        Agent("risks", lambda state: {"risks": f"risks for {state['question']}"}),
    )
    base = {"question": question}
    outcomes = await run_parallel(agents, base, max_concurrency=2)
    return dict(merge_outcomes(base, outcomes))


def main() -> None:
    print(asyncio.run(analyze_in_parallel("Should we cache this response?")))


if __name__ == "__main__":
    main()
