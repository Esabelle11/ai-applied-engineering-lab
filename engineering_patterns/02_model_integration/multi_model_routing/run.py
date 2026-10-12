"""Executable, offline Applied AI handbook pattern."""

from applied_ai import LLMRequest, Message, MockProvider
from applied_ai.routing import ModelTarget, TaskRouter


def main() -> None:
    fast = MockProvider(default_text="Fast summary")
    precise = MockProvider(default_text="Detailed analysis")
    router = TaskRouter(
        {
            "summarize": ModelTarget(fast, "mock-fast"),
            "analyze": ModelTarget(precise, "mock-precise"),
        }
    )
    request = LLMRequest("placeholder", (Message("user", "Explain RAG"),))
    for task in ("summarize", "analyze"):
        result = router.generate(task, request)
        print(f"{task}: {result.model} -> {result.text}")


if __name__ == "__main__":
    main()
