"""Opt-in Docker isolation for untrusted Python, not a cloud multi-tenant security boundary.

Requires an administratively provisioned Docker daemon and pre-pulled image.
"""

from __future__ import annotations

import contextlib
import os
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class SandboxResult:
    stdout: str
    stderr: str
    exit_code: int
    timed_out: bool = False


class DockerPythonSandbox:
    def __init__(self, *, image: str = "python:3.12-slim", timeout_seconds: float = 8.0) -> None:
        if not 0 < timeout_seconds <= 60:
            raise ValueError("timeout_seconds must be within (0,60]")
        if not image or any(ch.isspace() for ch in image) or image.startswith("-"):
            raise ValueError("Invalid Docker image identifier")
        self.image = image
        self.timeout_seconds = timeout_seconds

    def run(self, source: str) -> SandboxResult:
        if not isinstance(source, str) or len(source.encode("utf-8")) > 16_384:
            raise ValueError("Source must be text <= 16 KiB")
        # Docker daemon must be trusted and configured by the administrator.
        # The container receives no credentials, no network, and a read-only root filesystem.
        with tempfile.TemporaryDirectory(prefix="ai-lab-sandbox-") as tmp:
            script = Path(tmp) / "main.py"
            script.write_text(source, encoding="utf-8")
            script.chmod(0o644)
            cid = Path(tmp) / "container.cid"
            command = [
                "docker",
                "run",
                "--rm",
                "--pull=never",
                "--network=none",
                "--read-only",
                f"--cidfile={cid}",
                "--cap-drop=ALL",
                "--security-opt=no-new-privileges",
                "--pids-limit=32",
                "--memory=128m",
                "--cpus=0.5",
                "--user=65534:65534",
                "--tmpfs=/tmp:rw,noexec,nosuid,nodev,size=8m",
                f"--mount=type=bind,source={script.resolve()},target=/work/main.py,readonly",
                "--workdir=/tmp",
                self.image,
                "python",
                "-I",
                "-B",
                "/work/main.py",
            ]
            try:
                completed = subprocess.run(
                    command,
                    capture_output=True,
                    timeout=self.timeout_seconds,
                    check=False,
                    env={"PATH": os.environ.get("PATH", "")},
                )
            except subprocess.TimeoutExpired:
                # The Docker client can time out while its container survives: forcibly
                # remove the container if the daemon managed to create a CID file.
                if cid.exists():
                    container_id = cid.read_text(encoding="utf-8").strip()
                    if container_id:
                        with contextlib.suppress(subprocess.TimeoutExpired, OSError):
                            subprocess.run(
                                ["docker", "rm", "-f", container_id],
                                timeout=3,
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL,
                                check=False,
                                env={"PATH": os.environ.get("PATH", "")},
                            )
                return SandboxResult("", "Sandbox deadline exceeded", 124, timed_out=True)
            except FileNotFoundError as exc:
                raise RuntimeError(
                    "Docker CLI unavailable; install Docker and pre-pull image"
                ) from exc
            return SandboxResult(
                completed.stdout[:8192].decode("utf-8", errors="replace"),
                completed.stderr[:8192].decode("utf-8", errors="replace"),
                completed.returncode,
            )
