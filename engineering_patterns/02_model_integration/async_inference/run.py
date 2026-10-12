"""Executable, offline Applied AI handbook pattern."""

import asyncio

from applied_ai import LLMRequest, Message, MockProvider
from applied_ai.inference import generate_concurrently


async def demo() -> None:
    provider = MockProvider(responses={"First": "A", "Second": "B"})
    requests = [LLMRequest("mock", (Message("user", prompt),)) for prompt in ("First", "Second")]
    results = await generate_concurrently(provider, requests, max_concurrency=2)
    print([result.text for result in results])


if __name__ == "__main__":
    asyncio.run(demo())
