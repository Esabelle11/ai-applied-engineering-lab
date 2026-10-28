"""Offline runner for all published handbook patterns; no credentials ever forwarded."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
HANDBOOK = ROOT / "engineering_patterns"


def main() -> None:
    patterns = sorted(HANDBOOK.glob("[0-9][0-9]_*/**/pattern.yaml"))
    if not patterns:
        raise SystemExit("No published patterns")
    allow = {
        "PATH",
        "HOME",
        "SYSTEMROOT",
        "WINDIR",
        "TMP",
        "TEMP",
        "TMPDIR",
        "VIRTUAL_ENV",
        "PYTHONPATH",
        "PYTHONIOENCODING",
        "PYTHONUTF8",
    }
    env = {key: value for key, value in os.environ.items() if key in allow}
    successes = 0
    for manifest in patterns:
        info = yaml.safe_load(manifest.read_text(encoding="utf-8"))
        if info.get("requires_api_key") or not info.get("supports_offline_testing"):
            print(f"SKIP {info.get('id')} (no offline example)")
            continue
        entrypoint = info.get("entrypoint")
        if not isinstance(entrypoint, str) or Path(entrypoint).name != entrypoint:
            raise SystemExit(f"Unsafe pattern entrypoint: {manifest}")
        executable = manifest.parent / entrypoint
        print(f"RUN {info['id']}", flush=True)
        result = subprocess.run(
            [sys.executable, str(executable)],
            cwd=ROOT,
            env=env,
            timeout=20,
            check=False,
        )
        if result.returncode:
            raise SystemExit(f"FAILED {info['id']} (exit {result.returncode})")
        successes += 1
    print(f"PASS: {successes} offline patterns completed")


if __name__ == "__main__":
    main()
