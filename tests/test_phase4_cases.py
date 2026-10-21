"""All five case studies run without paid providers or credentials."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from applied_ai.execution import SandboxResult
from case_studies.autonomous_debate.run import run as debate
from case_studies.citizen_assist.run import run as civic
from case_studies.math_reasoning.run import run as math
from case_studies.prompt_forge.run import run as forge
from case_studies.whybuddy.run import run as buddy


@pytest.fixture(autouse=True)
def force_mock(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AI_LAB_PROVIDER", "mock")
    monkeypatch.setenv("AI_LAB_MODEL", "mock-model")


def test_prompt_forge_evaluates_two_templates() -> None:
    assert forge() == {"basic": 1.0, "constrained": 1.0}


def test_whybuddy_uses_task_router() -> None:
    values = buddy()
    assert set(values) == {"quick", "detailed"}
    assert all("[mock/mock-model]" in value for value in values.values())


def test_graph_completes_and_resumes() -> None:
    state = debate()
    assert state.completed
    assert state.history == ("opening", "optimist", "skeptic", "synthesis")
    assert "synthesis" in state.data


def test_retrieval_and_grounding_citations() -> None:
    result = civic()
    assert "city-001" in result.retrieved
    assert result.valid_citations == ("city-001",)
    assert result.unknown_citations == ()


def test_math_verification_without_execution() -> None:
    result = math()
    assert result.verification.accepted
    assert result.sandbox is None


def test_math_sandbox_uses_injected_executor() -> None:
    class FakeSandbox:
        def run(self, code: str) -> SandboxResult:
            assert code == "print(17 * 23 + 9)"
            return SandboxResult("400\n", "", 0)

    result = math(sandbox=FakeSandbox())
    assert result.sandbox_verified is True


def test_math_sandbox_incorrect_result_is_rejected() -> None:
    class FakeSandbox:
        def run(self, _code: str) -> SandboxResult:
            return SandboxResult("401", "", 0)

    assert math(sandbox=FakeSandbox()).sandbox_verified is False


def test_math_sandbox_does_not_use_host_python(monkeypatch: pytest.MonkeyPatch) -> None:
    from applied_ai.execution import DockerPythonSandbox

    def fake_run(command: list[str], **_kwargs: object) -> subprocess.CompletedProcess[bytes]:
        assert command[0] == "docker" and "--network=none" in command
        assert "--cap-drop=ALL" in command and "--read-only" in command
        assert "--pull=never" in command
        return subprocess.CompletedProcess(command, 0, stdout=b"400\n", stderr=b"")

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = DockerPythonSandbox().run("print(400)")
    assert result.stdout.strip() == "400"


def test_each_script_runs_with_python_m(monkeypatch: pytest.MonkeyPatch) -> None:
    root = Path(__file__).resolve().parents[1]
    env = {
        "PATH": str(Path(sys.executable).parent),
        "AI_LAB_PROVIDER": "mock",
        "PYTHONPATH": str(root / "src") + os.pathsep + str(root),
    }
    for key in ("SystemRoot", "WINDIR", "TEMP", "TMP"):
        if key in os.environ:
            env[key] = os.environ[key]
    for slug in (
        "prompt_forge",
        "whybuddy",
        "autonomous_debate",
        "citizen_assist",
        "math_reasoning",
    ):
        result = subprocess.run(
            [sys.executable, "-m", f"case_studies.{slug}.run"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
            env=env,
        )
        assert result.returncode == 0, (slug, result.stderr)
