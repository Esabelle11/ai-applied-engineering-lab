# PromptForge — One-Agent Prompt Linter

This is a small study case for learning one useful AI-engineering pattern:
**turn an incomplete developer request into a structured, reviewable prompt
before code generation.** It follows the attached Prompt Linter API route and
uses one LLM agent, one output contract, and one real captured example.

## Start here

| Step | Do this | What you learn | Calls an LLM? |
| --- | --- | --- | --- |
| 1 | Run --replay | Read a real output for a portfolio webpage request. | No |
| 2 | Run --show-design | Inspect the exact system instruction and JSON contract. | No |
| 3 | Read run.py top to bottom | See prompt → schema → request → validation → CLI safety. | No |
| 4 | Run --live | Compare a fresh result for the same or another request. | Yes, one call |

```
# Step 1 — replay the real saved output
uv run python -m case_studies.prompt_forge.run --replay

# Step 2 — inspect the agent design
uv run python -m case_studies.prompt_forge.run --show-design
```

## The learning flow

```
developer prompt
      ↓
Prompt Linter instruction
      ↓
schema-constrained JSON response
      ↓
issues + suggestions + improved prompt + reasons
```

The complete study is deliberately in [run.py](run.py). Its sections are
numbered as study steps, so readers can follow the flow without jumping across
multiple agent files.

## Captured portfolio example

[data/portfolio_webpage_easy_analysis.json](data/portfolio_webpage_easy_analysis.json)
is a real saved PromptForge response for:

> Build me a portfolio webpage for software engineering purpose.

It shows the difference between a vague idea and a more useful implementation
prompt. The suggested React, Tailwind, Vercel, and contact-form choices are
recommendations from one LLM run—not universal requirements.

## Run live

Configure a non-mock provider in .env, then authorize the single call:

```
uv sync --group dev --extra providers
uv run python -m case_studies.prompt_forge.run --live
```

Try your own request:

```
uv run python -m case_studies.prompt_forge.run --live \
  --prompt "Build a portfolio site for a UX designer."
```

If no live provider/model is configured, the script does not create a mock
model. It tells readers to use --replay instead.

## What the contract teaches

The response must validate against five fields:

- score: a 0–100 completeness assessment;
- issues: title, severity, and description;
- suggestions: clarification or improvement ideas;
- improvedPrompt: a rewritten implementation request;
- explanation: why each important change was made.

OpenAI uses native schema-constrained output through the lab provider. Other
supported providers receive the schema in the prompt and are validated locally.
Invalid JSON fails clearly; the study never silently strips code fences or
guesses at malformed output.

## Limits

This is a prompt-quality aid, not a guarantee that generated software will be
secure, complete, or maintainable. Review the improved prompt before using it,
especially when the model suggests technologies, deployment targets, or
integrations. Live calls may consume quota or money.

## Full application reference

For the complete application, see [PromptForge AI Advanced](https://github.com/Esabelle11/PromptForge-Ensemble). It extends this intentionally small example into a provider-flexible prompt-engineering workflow:

```
Developer idea
  → Prompt analysis and missing-requirement review
  → Structured software specification
  → Production-ready implementation prompt
  → Optional OpenAI project-generation workflow
  → AI coding agent
```

The full application supports prompt analysis, specification building,
production-prompt generation, provider/model selection, and an optional
project-generation path. This case study keeps the boundary deliberately
small: one prompt-linter instruction, one schema-validated response, captured
replay data, and an explicitly authorized live LLM call. Start here to learn
the core pattern before exploring the broader application workflow.

The replay file is historical model output, not a verified technical
recommendation. Treat its technology, hosting, and integration suggestions as
one possible response to review—not as requirements for every portfolio site.
