"""Offline test fixtures shared by the project."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture
def mock_llm_response() -> dict[str, Any]:
    """A deterministic fixture; no provider calls, credentials or network needed."""
    fixture = Path(__file__).parent / "fixtures" / "mock_responses.json"
    data: dict[str, Any] = json.loads(fixture.read_text(encoding="utf-8"))
    return data
