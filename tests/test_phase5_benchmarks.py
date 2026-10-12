"""Phase 5 evidence validity, deterministic controls and AST security boundaries."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from applied_ai.experimentation import Observation, aggregate, load_manifest, write_artifacts
from applied_ai.providers.mock import MockProvider
from benchmarks.runners import math_benchmark, orchestration_benchmark, retry_benchmark
from benchmarks.runners.math_benchmark import UnsupportedExpression, arithmetic
from scripts.run_live_benchmark import probe

ROOT = Path(__file__).resolve().parents[1]


def spec(name: str):  # noqa: ANN201
    return load_manifest(ROOT / "experiments/configs" / f"{name}.json", ROOT)


def test_retry_benchmark_same_fault_sequences_and_deterministic() -> None:
    manifest, dataset = spec("retry_strategies")
    first = retry_benchmark.run(manifest, dataset)
    second = retry_benchmark.run(manifest, dataset)
    assert first == second
    assert len(first) == 7 * 4 * 5
    result = aggregate(first)
    assert result["no_retry"]["correct_rate"] == 0.428571
    assert result["fixed"]["correct_rate"] == 1.0
    assert result["exponential"]["correct_rate"] == 1.0
    assert result["exponential_jitter"]["correct_rate"] == 1.0
    failed = [r for r in first if r.case_id == "authentication_denied"]
    assert failed and all(r.attempts == 1 for r in failed)
    assert all(r.cost_usd is None and r.latency_kind == "simulated" for r in first)


def test_retry_after_minimum_is_respected() -> None:
    manifest, dataset = spec("retry_strategies")
    records = retry_benchmark.run(manifest, dataset)
    relevant = [
        r for r in records if r.case_id == "retry_after_once" and r.implementation == "fixed"
    ]
    assert all(r.latency_seconds == 0.44 for r in relevant)


def test_orchestration_reuses_exact_same_functions() -> None:
    manifest, dataset = spec("orchestration_comparison")
    records = orchestration_benchmark.run(manifest, dataset)
    assert len(records) == 4 * 3 * 5
    for impl in ("manual_python", "sdk_state_graph"):
        samples = [r for r in records if r.implementation == impl]
        assert all(r.correct and r.outcome == "completed" for r in samples)
    framework = [r for r in records if r.implementation == "langgraph"]
    assert all(r.outcome in {"completed", "unavailable"} for r in framework)
    assert not any(r.outcome == "unavailable" and r.correct is True for r in framework)


def test_math_benchmark_determinism_and_negative_findings() -> None:
    manifest, dataset = spec("math_strategies")
    first = math_benchmark.run(manifest, dataset)
    assert first == math_benchmark.run(manifest, dataset)
    assert len(first) == 5 * 3 * 5
    rates = aggregate(first)
    assert rates["direct"]["correct_rate"] == 0.4
    assert rates["arithmetic_tool"]["correct_rate"] == 0.6
    assert rates["verification_loop"]["correct_rate"] == 0.8
    unsafe = [r for r in first if r.case_id == "math_04" and r.implementation == "arithmetic_tool"]
    assert all(
        r.tool_success is False and r.error_category == "invalid_tool_expression" for r in unsafe
    )
    assert all(r.cost_usd is None for r in first)


@pytest.mark.parametrize(
    "expr",
    [
        "__import__('os').system('echo escaped')",
        "2 ** 10000000",
        "open('private')",
        "1/0",
        "[1,2,3]",
        "True",
        "1.4 + 2",
        "(5 + 9) * 10 ** 1000",
        "9" * 500,
        "1000000000 * 1000000000",
        "(1+2)" * 25,
    ],
)
def test_math_tool_rejects_unsafe_or_unsupported_expressions(expr: str) -> None:
    with pytest.raises(UnsupportedExpression):
        arithmetic(expr)


def test_math_tool_handles_bounded_integers() -> None:
    assert arithmetic("17 * 23 + 9") == 400
    assert arithmetic("-(4 + 5) * 6") == -54


def test_manifest_rejects_outside_repository(tmp_path: Path) -> None:
    manifest, _ = spec("retry_strategies")
    source = json.loads((ROOT / "experiments/configs/retry_strategies.json").read_text())
    source["dataset"] = "../../../../etc/passwd"
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(source))
    with pytest.raises(ValueError, match="outside the repository"):
        load_manifest(path, ROOT)
    assert manifest.id == "retry_strategies"


def test_report_contains_provenance_and_raw_rows(tmp_path: Path) -> None:
    manifest_path = ROOT / "experiments/configs/math_strategies.json"
    manifest, dataset = load_manifest(manifest_path, ROOT)
    rows = math_benchmark.run(manifest, dataset)
    destination = tmp_path / "reports"
    write_artifacts(
        manifest_path=manifest_path,
        dataset_path=dataset,
        manifest=manifest,
        observations=rows,
        destination=destination,
        repo_version="0.6.0",
    )
    saved = [json.loads(line) for line in (destination / "results.jsonl").read_text().splitlines()]
    assert len(saved) == len(rows)
    metadata = json.loads((destination / "metadata.json").read_text())
    assert len(metadata["dataset_sha256"]) == 64
    assert len(metadata["manifest_sha256"]) == 64
    assert metadata["concurrency"] == 1
    assert "Negative results" in (destination / "report.md").read_text()
    assert "N/A" in (destination / "report.md").read_text()


def test_live_probe_is_offline_testable_with_mock() -> None:
    mock = MockProvider(responses={"Q?": "400"})
    rows = probe(mock, "mock", [{"id": "test", "question": "Q?", "expected": "400"}])
    assert len(rows) == 1
    assert rows[0].correct is True and rows[0].usage_kind == "unavailable"
    assert rows[0].latency_kind == "observed_wall"


def test_aggregate_missing_data_is_not_zero() -> None:
    stats = aggregate(
        [Observation("t", "one", "unavailable", 0, "unavailable", None, None, "unavailable")]
    )["unavailable"]
    assert stats["cost_usd_total_known"] is None
    assert stats["correct_rate"] is None
    assert stats["latency_p95_seconds"] is None
