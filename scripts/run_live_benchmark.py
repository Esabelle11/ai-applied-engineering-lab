"""Optional explicitly authorized live arithmetic probe, using .env provider selection.

Never called by default tests/CI. At most three paid or quota-limited requests.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from applied_ai import LLMRequest, Message, __version__  # noqa: E402
from applied_ai.core.exceptions import LLMError  # noqa: E402
from applied_ai.experimentation import Observation, load_manifest, write_artifacts  # noqa: E402
from applied_ai.providers.factory import ProviderFactory  # noqa: E402


def probe(provider, model: str, cases: list[dict[str, str]]) -> list[Observation]:  # noqa: ANN001
    rows: list[Observation] = []
    for case in cases:
        start = time.perf_counter()
        try:
            answer = provider.generate(
                LLMRequest(model, (Message("user", case["question"]),), max_output_tokens=32)
            )
        except LLMError as exc:
            rows.append(
                Observation(
                    "live_arithmetic_probe",
                    case["id"],
                    "configured_live_provider",
                    0,
                    "error",
                    False,
                    time.perf_counter() - start,
                    "observed_wall",
                    attempts=1,
                    error_category=exc.category,
                )
            )
        else:
            usage = answer.usage
            rows.append(
                Observation(
                    "live_arithmetic_probe",
                    case["id"],
                    "configured_live_provider",
                    0,
                    "completed",
                    answer.text.strip() == case["expected"],
                    time.perf_counter() - start,
                    "observed_wall",
                    attempts=1,
                    input_tokens=usage.input_tokens if usage else None,
                    output_tokens=usage.output_tokens if usage else None,
                    usage_kind="provider" if usage else "unavailable",
                    note="Strict string match, does not judge semantically equivalent answers",
                )
            )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Explicitly authorize API requests")
    parser.add_argument("--max-requests", type=int, default=3)
    parser.add_argument("--output", type=Path, default=ROOT / "benchmarks/reports/generated")
    args = parser.parse_args()
    if not args.live:
        parser.error("Live calls are disabled; pass --live to authorize API and quota usage")
    if not 1 <= args.max_requests <= 3:
        parser.error("--max-requests must be in [1,3]")
    factory = ProviderFactory()
    if factory.kind == "mock":
        parser.error("This probe requires a real configured provider, not mock")
    manifest_path = ROOT / "experiments/configs/live_arithmetic_probe.json"
    manifest, dataset = load_manifest(manifest_path, ROOT)
    cases = json.loads(dataset.read_text(encoding="utf-8"))[: args.max_requests]
    selection = factory.create(allow_live=True)
    try:
        observations = probe(selection.provider, selection.model, cases)
    finally:
        close = getattr(selection.provider, "close", None)
        if callable(close):
            close()
    extra = {
        "provider": factory.kind,
        "model": selection.model,
        "temperature": None,
        "seed_supported": False,
        "seed_effective": None,
        "prompt_version": "live-probe-v1",
        "live_api_calls": len(observations),
        "concurrency": 1,
        "known_uncontrolled": [
            "provider backend version",
            "service load",
            "model routing",
            "seed and sampling",
            "network conditions",
            "API quota",
        ],
    }
    write_artifacts(
        manifest_path=manifest_path,
        dataset_path=dataset,
        manifest=manifest,
        observations=observations,
        destination=args.output / f"live_arithmetic_probe_{factory.kind}",
        repo_version=__version__,
        extra_metadata=extra,
    )
    print(f"Recorded {len(observations)} live results (model={selection.model}).")
    print("Billed cost unverified; check your provider dashboard.")


if __name__ == "__main__":
    main()
