"""Privacy-conscious in-process request event collection."""

from __future__ import annotations

from dataclasses import dataclass
from time import monotonic


@dataclass(frozen=True, slots=True)
class RequestEvent:
    provider: str
    model: str
    elapsed_seconds: float
    success: bool
    error_category: str | None = None


class EventRecorder:
    def __init__(self) -> None:
        self._events: list[RequestEvent] = []

    def record(self, event: RequestEvent) -> None:
        if event.elapsed_seconds < 0:
            raise ValueError("elapsed_seconds cannot be negative")
        self._events.append(event)

    def record_call(self, provider: str, model: str, operation: object) -> object:
        """Record a completed callable operation without storing its payload."""
        started = monotonic()
        try:
            result = operation() if callable(operation) else operation
        except Exception as exc:
            self.record(
                RequestEvent(provider, model, monotonic() - started, False, type(exc).__name__)
            )
            raise
        else:
            self.record(RequestEvent(provider, model, monotonic() - started, True))
            return result

    def snapshot(self) -> tuple[RequestEvent, ...]:
        return tuple(self._events)
