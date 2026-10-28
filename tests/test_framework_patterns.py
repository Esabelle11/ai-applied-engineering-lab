"""Offline contracts for the optional LangChain and LangGraph handbook examples."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = (
    "langchain/controlled_tool_loop",
    "langchain/provider_neutral_rag",
    "langchain/simple_tool_assistant",
    "langgraph/human_approval_gate",
    "langgraph/long_running_case",
    "langgraph/recovery_loop",
    "langgraph/specialist_routing",
)


@pytest.mark.parametrize("pattern", PATTERNS)
def test_framework_patterns_have_a_no_dependency_replay(pattern: str) -> None:
    path = ROOT / "engineering_patterns/09_langchain_and_langgraph" / pattern / "run.py"
    spec = importlib.util.spec_from_file_location(pattern.replace("/", "_"), path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    result = module.run()
    assert result["offline"] is True
