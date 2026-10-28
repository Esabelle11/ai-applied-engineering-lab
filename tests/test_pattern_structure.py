"""Check that handbook scaffolding and examples exist."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_nine_documented_categories_exist() -> None:
    categories = sorted((ROOT / "engineering_patterns").glob("[0-9][0-9]_*"))
    assert len(categories) == 9
    assert all((category / "README.md").is_file() for category in categories)


def test_shared_template_is_complete() -> None:
    template = ROOT / "engineering_patterns" / "_template"
    for name in ("README.md", "pattern.yaml", "config.example.yaml", "run.py"):
        assert (template / name).is_file()


def test_offline_example_is_present() -> None:
    pattern = ROOT / "engineering_patterns" / "01_prompt_engineering" / "prompt_templates"
    assert (pattern / "README.md").is_file()
    assert (pattern / "pattern.yaml").is_file()
    assert (pattern / "run.py").is_file()


def test_offline_example_runs_without_keys() -> None:
    import subprocess
    import sys

    result = subprocess.run(
        [
            sys.executable,
            str(
                ROOT
                / "engineering_patterns"
                / "01_prompt_engineering"
                / "prompt_templates"
                / "run.py"
            ),
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.stdout.strip() == (
        "Explain retrieval-augmented generation to a beginner in 2 sentences."
    )
