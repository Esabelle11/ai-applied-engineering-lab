"""Offline benchmark infrastructure: validated manifests and auditable artifacts.

Raw case results carry *reported* measurements only. Synthetic timing and token
values must state their source, never masquerade as provider telemetry.
"""

from __future__ import annotations

import hashlib
import json
import math
import platform
import statistics
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass(frozen=True, slots=True)
class ExperimentManifest:
    id: str
    version: str
    question: str
    hypothesis: str
    controls: tuple[str, ...]
    dataset: str
    implementations: tuple[str, ...]
    metrics: tuple[str, ...]
    seed: int
    repetitions: int
    concurrency: int
    simulation: bool
    limitations: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.id.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Experiment id must be alphanumeric with '-' or '_'")
        if not self.version or not self.question or not self.hypothesis:
            raise ValueError("Version, question and hypothesis are required")
        if (
            not self.controls
            or not self.implementations
            or len(set(self.implementations)) != len(self.implementations)
        ):
            raise ValueError("Unique implementations and experimental controls are required")
        if (
            type(self.seed) is not int
            or type(self.repetitions) is not int
            or not 1 <= self.repetitions <= 100
        ):
            raise ValueError("Invalid seed or repetitions")
        if type(self.concurrency) is not int or self.concurrency != 1:
            raise ValueError("Phase 5 offline benchmark uses concurrency=1 to avoid confounding")
        if not self.limitations or not self.metrics:
            raise ValueError("Metrics and limitations are mandatory")


def load_manifest(path: Path, repo_root: Path) -> tuple[ExperimentManifest, Path]:
    """Dataset must remain inside the repo; hashes tie results to exact inputs."""
    doc = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(doc, dict):
        raise ValueError("Manifest must be a JSON object")
    spec = ExperimentManifest(
        id=doc["id"],
        version=doc["version"],
        question=doc["question"],
        hypothesis=doc["hypothesis"],
        controls=tuple(doc["controls"]),
        dataset=doc["dataset"],
        implementations=tuple(doc["implementations"]),
        metrics=tuple(doc["metrics"]),
        seed=doc["seed"],
        repetitions=doc["repetitions"],
        concurrency=doc["concurrency"],
        simulation=doc["simulation"],
        limitations=tuple(doc["limitations"]),
    )
    root = repo_root.resolve()
    dataset = (root / spec.dataset).resolve()
    if not dataset.is_relative_to(root) or not dataset.is_file():
        raise ValueError("Dataset path missing or outside the repository")
    return spec, dataset


@dataclass(frozen=True, slots=True)
class Observation:
    experiment_id: str
    case_id: str
    implementation: str
    repeat: int
    outcome: str  # completed | error | unavailable
    correct: bool | None
    latency_seconds: float | None
    latency_kind: str  # observed_wall | simulated | unavailable
    attempts: int | None = None
    tool_success: bool | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    usage_kind: str = "unavailable"  # fixture | provider | unavailable
    cost_usd: float | None = None
    error_category: str | None = None
    note: str | None = None

    def __post_init__(self) -> None:
        if self.outcome not in {"completed", "error", "unavailable"}:
            raise ValueError("Invalid outcome")
        if self.latency_kind not in {"simulated", "observed_wall", "unavailable"}:
            raise ValueError("Invalid latency kind")
        if self.usage_kind not in {"fixture", "provider", "unavailable"}:
            raise ValueError("Invalid usage kind")
        if self.latency_seconds is not None and (
            not math.isfinite(self.latency_seconds) or self.latency_seconds < 0
        ):
            raise ValueError("Latency must be finite and nonnegative")


def _percentile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    pos = (len(ordered) - 1) * fraction
    low = math.floor(pos)
    high = math.ceil(pos)
    return round(ordered[low] + (ordered[high] - ordered[low]) * (pos - low), 6)


def aggregate(observations: list[Observation]) -> dict[str, dict[str, Any]]:
    groups: dict[str, list[Observation]] = defaultdict(list)
    for item in observations:
        groups[item.implementation].append(item)
    summary: dict[str, dict[str, Any]] = {}
    for name, rows in sorted(groups.items()):
        available = [row for row in rows if row.outcome != "unavailable"]
        successes = [row for row in available if row.outcome == "completed"]
        measured = [row for row in available if row.correct is not None]
        latencies = [row.latency_seconds for row in available if row.latency_seconds is not None]
        token_measured = [
            row
            for row in available
            if row.input_tokens is not None and row.output_tokens is not None
        ]
        costs_measured = [row.cost_usd for row in available if row.cost_usd is not None]
        tools = [row for row in available if row.tool_success is not None]
        summary[name] = {
            "records": len(rows),
            "available_records": len(available),
            "distinct_cases": len({row.case_id for row in available}),
            "completion_rate": round(len(successes) / len(available), 6) if available else None,
            "error_rate": round((len(available) - len(successes)) / len(available), 6)
            if available
            else None,
            "correct_rate": round(sum(row.correct is True for row in measured) / len(measured), 6)
            if measured
            else None,
            "correct_denominator": len(measured),
            "tool_success_rate": round(
                sum(row.tool_success is True for row in tools) / len(tools), 6
            )
            if tools
            else None,
            "latency_p50_seconds": _percentile(latencies, 0.5),
            "latency_p95_seconds": _percentile(latencies, 0.95),
            "latency_kind": sorted({row.latency_kind for row in available}),
            "mean_attempts": round(
                statistics.mean(row.attempts for row in available if row.attempts is not None), 6
            )
            if any(row.attempts is not None for row in available)
            else None,
            "tokens_total_known": sum(
                (row.input_tokens or 0) + (row.output_tokens or 0) for row in token_measured
            )
            if token_measured
            else None,
            "tokens_coverage": len(token_measured),
            "cost_usd_total_known": round(sum(costs_measured), 8)
            if len(costs_measured) == len(available) and available
            else None,
            "cost_coverage": len(costs_measured),
            "error_categories": sorted(
                {row.error_category for row in available if row.error_category}
            ),
        }
    return summary


