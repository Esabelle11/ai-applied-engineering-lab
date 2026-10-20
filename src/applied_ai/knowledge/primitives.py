"""Deterministic, dependency-light knowledge and context utilities."""

from __future__ import annotations

import hashlib
import math
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from applied_ai.knowledge import Document, LexicalRetriever


def ingest_records(records: Sequence[Mapping[str, str]]) -> tuple[Document, ...]:
    """Validate simple ID/text records before they enter a retrieval index."""
    documents = tuple(Document(record["id"], record["text"]) for record in records)
    if len({document.id for document in documents}) != len(documents):
        raise ValueError("Document identifiers must be unique")
    return documents


def chunk_text(text: str, *, max_chars: int = 400, overlap: int = 40) -> tuple[str, ...]:
    """Create bounded, overlapping character chunks without silently dropping text."""
    if not text.strip() or max_chars < 1 or not 0 <= overlap < max_chars:
        raise ValueError("text, max_chars, and overlap are invalid")
    return tuple(text[start : start + max_chars] for start in range(0, len(text), max_chars - overlap))


def embed_text(text: str, *, dimensions: int = 1024) -> tuple[float, ...]:
    """Hash-token embedding for deterministic demos; it is not a semantic model embedding."""
    if not text.strip() or dimensions < 2:
        raise ValueError("text must be non-empty and dimensions must be at least 2")
    vector = [0.0] * dimensions
    for token in re.findall(r"[a-z0-9]+", text.lower()):
        index = int.from_bytes(hashlib.sha256(token.encode()).digest()[:4], "big") % dimensions
        vector[index] += 1.0
    magnitude = math.sqrt(sum(value * value for value in vector))
    return tuple(value / magnitude for value in vector) if magnitude else tuple(vector)


def cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right) or not left:
        raise ValueError("Vectors must be non-empty and have matching dimensions")
    return sum(a * b for a, b in zip(left, right, strict=True))


class VectorRetriever:
    def __init__(self, documents: Sequence[Document], *, dimensions: int = 1024) -> None:
        if not documents or dimensions < 2:
            raise ValueError("Documents and a valid dimension count are required")
        self.documents = tuple(documents)
        self.dimensions = dimensions
        self._vectors = {document.id: embed_text(document.text, dimensions=dimensions) for document in documents}

    def search(self, query: str, *, limit: int = 3) -> tuple[Document, ...]:
        if not query.strip() or limit < 1:
            raise ValueError("query must be non-empty and limit positive")
        query_vector = embed_text(query, dimensions=self.dimensions)
        ranked = sorted(
            self.documents,
            key=lambda document: (-cosine_similarity(query_vector, self._vectors[document.id]), document.id),
        )
        return tuple(ranked[:limit])


def hybrid_search(documents: Sequence[Document], query: str, *, limit: int = 3) -> tuple[Document, ...]:
    """Fuse lexical and hash-vector rankings using deterministic reciprocal ranks."""
    lexical = LexicalRetriever(documents).search(query, limit=len(documents))
    vector = VectorRetriever(documents).search(query, limit=len(documents))
    scores: dict[str, float] = {}
    for ranking in (lexical, vector):
        for rank, document in enumerate(ranking, 1):
            scores[document.id] = scores.get(document.id, 0.0) + 1 / (60 + rank)
    by_id = {document.id: document for document in documents}
    return tuple(by_id[document_id] for document_id in sorted(scores, key=lambda item: (-scores[item], item))[:limit])


def rerank(query: str, candidates: Sequence[Document], *, limit: int = 3) -> tuple[Document, ...]:
    """Rerank candidates by exact query-term overlap with stable ties."""
    if not query.strip() or limit < 1:
        raise ValueError("query must be non-empty and limit positive")
    terms = set(re.findall(r"[a-z0-9]+", query.lower()))
    return tuple(sorted(candidates, key=lambda doc: (-len(terms & set(re.findall(r"[a-z0-9]+", doc.text.lower()))), doc.id))[:limit])


def rewrite_query(query: str) -> str:
    """Remove common conversational filler while preserving the user's concrete terms."""
    if not query.strip():
        raise ValueError("query must be non-empty")
    rewritten = re.sub(
        r"^(could you tell me |can you tell me |please |could you |can you |tell me )",
        "",
        query.strip(),
        flags=re.IGNORECASE,
    )
    return rewritten.rstrip("?").strip()


@dataclass(frozen=True, slots=True)
class ContextWindow:
    text: str
    included_ids: tuple[str, ...]
    omitted_ids: tuple[str, ...]


def build_context(documents: Sequence[Document], *, max_chars: int) -> ContextWindow:
    if max_chars < 1:
        raise ValueError("max_chars must be positive")
    parts: list[str] = []
    included: list[str] = []
    omitted: list[str] = []
    used = 0
    for document in documents:
        part = f"[{document.id}] {document.text}\n"
        if used + len(part) <= max_chars:
            parts.append(part)
            used += len(part)
            included.append(document.id)
        else:
            omitted.append(document.id)
    return ContextWindow("".join(parts).rstrip(), tuple(included), tuple(omitted))


class LongTermMemory:
    """Small in-memory fact store with lexical retrieval; no hidden persistence."""

    def __init__(self) -> None:
        self._facts: dict[str, Document] = {}

    def remember(self, key: str, text: str) -> None:
        if key in self._facts:
            raise ValueError(f"Memory already exists: {key}")
        self._facts[key] = Document(key, text)

    def recall(self, query: str, *, limit: int = 3) -> tuple[Document, ...]:
        if not self._facts:
            return ()
        return LexicalRetriever(tuple(self._facts.values())).search(query, limit=limit)


def citations_supported(answer: str, source_ids: Sequence[str]) -> bool:
    """Require each bracketed citation in an answer to name a supplied source."""
    cited = re.findall(r"\[([^\]]+)\]", answer)
    return bool(cited) and all(citation in set(source_ids) for citation in cited)


@dataclass(frozen=True, slots=True)
class RetrievalMetrics:
    precision_at_k: float
    recall_at_k: float


def measure_retrieval(retrieved_ids: Sequence[str], relevant_ids: Sequence[str], *, k: int) -> RetrievalMetrics:
    if k < 1 or not relevant_ids:
        raise ValueError("k must be positive and relevant_ids must be non-empty")
    top = set(retrieved_ids[:k])
    relevant = set(relevant_ids)
    hits = len(top & relevant)
    return RetrievalMetrics(hits / k, hits / len(relevant))
