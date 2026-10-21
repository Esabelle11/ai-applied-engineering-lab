"""Run independent provider calls concurrently while preserving input order."""

from __future__ import annotations

import asyncio
from collections.abc import Sequence
from dataclasses import dataclass

from applied_ai import LLMRequest, LLMResponse
from applied_ai.core.protocols import LLMProvider


@dataclass(frozen=True, slots=True)
class ModelCall:
    provider: LLMProvider
    request: LLMRequest


async def execute_parallel(
    calls: Sequence[ModelCall], *, max_concurrency: int = 3
) -> list[LLMResponse]:
    """Use bounded worker threads for existing synchronous providers; do not assume thread safety."""
    if not calls or max_concurrency < 1:
        raise ValueError("calls must be non-empty and max_concurrency must be positive")
    gate = asyncio.Semaphore(max_concurrency)

    async def execute(call: ModelCall) -> LLMResponse:
        async with gate:
            return await asyncio.to_thread(call.provider.generate, call.request)

    return list(await asyncio.gather(*(execute(call) for call in calls)))


def main() -> None:
    from applied_ai import Message, MockProvider

    calls = (
        ModelCall(
            MockProvider(default_text="fast"),
            LLMRequest("mock-fast", (Message("user", "Summarize"),)),
        ),
        ModelCall(
            MockProvider(default_text="careful"),
            LLMRequest("mock-careful", (Message("user", "Analyze"),)),
        ),
    )
    print([response.text for response in asyncio.run(execute_parallel(calls, max_concurrency=2))])


if __name__ == "__main__":
    main()
