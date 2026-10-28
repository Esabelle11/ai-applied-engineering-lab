# Requirements clarification

## Problem and context

An implementation prompt can look detailed while still omitting decisions that
change the architecture: identity, data ownership, integrations, or deployment.
Asking every possible question overwhelms the user; asking none forces an AI
coding agent to invent product decisions.

## Mechanism and implementation

Represent each detected gap as a named question with a human-assigned impact
score. `select_clarifying_questions` excludes areas the user already answered,
orders the remainder by impact, and applies an eight-question ceiling.
`merge_requirement_answers` then keeps only non-empty answers to the selected
questions. A model may identify candidate gaps, but this selection policy stays
deterministic and reviewable.

## Run offline

```sh
uv run --offline --locked python engineering_patterns/01_prompt_engineering/requirements_clarification/run.py
```

## Alternatives and tradeoffs

A fixed questionnaire is cheaper and more consistent, but can ask irrelevant
questions. An LLM-led interview can adapt to the idea, but needs schema
validation, prompt-injection controls, and evaluation for duplicate or leading
questions. Impact is a prioritization aid, not an objective measure.

## Failure modes

The helper cannot determine whether a gap list is complete or whether an answer
is true. It rejects invalid impact scores and question limits. Production
systems should persist answers, support privacy controls, and let users decline
or revise assumptions.

## Reuse

Use this before specification compilation when missing decisions would change
what the coding agent builds. It is not useful for tiny, fully constrained
transformations where the input contract is already complete.
