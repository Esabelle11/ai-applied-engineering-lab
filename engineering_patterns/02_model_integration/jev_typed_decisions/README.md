# Jev typed decisions

This pattern uses TypeSafe's Jev System One API for a bounded civic-intake
decision. It takes one message as `state`, asks multiple independent typed
questions together, and lets ordinary application code decide whether a report
can enter an **internal review queue**. It never dispatches an incident,
contacts an agency, or offers emergency advice.

The question set borrows the safe boundary from the CitizenAssist reference:
classify intent first, select only from a local category allowlist, and resolve
any destination from application-owned data. It does not copy the attachment's
application code, infrastructure, or configuration.

```text
message
  └─ Jev: intent (Choice), category (Choice), location present (Noul), urgency (Score)
       └─ local threshold and approved-route policy
            └─ NOT_A_REPORT | NEEDS_HUMAN_REVIEW | NEEDS_LOCATION | READY_FOR_REVIEW
```

## Run offline

The default reads a captured System One response; no key or network call is
made.

```bash
uv run --offline --locked python engineering_patterns/02_model_integration/jev_typed_decisions/run.py
```

## Live Jev calls

Set a TypeSafe API key in the shell; never commit it to `.env.example` or this
repository.

```bash
export TYPESAFE_API_KEY="..."
```

Two real integration paths are included because they use different calling
surfaces but normalize to the same `JevDecision` result:

```bash
# Official TypeSafe Python SDK; install the optional dependency first.
uv sync --extra jev
uv run --extra jev python engineering_patterns/02_model_integration/jev_typed_decisions/run.py \
  --live-sdk --message "A pothole is blocking one lane outside the library."

# Direct documented REST call: POST https://api.typesafe.ai/v1/systemone.
uv run python engineering_patterns/02_model_integration/jev_typed_decisions/run.py \
  --live-http --message "Bins on Maple Street have not been collected."
```

`TYPESAFE_DEFAULT_MODEL` selects the model alias for either mode; it defaults to
`jev-latest`. `TYPESAFE_BASE_URL` can point the direct HTTP mode at a compatible
test server ending in `/v1`.

## Why these question types

- **Choice** selects one explicit intent and one category, including `NONE`.
- **Noul** gives the probability that a usable location is present.
- **Score** places urgency on three defined levels.

Jev evaluates the named questions against the same state in one request; they
are independent. The pattern deliberately combines them with deterministic
code rather than asking the model for an action plan. See TypeSafe's
[System One API](https://docs.typesafe.ai/api/system-one), [Python SDK](https://docs.typesafe.ai/sdk/python),
and [question primitives](https://docs.typesafe.ai/primitives).

## Safety and limits

The chosen category is not an official agency classification and a high
probability is not proof. Treat low confidence, `NONE`, and missing location as
review states. This small synthetic example does not handle emergencies,
identity, persistence, authentication, jurisdiction, or real dispatch.
