"""Simplified WhyBuddy: explicit task routing and provider-neutral generation."""

from __future__ import annotations

import sys

from applied_ai.core import LLMRequest, Message
from applied_ai.providers.factory import ProviderFactory
from applied_ai.routing import ModelTarget, TaskRouter


def run(*, allow_live: bool = False) -> dict[str, str]:
    config = ProviderFactory()
    selected = config.create(allow_live=allow_live, mock_text="A concise mock answer.")
    provider = selected.provider
    # Assign distinct models through environment without changing application code.
    fast_model = config.env.get("AI_LAB_FAST_MODEL", selected.model)
    detailed_model = config.env.get("AI_LAB_DETAILED_MODEL", selected.model)
    router = TaskRouter(
        {
            "quick": ModelTarget(provider, fast_model),
            "detailed": ModelTarget(provider, detailed_model),
        }
    )
    try:
        results = {}
        for task in ("quick", "detailed"):
            response = router.generate(
                task,
                LLMRequest(
                    selected.model,
                    (
                        Message(
                            "user",
                            "Explain RAG in one sentence."
                            if task == "quick"
                            else "Explain RAG, including one limitation.",
                        ),
                    ),
                ),
            )
            results[task] = f"[{response.provider}/{response.model}] {response.text}"
        print("results:", results)
        return results
    finally:
        close = getattr(provider, "close", None)
        if callable(close):
            close()


if __name__ == "__main__":
    for key, answer in run(allow_live="--live" in sys.argv).items():
        print(f"{key}: {answer}")
