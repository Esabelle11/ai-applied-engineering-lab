"""Concurrent sync-provider execution using worker threads, not native async inference."""

from __future__ import annotations

import asyncio
from collections.abc import Sequence

from applied_ai.core.protocols import LLMProvider
from applied_ai.core.requests import LLMRequest
from applied_ai.core.responses import LLMResponse


async def generate_concurrently(
    provider: LLMProvider, requests: Sequence[LLMRequest], *, max_concurrency: int = 2
) -> list[LLMResponse]:
    """Execute synchronous calls concurrently (caller must ensure provider thread safety)."""
    if max_concurrency < 1:
        raise ValueError("max_concurrency must be positive")
    gate = asyncio.Semaphore(max_concurrency)

    async def one(request: LLMRequest) -> LLMResponse:
        async with gate:
            return await asyncio.to_thread(provider.generate, request)

    return list(await asyncio.gather(*(one(request) for request in requests)))
