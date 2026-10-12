"""Synthetic civic FAQs with lexical retrieval and source-id citation checks."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass

from applied_ai.knowledge import Document, LexicalRetriever, answer_with_context
from applied_ai.providers.factory import ProviderFactory

SAMPLE_DOCS = (
    Document(
        "city-001",
        "Residents can report broken streetlights using the city's streetlight service form. Provide the pole number and location.",
    ),
    Document(
        "city-002",
        "To report missed rubbish collection, use the waste service form and include your street name.",
    ),
    Document(
        "city-003",
        "Library cards can be requested at the community library front desk with photo identification.",
    ),
)


@dataclass(frozen=True, slots=True)
class CitizenResult:
    answer: str
    retrieved: tuple[str, ...]
    valid_citations: tuple[str, ...]
    unknown_citations: tuple[str, ...]


def run(*, allow_live: bool = False) -> CitizenResult:
    selected = ProviderFactory().create( allow_live=allow_live, mock_text="Use the streetlight service form and include the pole number [city-001].", )

    provider = selected.provider
    try:
        grounded = answer_with_context(
            provider,
            selected.model,
            LexicalRetriever(SAMPLE_DOCS),
            "How can residents report broken streetlights?",
        )
    finally:
        close = getattr(provider, "close", None)
        if callable(close):
            close()
    print("grounded:", grounded)
    cited = tuple(re.findall(r"\[([a-z]+-\d+)\]", grounded.response.text))
    valid = tuple(c for c in cited if c in grounded.retrieved_ids)
    invalid = tuple(c for c in cited if c not in grounded.retrieved_ids)
    return CitizenResult(grounded.response.text, grounded.retrieved_ids, valid, invalid)


if __name__ == "__main__":
    result = run(allow_live="--live" in sys.argv)
    print("Retrieved:", result.retrieved)
    print("Answer:", result.answer)
    print("Validated citation IDs:", result.valid_citations)
    if result.unknown_citations:
        print("WARNING unknown citation IDs:", result.unknown_citations)
