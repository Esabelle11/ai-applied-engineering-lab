"""Explicit isolated execution boundary. Never execute model code in-process."""

from applied_ai.execution.docker_sandbox import DockerPythonSandbox, SandboxResult

__all__ = ["DockerPythonSandbox", "SandboxResult"]
