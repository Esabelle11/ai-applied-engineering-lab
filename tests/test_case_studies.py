"""Case-study replay and CLI contracts."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from applied_ai.core import ConfigurationError
from case_studies.autonomous_debate.run import run as debate
from case_studies.citizen_assist.run import replay as citizen_assist_replay
from case_studies.citizen_assist.run import run as civic
from case_studies.prompt_forge.run import captured_portfolio_analysis
from case_studies.prompt_forge.run import main as prompt_forge_main
from case_studies.prompt_forge.run import run as forge
from case_studies.whybuddy.run import replay as buddy_replay


@pytest.fixture(autouse=True)
def force_mock(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AI_LAB_PROVIDER", "mock")
    monkeypatch.setenv("AI_LAB_MODEL", "mock-model")


def test_prompt_forge_requires_live_model_or_replay() -> None:
    with pytest.raises(ConfigurationError, match="--replay"):
        forge()


def test_prompt_forge_replays_captured_portfolio_linter_output() -> None:
    analysis = captured_portfolio_analysis()
    assert analysis["score"] == 35
    assert "improvedPrompt" in analysis


def test_prompt_forge_can_show_agent_design_without_provider(
    capsys: pytest.CaptureFixture[str],
) -> None:
    prompt_forge_main(["--show-design"])
    shown = capsys.readouterr().out
    assert "Prompt Linter agent instruction" in shown
    assert "Required JSON Schema" in shown


def test_whybuddy_replays_a_storyboard_and_media_plan() -> None:
    lesson = buddy_replay()
    assert lesson.question == "Why do bees make honey?"
    assert len(lesson.images) == 7
    assert lesson.audio.suffix == ".mp3"
    assert lesson.video.suffix == ".mp4"


def test_graph_completes_and_resumes() -> None:
    state = debate()
    assert state.completed
    assert state.history == ("opening", "optimist", "skeptic", "synthesis")
    assert "synthesis" in state.data


def test_citizen_assist_requires_live_model_or_replay() -> None:
    with pytest.raises(ConfigurationError, match="--replay"):
        civic()


def test_citizen_assist_replays_saved_routing_decision() -> None:
    result = citizen_assist_replay()
    assert result.decision.category == "STREETLIGHT"
    assert result.routing_status == "READY_FOR_REVIEW"
    assert result.route is not None
    assert result.route.destination == "public-works/street-lighting"


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
    for slug in ("prompt_forge", "whybuddy", "autonomous_debate", "citizen_assist"):
        result = subprocess.run(
            [sys.executable, "-m", f"case_studies.{slug}.run", "--replay"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
            env=env,
        )
        assert result.returncode == 0, (slug, result.stderr)
