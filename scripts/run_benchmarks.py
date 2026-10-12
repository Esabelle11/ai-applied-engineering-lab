"""Reproducible offline benchmark runner with per-experiment evidence bundles.

Usage: python scripts/run_benchmarks.py [--experiment ID] [--output PATH] [--require-langgraph]
"""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for import_dir in (ROOT / "src", ROOT):
    if str(import_dir) not in sys.path:
        sys.path.insert(0, str(import_dir))

from applied_ai import __version__  # noqa: E402
from applied_ai.experimentation import aggregate, load_manifest, write_artifacts  # noqa: E402
from benchmarks.runners import (  # noqa: E402
    math_benchmark,
    orchestration_benchmark,
    retry_benchmark,
)

RUNNERS = {
    "retry_strategies": retry_benchmark.run,
    "orchestration_comparison": orchestration_benchmark.run,
    "math_strategies": math_benchmark.run,
}


def _git_revision() -> str | None:
    process = (
        subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
        if (ROOT / ".git").exists()
        else None
    )
    return process.stdout.strip() if process and process.returncode == 0 else None


def run_all(
    *, experiment: str | None = None, output: Path | None = None, require_langgraph: bool = False
) -> None:
    output_dir = output or ROOT / "benchmarks/reports/generated"
    targets = [experiment] if experiment else list(RUNNERS)
    for target in targets:
        if target not in RUNNERS:
            raise ValueError(f"Unknown experiment: {target}")
        manifest_path = ROOT / "experiments/configs" / f"{target}.json"
        spec, dataset = load_manifest(manifest_path, ROOT)
        observations = RUNNERS[target](spec, dataset)
        if len(observations) != spec.repetitions * len(spec.implementations) * len(
            json.loads(dataset.read_text(encoding="utf-8"))
        ):
            raise RuntimeError("Incomplete experiment observation matrix")
        if (
            require_langgraph
            and target == "orchestration_comparison"
            and any(obs.outcome == "unavailable" for obs in observations)
        ):
            raise RuntimeError("--require-langgraph requested, install the benchmark extra")
        try:
            lg_version = importlib.metadata.version("langgraph")
        except importlib.metadata.PackageNotFoundError:
            lg_version = None
        extra = {
            "git_revision": _git_revision(),
            "langgraph_version": lg_version,
            "provider": "MockProvider" if target != "orchestration_comparison" else "none",
            "model": "mock-model" if target != "orchestration_comparison" else None,
            "temperature": None,
            "prompt_version": "synthetic-v1",
            "clock": "virtual" if target != "orchestration_comparison" else "wall_perf_counter",
            "live_api_calls": 0,
        }
        write_artifacts(
            manifest_path=manifest_path,
            dataset_path=dataset,
            manifest=spec,
            observations=observations,
            destination=output_dir / target,
            repo_version=__version__,
            extra_metadata=extra,
        )
        totals = aggregate(observations)
        status = ", ".join(f"{name}:{stats['correct_rate']}" for name, stats in totals.items())
        print(f"PASS {target}: {len(observations)} records; correctness={status}")
    print(f"Artifacts: {output_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment", choices=sorted(RUNNERS))
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--require-langgraph", action="store_true")
    args = parser.parse_args()
    run_all(
        experiment=args.experiment, output=args.output, require_langgraph=args.require_langgraph
    )


if __name__ == "__main__":
    main()
