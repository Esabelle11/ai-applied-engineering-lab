"""Offline tests for version consistency, deterministic documentation, and release gates."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_script(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / (name + ".py"))
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_release_versions_match_and_files_exist() -> None:
    checker = load_script("release_check")
    assert checker.declared_version(ROOT) == "0.8.0"
    assert checker.validate(ROOT, require_lock=False) == []


def test_strict_release_check_requires_real_lockfile() -> None:
    checker = load_script("release_check")
    if not (ROOT / "uv.lock").exists():
        assert any("uv.lock" in item for item in checker.validate(ROOT, require_lock=True))


def test_api_reference_reproducible() -> None:
    api = load_script("generate_api_reference")
    assert api.generate() == (ROOT / "docs" / "API_REFERENCE.md").read_text(encoding="utf-8")
    assert "MockProvider" in api.generate()


def test_catalog_reproducible_and_complete() -> None:
    catalog = load_script("generate_catalog")
    result = catalog.generate()
    assert result == (ROOT / "docs" / "PATTERN_CATALOG.md").read_text(encoding="utf-8")
    assert result.count("| `") >= 14


def test_secret_regex_detects_example_realistic_formats() -> None:
    audit = load_script("security_static_check")
    candidate = "sk-" + "proj-" + "A" * 24
    assert "openai-token" in audit.scan_text(candidate)
    assert not audit.scan_text("OPENAI_API_KEY=your_api_key")


def test_scanner_catches_forbidden_env_file(tmp_path: Path) -> None:
    audit = load_script("security_static_check")
    (tmp_path / ".env").write_text("DUMMY=1", encoding="utf-8")
    assert "environment file" in " ".join(audit.scan_tree(tmp_path))


def test_scanner_ignores_example_env(tmp_path: Path) -> None:
    audit = load_script("security_static_check")
    (tmp_path / ".env.example").write_text("DUMMY=placeholder", encoding="utf-8")
    assert audit.scan_tree(tmp_path) == []
