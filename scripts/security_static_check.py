"""Offline defense-in-depth secret-pattern scan (not an audit of Git history)."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE = {
    ".git",
    ".venv",
    "build",
    "dist",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}
ALLOWED = {".py", ".md", ".txt", ".toml", ".yaml", ".yml", ".json", ".html", ".js", ".css", ".sh"}
PATTERNS = {
    "private-key-block": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "aws-key-id": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "github-token": re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{30,}\b"),
    "openai-token": re.compile(r"\bsk-(?:proj-|svcacct-)[A-Za-z0-9_-]{20,}\b"),
}


def scan_text(content: str) -> list[str]:
    return [name for name, regex in PATTERNS.items() if regex.search(content)]


def scan_tree(root: Path) -> list[str]:
    findings: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or any(part in EXCLUDE for part in path.relative_to(root).parts):
            continue
        rel = path.relative_to(root)
        if rel.name == ".env" or (rel.name.startswith(".env.") and rel.name != ".env.example"):
            findings.append(f"{rel}: untracked/private environment file must not be shipped")
            continue
        if rel.suffix.lower() not in ALLOWED or path.stat().st_size > 1_000_000:
            continue
        for finding in scan_text(path.read_text(encoding="utf-8", errors="replace")):
            findings.append(f"{rel}: {finding}")
    return findings


def main() -> None:
    argparse.ArgumentParser(description=__doc__).parse_args()
    found = scan_tree(ROOT)
    if found:
        raise SystemExit(
            "Potential secret material found (contents not displayed):\n" + "\n".join(found)
        )
    print("Offline source/filename secret-pattern scan passed; run Gitleaks for history scanning")


if __name__ == "__main__":
    main()
