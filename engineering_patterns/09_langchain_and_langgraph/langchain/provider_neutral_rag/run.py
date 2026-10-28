"""Offline replay and optional LangChain local retrieval runnable."""

from __future__ import annotations

import argparse
import json
from typing import Any


def run() -> dict[str, Any]:
    return {
        "offline": True,
        "question": "When can I request a refund?",
        "answer": "Within 30 days with proof of purchase [refund-policy].",
        "sources": ["refund-policy"],
    }


def framework_run() -> dict[str, Any]:
    from langchain_core.documents import Document
    from langchain_core.runnables import RunnableLambda

    corpus = [
        Document(
            page_content="Refunds are available within 30 days with proof of purchase.",
            metadata={"source": "refund-policy"},
        ),
        Document(
            page_content="Shipping takes three to five business days.",
            metadata={"source": "shipping"},
        ),
    ]

    def retrieve(question: str) -> list[Document]:
        return [
            item
            for item in corpus
            if "refund" in question.lower() and "refund" in item.page_content.lower()
        ]

    def compose(documents: list[Document]) -> dict[str, Any]:
        if not documents:
            return {"offline": True, "answer": "No approved evidence found.", "sources": []}
        document = documents[0]
        return {
            "offline": True,
            "answer": f"Within 30 days with proof of purchase [{document.metadata['source']}].",
            "sources": [document.metadata["source"]],
        }

    result = (RunnableLambda(retrieve) | RunnableLambda(compose)).invoke(
        "When can I request a refund?"
    )
    return {"question": "When can I request a refund?", **result}


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--framework", action="store_true")
    args = parser.parse_args(argv)
    print(json.dumps(framework_run() if args.framework else run(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
