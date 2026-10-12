"""Run five case studies with a scrubbed, explicitly mock-only environment."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES = ("prompt_forge", "whybuddy", "autonomous_debate", "citizen_assist", "math_reasoning")


def main() -> None:
    safe = {
        key: os.environ[key]
        for key in ("PATH", "SYSTEMROOT", "WINDIR", "TMP", "TEMP", "TMPDIR")
        if key in os.environ
    }
    safe["AI_LAB_PROVIDER"] = "mock"
    safe["AI_LAB_MODEL"] = "mock-model"
    safe["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + str(ROOT)
    for name in CASES:
        print(f"CASE {name}", flush=True)
        subprocess.run(
            [sys.executable, "-m", f"case_studies.{name}.run"],
            check=True,
            cwd=ROOT,
            timeout=20,
            env=safe,
        )
    print(f"PASS: {len(CASES)} offline case studies")


if __name__ == "__main__":
    main()
