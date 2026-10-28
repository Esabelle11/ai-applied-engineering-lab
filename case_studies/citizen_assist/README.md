# CitizenAssist — One-Call Intake and Local Routing

**Problem:** A civic intake assistant must decide whether a message is a report,
ask for missing details, and avoid letting an LLM invent an agency destination.

**Architecture:** message → one structured LLM decision → schema/business-rule
validation → local approved route lookup. The model selects only a category; the
application resolves the agency destination from
[`data/agency_routes.json`](data/agency_routes.json). This example never creates
an incident, sends a webhook, or contacts an agency.

```sh
# Always available: saved LLM output plus deterministic routing data
uv run python -m case_studies.citizen_assist.run --replay

# One opt-in call to the provider configured in .env
uv run python -m case_studies.citizen_assist.run --live \
  --message "A streetlight at 18 River Walk, pole SL-204, is out."
```

There is intentionally **no mock-provider path**. If no real provider is
configured, use `--replay`; it reads
[`data/streetlight_report_replay.json`](data/streetlight_report_replay.json), a
synthetic captured LLM decision, and validates it exactly as live output is
validated.

**Tests:** `tests/test_case_studies.py::test_citizen_assist_replays_saved_routing_decision`.

**Limitations:** The route table, message, and replay response are fictional.
Production deployments need authenticated persistence, official agency data,
human review, emergency guidance, multilingual handling, abuse safeguards, and
an audited dispatch integration.

## Full application reference

For the complete CitizenAssist chat application, see
[CitizenAssist AI](https://github.com/Esabelle11/CitizenAssist-AI-). It extends
this intentionally small example into a multimodal, multi-turn civic-assistance
workflow:

```text
Citizen input
  → Text, image, audio, or video processing
  → Intent and situation analysis
  → Interactive information gathering
  → Incident reporting and routing
  → Conversation persistence
```

The full application includes media evidence extraction, GPS-aware workflows,
specialised response paths, and Supabase-backed conversation storage. This case
study focuses only on the smaller, auditable boundary between one LLM decision
and an approved local routing table.
