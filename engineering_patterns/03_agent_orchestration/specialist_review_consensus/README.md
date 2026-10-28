# Specialist review consensus

## Problem and context

Architecture, security, and QA reviews can run independently, but their results
often repeat the same concern with different severity. Passing all raw output
to a coding agent hides priorities and loses who raised an issue.

## Mechanism and implementation

Each named specialist returns typed findings. `synthesize_reviews` groups
findings with the same normalized title, retains the highest severity, preserves
the contributing specialists, and sorts the final list from critical to low.
It is designed to follow parallel review execution such as `run_parallel`.

## Run offline

```sh
uv run --offline --locked python engineering_patterns/03_agent_orchestration/specialist_review_consensus/run.py
```

## Alternatives and tradeoffs

An engineering lead or an LLM can resolve semantic duplicates and conflicting
recommendations better than exact-title grouping. That flexibility costs more
and must be evaluated. This primitive deliberately performs no model call and
does not claim that agreement means correctness.

## Failure modes

Only equal normalized titles are deduplicated. A critical concern can still be
missed if no specialist raises it, and conflicting recommendations under the
same title need a human decision. Production workflows need reviewer identity,
authorization, durable audit history, and a way to record resolutions.

## Reuse

Use after independent specialist reviews and before a final handoff document.
Do not use it as a voting algorithm for factual answers; use answer-specific
consensus or an independent verifier instead.
