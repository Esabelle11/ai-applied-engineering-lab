"""Validate concrete handbook pattern metadata and minimal layout."""

from __future__ import annotations

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
}


def validate() -> list[str]:
    errors: list[str] = []
    identifiers: set[str] = set()
    categories = sorted(p for p in HANDBOOK.glob("0[1-8]_*") if p.is_dir())
    if len(categories) != 8:
        errors.append(f"Expected 8 pattern categories; found {len(categories)}")

    patterns = 0
    for category in categories:
        if not (category / "README.md").is_file():
            errors.append(f"Missing README: {category}")
        for pattern in category.iterdir():
            if not pattern.is_dir():
                continue
            patterns += 1
            metadata_path = pattern / "pattern.yaml"
            if not metadata_path.is_file():
                errors.append(f"Missing pattern metadata: {metadata_path}")
                continue
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

    if patterns < 1:
        errors.append("At least one concrete example pattern is required")
    return errors


def main() -> None:
    errors = validate()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print("Handbook structure valid: 8 categories and runnable example(s).")


if __name__ == "__main__":
    main()
