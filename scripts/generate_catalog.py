"""Generate the deterministic executable handbook catalog from pattern manifests."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
OWNERS = {
    "01_prompt_engineering": "applied_ai.prompting, applied_ai.core.structured",
    "02_model_integration": "applied_ai.providers, applied_ai.routing, applied_ai.inference",
    "03_agent_orchestration": "applied_ai.orchestration",
    "04_knowledge_and_context": "applied_ai.knowledge",
    "05_reliability_engineering": "applied_ai.reliability",
    "06_evaluation_and_observability": "applied_ai.evaluation",
    "07_optimization": "applied_ai.optimization",
    "08_reasoning_and_execution": "applied_ai.reasoning, applied_ai.execution",
}


def generate(root: Path = ROOT) -> str:
    rows = []
    for meta in sorted((root / "engineering_patterns").glob("0[1-8]_*/**/pattern.yaml")):
        data: Any = yaml.safe_load(meta.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not all(
            isinstance(data.get(k), str) for k in ("id", "name", "entrypoint", "started_on")
        ):
            raise ValueError(f"Invalid pattern manifest: {meta}")
        entrypoint = data["entrypoint"]
        if Path(entrypoint).name != entrypoint or not (meta.parent / entrypoint).is_file():
            raise ValueError(f"Invalid entrypoint in {meta}")
        category = meta.relative_to(root / "engineering_patterns").parts[0]
        if category not in OWNERS or data.get("category") != category:
            raise ValueError(f"Invalid pattern category in {meta}")
        doc = meta.parent / "README.md"
        if not doc.is_file():
            raise ValueError(f"Missing README: {meta}")
        display = data["name"].replace("|", r"\|")
        link = "../" + meta.parent.relative_to(root).as_posix() + "/README.md"
        rows.append(
            (
                category,
                f"| [{display}]({link}) | `{data['id']}` | {data['started_on']} | {'Yes' if data.get('supports_offline_testing') is True else 'No'} |",
            )
        )
    if not rows:
        raise ValueError("No published patterns found")
    lines = [
        "# Executable Engineering-Pattern Catalog",
        "",
        "Generated from `engineering_patterns/**/pattern.yaml` by `scripts/generate_catalog.py`.",
        "The numbering organizes independent handbook categories; it is not a runtime sequence.",
        "",
    ]
    for category, owner in OWNERS.items():
        group = [entry for c, entry in rows if c == category]
        lines.extend(
            [
                f"## {category}",
                "",
                f"SDK owner(s): `{owner}`",
                "",
                "| Pattern | ID | Started | Offline |",
                "| --- | --- | --- | --- |",
                *group,
                "",
            ]
        )
    lines.extend(
        [
            "Run all offline patterns:",
            "",
            "```bash",
            "uv run --offline --locked python scripts/run_all_patterns.py",
            "```",
            "",
            "Only entries with a runnable manifest are listed; directories in the long-term roadmap are not claimed as implemented.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    target = ROOT / "docs" / "PATTERN_CATALOG.md"
    content = generate()
    if args.check:
        if not target.exists() or target.read_text(encoding="utf-8") != content:
            raise SystemExit("Pattern catalog is stale: run python scripts/generate_catalog.py")
        print("Pattern catalog is current")
    else:
        target.write_text(content, encoding="utf-8")
        print(f"Wrote {target}")


if __name__ == "__main__":
    main()
