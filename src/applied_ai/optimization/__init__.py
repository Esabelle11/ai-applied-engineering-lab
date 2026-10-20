"""Explicit in-process response cache, with hashed request keys and optional TTL."""

from __future__ import annotations

import hashlib
import json
import math
import time
from collections.abc import Callable
from dataclasses import dataclass

from applied_ai.core.capabilities import ProviderCapabilities
from applied_ai.core.protocols import LLMProvider
from applied_ai.core.requests import LLMRequest
from applied_ai.core.responses import LLMResponse


@dataclass(frozen=True, slots=True)
class CacheResult:
    response: LLMResponse
    hit: bool


class CachingProvider:
    """Process-local opt-in cache. No cross-user sharing, locking, or persistent storage."""

    def __init__(
        self,
        provider: LLMProvider,
        *,
        ttl_seconds: float = 60.0,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if not math.isfinite(ttl_seconds) or ttl_seconds <= 0:
            raise ValueError("TTL must be positive")
        self.provider = provider
        self.ttl_seconds = ttl_seconds
        self._clock = clock
        self._entries: dict[str, tuple[float, LLMResponse]] = {}

    @property
    def name(self) -> str:
        return self.provider.name

    @property
    def capabilities(self) -> ProviderCapabilities:
        return self.provider.capabilities

    @staticmethod
    def _key(request: LLMRequest) -> str:
        obj = {
            "model": request.model,
            "messages": [(m.role, m.content) for m in request.messages],
            "temperature": request.temperature,
            "max_output_tokens": request.max_output_tokens,
            "response_format": None
            if request.response_format is None
            else {
                "name": request.response_format.name,
                "strict": request.response_format.strict,
                "schema": dict(request.response_format.schema),
            },
        }
        encoded = json.dumps(obj, sort_keys=True, default=str).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def generate_with_cache_info(self, request: LLMRequest) -> CacheResult:
        key = self._key(request)
        now = self._clock()
        cached = self._entries.get(key)
        if cached is not None and cached[0] > now:
            return CacheResult(cached[1], True)
        result = self.provider.generate(request)
        self._entries[key] = (self._clock() + self.ttl_seconds, result)
        return CacheResult(result, False)

    def generate(self, request: LLMRequest) -> LLMResponse:
        return self.generate_with_cache_info(request).response


from applied_ai.optimization.primitives import (  # noqa: E402, F401
    ModelOption,
    SemanticCache,
    batch_items,
    bounded_map,
    cheapest_qualified,
    compress_text,
    estimate_tokens,
    fastest_qualified,
    pareto_frontier,
)
