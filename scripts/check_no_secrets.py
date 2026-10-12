"""Check dangerous tracked filenames. This is not a comprehensive secret scanner."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RISKY_SUFFIXES = (".pem", ".p12", ".pfx", ".key")


def main() -> None:
    try:
        output = subprocess.check_output(
            ["git", "ls-files", "-z"], cwd=ROOT, stderr=subprocess.DEVNULL
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("SKIP: Git repository not initialized; use git init before tracked-file checks.")
        return

    tracked = [entry.decode("utf-8") for entry in output.split(b"\x00") if entry]
    risky: list[str] = []
    for filename in tracked:
        path = Path(filename)
        name = path.name.lower()
        if (
            name == ".env"
            or (name.startswith(".env.") and name != ".env.example")
            or name.endswith(RISKY_SUFFIXES)
            or "secrets" in path.parts
        ):
            risky.append(filename)
    if risky:
        raise SystemExit("Potential secret files are tracked:\n" + "\n".join(risky))
    print(f"Tracked-file name check passed ({len(tracked)} tracked files).")


if __name__ == "__main__":
    main()
