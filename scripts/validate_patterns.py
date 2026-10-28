"""Validate concrete handbook pattern metadata and minimal layout."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
HANDBOOK = ROOT / "engineering_patterns"
REQUIRED = {
    "id",
    "name",
    "category",
    "status",
    "requires_api_key",
    "supports_offline_testing",
    "entrypoint",
    "started_on",
}


def validate() -> list[str]:
    errors: list[str] = []
    identifiers: set[str] = set()
    categories = sorted(p for p in HANDBOOK.glob("[0-9][0-9]_*") if p.is_dir())
    if len(categories) != 9:
        errors.append(f"Expected 9 pattern categories; found {len(categories)}")

    patterns = 0
    for category in categories:
        if not (category / "README.md").is_file():
            errors.append(f"Missing README: {category}")
        for metadata_path in sorted(category.rglob("pattern.yaml")):
            pattern = metadata_path.parent
            patterns += 1
            try:
                loaded = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
            except yaml.YAMLError as exc:
                errors.append(f"Invalid YAML: {metadata_path} ({exc})")
                continue
            if not isinstance(loaded, dict):
                errors.append(f"Metadata must be a mapping: {metadata_path}")
                continue
            missing = REQUIRED.difference(loaded)
            if missing:
                errors.append(f"{metadata_path}: missing {', '.join(sorted(missing))}")
                continue
            identifier = loaded["id"]
            if not isinstance(identifier, str) or not identifier.strip():
                errors.append(f"{metadata_path}: id must be a nonempty string")
            elif identifier in identifiers:
                errors.append(f"Duplicate pattern ID: {identifier}")
            else:
                identifiers.add(identifier)
            if loaded["category"] != category.name:
                errors.append(f"{metadata_path}: category does not match folder")
            if (
                not isinstance(loaded["entrypoint"], str)
                or not (pattern / loaded["entrypoint"]).is_file()
            ):
                errors.append(f"{metadata_path}: missing executable entrypoint")
            if not (pattern / "README.md").is_file():
                errors.append(f"{pattern}: missing README.md")
            for key in ("requires_api_key", "supports_offline_testing"):
                if not isinstance(loaded[key], bool):
                    errors.append(f"{metadata_path}: {key} must be a boolean")
            if not isinstance(loaded["started_on"], str) or not re.fullmatch(
                r"\d{2}/\d{2}/\d{4}", loaded["started_on"]
            ):
                errors.append(f"{metadata_path}: started_on must use DD/MM/YYYY")

    if patterns < 1:
        errors.append("At least one concrete example pattern is required")
    return errors


def main() -> None:
    errors = validate()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print("Handbook structure valid: 9 categories and runnable example(s).")


if __name__ == "__main__":
    main()
