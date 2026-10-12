# CitizenAssist — Source-Aware FAQ Reference

**Problem:** Assistants need to retrieve source text instead of inventing administrative instructions.

**Architecture:** Synthetic `Document` fixtures → `LexicalRetriever` (04) → `answer_with_context` (04) → `LLMProvider` (02) → source-ID validation.

```sh
uv run python -m case_studies.citizen_assist.run
uv run python -m case_studies.citizen_assist.run --live  # opt-in
```

Citations are checked **only** for whether their IDs appear in the retrieved set. This does **not** prove claims are factually grounded; the model can still invent unsupported facts. The text is synthetic, not official civic guidance.

**Tests:** `tests/test_phase4_cases.py::test_retrieval_and_grounding_citations`.

**Limitations:** Token-overlap retrieval instead of embeddings/pgvector, no multilingual workflows, source ranking quality evaluation, or production prompt-injection defense. Real deployments need human review and official source verification.
