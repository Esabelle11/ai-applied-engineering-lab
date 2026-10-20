"""Optional integration boundary for application services."""

from __future__ import annotations

from collections.abc import Callable


def call_service(service: Callable[..., object], *args: object, **kwargs: object) -> object:
    """Invoke an application service through a deliberately small boundary."""
    if not callable(service):
        raise TypeError("service must be callable")
    return service(*args, **kwargs)
