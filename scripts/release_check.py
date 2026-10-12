"""Pre-tag release-readiness gate. No tags are created by this script."""

from __future__ import annotations

import argparse
import ast
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "README.md",
    "LICENSE",
    "CHANGELOG.md",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "docs/API_REFERENCE.md",
    "docs/PATTERN_CATALOG.md",
    "docs/RELEASE_PROCESS.md",
    "docs/COMPATIBILITY.md",
    "docs/SECURITY_REVIEW.md",
    ".github/workflows/ci.yml",
    ".github/workflows/security.yml",
    ".github/PULL_REQUEST_TEMPLATE.md",
)


def declared_version(root: Path) -> str:
    project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    version = project["project"]["version"]
    module = ast.parse((root / "src/applied_ai/__init__.py").read_text(encoding="utf-8"))
    values = [
        node.value.value
        for node in module.body
        if isinstance(node, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "__version__" for t in node.targets)
        and isinstance(node.value, ast.Constant)
        and isinstance(node.value.value, str)
    ]
    if values != [version]:
        raise ValueError(f"Version mismatch: pyproject={version}; package={values}")
    return version


def validate(root: Path, *, require_lock: bool) -> list[str]:
    errors = [f"Missing {path}" for path in REQUIRED if not (root / path).is_file()]
    try:
        version = declared_version(root)
        if f"[{version}]" not in (root / "CHANGELOG.md").read_text(encoding="utf-8"):
            errors.append(f"CHANGELOG.md missing [{version}]")
    except (OSError, KeyError, ValueError, tomllib.TOMLDecodeError) as exc:
        errors.append(str(exc))
    if require_lock and not (root / "uv.lock").is_file():
        errors.append("No uv.lock: run uv lock online and commit it before release")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strict", action="store_true", help="Require a genuine committed-ready uv.lock"
    )
    args = parser.parse_args()
    issues = validate(ROOT, require_lock=args.strict)
    if issues:
        raise SystemExit("RELEASE BLOCKED:\n" + "\n".join(f"- {s}" for s in issues))
    print(f"Release metadata checks passed for {declared_version(ROOT)}")
    if not args.strict:
        print(
            "Metadata-only check: lockfile, dependency audit, GitHub CI, and tag still require verification"
        )


if __name__ == "__main__":
    main()
