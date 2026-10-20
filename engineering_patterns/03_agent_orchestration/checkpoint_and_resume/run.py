"""Persist a checkpoint at a workflow boundary and resume from a copy."""

from __future__ import annotations

from applied_ai.orchestration import CheckpointStore


def resume_after_review() -> str:
    store = CheckpointStore()
    store.save("case-1", {"stage": "review", "draft": "initial answer"})
    resumed = dict(store.load("case-1"))
    resumed["stage"] = "complete"
    return str(resumed["stage"])


def main() -> None:
    print(resume_after_review())


if __name__ == "__main__":
    main()
