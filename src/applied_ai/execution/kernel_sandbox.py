"""Trusted-local Jupyter execution and bounded sandbox pooling.

This backend is useful for local agent experiments, but it is not a security
boundary. Use :class:`DockerPythonSandbox` for the repository's stronger,
explicitly isolated execution example.
"""

from __future__ import annotations

import contextlib
import queue
import threading
import time
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class KernelExecutionResult:
    stdout: str
    timed_out: bool = False
    error: str | None = None


class PythonExecutor(Protocol):
    def execute(
        self, source: str, *, timeout_seconds: float | None = None
    ) -> KernelExecutionResult: ...

    def reset(self) -> None: ...

    def close(self) -> None: ...


class LocalKernelSandbox:
    """Stateful Jupyter kernel for trusted local experiments.

    ``jupyter-client`` is imported lazily so the core SDK remains usable when
    the optional local-kernel dependency is not installed.
    """

    def __init__(self, *, timeout_seconds: float = 8.0, preload: Sequence[str] = ()) -> None:
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        try:
            from jupyter_client import KernelManager  # type: ignore[import-not-found]
        except ImportError as exc:
            raise RuntimeError(
                "LocalKernelSandbox requires the optional jupyter-client dependency"
            ) from exc
        self._timeout = timeout_seconds
        self._manager = KernelManager()
        self._manager.start_kernel()
        self._client = self._manager.blocking_client()
        self._client.start_channels()
        self._client.wait_for_ready(timeout=timeout_seconds)
        self._preload = tuple(preload)
        self.reset()

    def execute(
        self, source: str, *, timeout_seconds: float | None = None
    ) -> KernelExecutionResult:
        if not isinstance(source, str) or not source.strip():
            raise ValueError("source must be non-empty text")
        timeout = self._timeout if timeout_seconds is None else timeout_seconds
        if timeout <= 0:
            raise ValueError("timeout_seconds must be positive")
        message_id = self._client.execute(source, allow_stdin=False, stop_on_error=False)
        output: list[str] = []
        errors: list[str] = []
        started = time.monotonic()
        while True:
            if time.monotonic() - started > timeout:
                self._manager.interrupt_kernel()
                return KernelExecutionResult(
                    "", True, f"Execution timed out after {timeout:g} seconds"
                )
            try:
                message = self._client.get_iopub_msg(timeout=0.5)
            except queue.Empty:
                continue
            if message.get("parent_header", {}).get("msg_id") != message_id:
                continue
            content = message.get("content", {})
            message_type = message.get("msg_type")
            if message_type == "stream":
                output.append(content.get("text", ""))
            elif message_type in {"execute_result", "display_data"}:
                text = content.get("data", {}).get("text/plain")
                if text:
                    output.append(f"{text}\n")
            elif message_type == "error":
                errors.extend(content.get("traceback", []))
            elif message_type == "status" and content.get("execution_state") == "idle":
                break
        return KernelExecutionResult("".join(output), error="".join(errors) or None)

    def reset(self) -> None:
        code = "%reset -f\n" + "\n".join(self._preload)
        self.execute(code)

    def close(self) -> None:
        with contextlib.suppress(Exception):
            self._client.stop_channels()
        with contextlib.suppress(Exception):
            self._manager.shutdown_kernel(now=True)
        with contextlib.suppress(Exception):
            self._manager.cleanup_resources()


class SandboxPool:
    """Thread-safe pool that resets an executor whenever it is released."""

    def __init__(self, executors: Sequence[PythonExecutor]) -> None:
        if not executors:
            raise ValueError("At least one executor is required")
        self._available: queue.Queue[PythonExecutor] = queue.Queue()
        self._all = tuple(executors)
        for executor in self._all:
            self._available.put(executor)
        self._closed = False
        self._lock = threading.Lock()

    @contextlib.contextmanager
    def lease(self, *, timeout_seconds: float = 10.0) -> Iterator[PythonExecutor]:
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        with self._lock:
            if self._closed:
                raise RuntimeError("SandboxPool is closed")
        try:
            executor = self._available.get(timeout=timeout_seconds)
        except queue.Empty as exc:
            raise TimeoutError("No sandbox became available before the deadline") from exc
        try:
            yield executor
        finally:
            with contextlib.suppress(Exception):
                executor.reset()
            self._available.put(executor)

    def close(self) -> None:
        with self._lock:
            if self._closed:
                return
            self._closed = True
        for executor in self._all:
            with contextlib.suppress(Exception):
                executor.close()

    def __enter__(self) -> SandboxPool:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