def _render_val(value: Any) -> str:
    if value is None:
        return "N/A"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def write_artifacts(
    *,
    manifest_path: Path,
    dataset_path: Path,
    manifest: ExperimentManifest,
    observations: list[Observation],
    destination: Path,
    repo_version: str,
    extra_metadata: dict[str, Any] | None = None,
) -> None:
    """Write raw observations, summary, provenance, and a limitation-aware report."""
    destination.mkdir(parents=True, exist_ok=True)
    summary = aggregate(observations)
    metadata: dict[str, Any] = {
        "experiment_id": manifest.id,
        "experiment_version": manifest.version,
        "run_utc": datetime.now(UTC).isoformat(),
        "seed": manifest.seed,
        "repetitions": manifest.repetitions,
        "concurrency": manifest.concurrency,
        "simulation": manifest.simulation,
        "manifest_sha256": _sha256(manifest_path),
        "dataset_sha256": _sha256(dataset_path),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "applied_ai_version": repo_version,
        "comparison_status": "offline_synthetic" if manifest.simulation else "live_uncontrolled",
    }
    metadata.update(extra_metadata or {})
    (destination / "manifest_snapshot.json").write_text(
        json.dumps(asdict(manifest), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (destination / "metadata.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (destination / "results.jsonl").write_text(
        "".join(json.dumps(asdict(obs), sort_keys=True) + "\n" for obs in observations),
        encoding="utf-8",
    )
    (destination / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    report = [
        f"# {manifest.id} — controlled experiment",
        "",
        f"**Question:** {manifest.question}",
        "",
        f"**Hypothesis (not assumed true):** {manifest.hypothesis}",
        "",
        f"**Manifest version:** {manifest.version}; **unique dataset cases:** "
        f"{len({row.case_id for row in observations})}; **repeat runs:** {manifest.repetitions}; "
        f"**seed:** {manifest.seed}",
        "",
        "**Evidence scope:** offline synthetic/fixture results; not evidence of live model quality "
        "or production throughput."
        if manifest.simulation
        else "**Evidence scope:** live observational results, not a controlled offline comparison.",
        "",
        "## Controlled conditions",
        "",
    ]
    report.extend(f"- {item}" for item in manifest.controls)
    report.extend(
        [
            "",
            "## Results",
            "",
            "| Implementation | Completed | Correct | p50 (s) | p95 (s) | Errors | Attempts mean | Tokens known | Cost USD |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for name, data in summary.items():
        report.append(
            "| "
            + " | ".join(
                (
                    name,
                    *(
                        _render_val(data[col])
                        for col in (
                            "completion_rate",
                            "correct_rate",
                            "latency_p50_seconds",
                            "latency_p95_seconds",
                            "error_rate",
                            "mean_attempts",
                            "tokens_total_known",
                            "cost_usd_total_known",
                        )
                    ),
                )
            )
            + " |"
        )
    report.extend(["", "Latency types by implementation:", ""])
    report.extend(
        f"- `{name}`: {', '.join(v['latency_kind']) or 'unavailable'}"
        for name, v in summary.items()
    )
    report.extend(["", "## Negative results and failures", ""])
    failures = [o for o in observations if o.outcome == "error" or o.correct is False]
    if failures:
        for row in failures[:12]:
            report.append(
                f"- `{row.implementation}` on `{row.case_id}`: outcome={row.outcome}, "
                f"correct={row.correct}, error={row.error_category or 'none'}"
            )
        if len(failures) > 12:
            report.append(f"- … {len(failures) - 12} additional repeated failures in results.jsonl")
    else:
        report.append(
            "- None observed in these fixture cases; this does not establish general reliability."
        )
    report.extend(["", "## Limitations", ""])
    report.extend(f"- {item}" for item in manifest.limitations)
    report.extend(
        [
            "- Repeated runs of the same fixed fixtures are **not independent samples**; do not infer statistical significance.",
            "- Percentiles use linear interpolation over recorded observations. Small samples make tail estimates unstable.",
            "- Token/cost aggregates are reported only for measured or explicitly fixture-defined usage; missing is N/A, not zero.",
            "- Inspect `results.jsonl`, `summary.json`, `metadata.json` and the exact dataset/manifest hashes to reproduce claims.",
            "",
            "## Reproduction",
            "",
            f"`uv run --locked python scripts/run_benchmarks.py --experiment {manifest.id}`",
            "",
        ]
    )
    (destination / "report.md").write_text("\n".join(report), encoding="utf-8")
