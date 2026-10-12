"""Executable, offline Applied AI handbook pattern."""

from applied_ai import MockProvider
from applied_ai.prompting import PromptChain, PromptStep, PromptTemplate


def main() -> None:
    provider = MockProvider(
        responses={
            "Summarize RAG": "retrieval adds context",
            "Shorten retrieval adds context": "RAG uses context",
        }
    )
    chain = PromptChain(
        [
            PromptStep("summary", PromptTemplate("Summarize {topic}")),
            PromptStep("short", PromptTemplate("Shorten {summary}")),
        ]
    )
    result = chain.run(provider, "mock", {"topic": "RAG"})
    print(result["short"])


if __name__ == "__main__":
    main()
