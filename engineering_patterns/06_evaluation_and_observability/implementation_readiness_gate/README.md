# Implementation readiness gate

## Problem and context

Before handing a specification to a coding agent, teams need a clear answer to
“what is still missing?” A model-produced quality percentage can sound more
certain than it is and can conceal a critical unresolved decision.

## Mechanism and implementation

Declare the checks appropriate for the project—such as requirements coverage,
security decisions, and acceptance criteria—then call `assess_readiness`. It
reports a simple coverage score but fails closed when any required check fails
or when the caller declares an unresolved blocker.

## Run offline

```sh
uv run --offline --locked python engineering_patterns/06_evaluation_and_observability/implementation_readiness_gate/run.py
```

## Alternatives and tradeoffs

An LLM-as-judge can assess prose completeness, while a checklist is auditable
and repeatable. Combine both when needed: validate the judge's output, expose
its rubric, and keep explicit hard blockers outside the model score.

## Failure modes

The reported score is coverage of caller-declared checks, not the probability
of successful code generation. A 100% score cannot prove the requirements are
correct or complete. Teams must choose the checks, record exceptions, and
apply their own release/security policies.

## Reuse

Use as a transparent gate between specification review and code generation,
especially when a human needs to decide whether to accept remaining risk.
