from __future__ import annotations

import argparse
import json
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from applied_ai.core import (
    ConfigurationError,
    LLMProvider,
    LLMRequest,
    Message,
    StructuredOutputSpec,
)
from applied_ai.core.structured import parse_structured_output
from applied_ai.providers.factory import ProviderFactory

DEFAULT_MESSAGE = "A streetlight at 18 River Walk, pole SL-204, has been out for two nights."
DATA_DIR = Path(__file__).resolve().parent / "data"
ROUTES_PATH = DATA_DIR / "agency_routes.json"
REPLAY_PATH = DATA_DIR / "streetlight_report_replay.json"


@dataclass(frozen=True, slots=True)
class AgencyRoute:
    """An approved, synthetic destination for one report category."""

    category: str
    agency_name: str
    channel: str
    destination: str


@dataclass(frozen=True, slots=True)
class AssistanceDecision:
    """The validated output of the one CitizenAssist LLM call."""

    intent: str
    category: str
    urgency: str
    response: str
    requires_immediate_gps: bool
    extracted_entities: Mapping[str, Any]
    missing_fields: tuple[str, ...]
    ready_for_submission: bool
    follow_up_question: str | None
    rationale: str


@dataclass(frozen=True, slots=True)
class CitizenAssistResult:
    message: str
    decision: AssistanceDecision
    route: AgencyRoute | None
    routing_status: str
    provider: str
    model: str


def _load_routes() -> tuple[AgencyRoute, ...]:
    """Load the only destinations this example is permitted to return."""
    payload = json.loads(ROUTES_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping) or not isinstance(payload.get("routes"), list):
        raise ValueError("CitizenAssist agency-routes fixture needs a routes list")

    routes: list[AgencyRoute] = []
    for item in payload["routes"]:
        if not isinstance(item, Mapping):
            raise ValueError("Every CitizenAssist route must be an object")
        values = tuple(
            item.get(key) for key in ("category", "agencyName", "channel", "destination")
        )
        if not all(isinstance(value, str) and value.strip() for value in values):
            raise ValueError("Every CitizenAssist route needs non-empty string fields")
        routes.append(AgencyRoute(values[0], values[1], values[2], values[3]))

    if not routes or len({route.category for route in routes}) != len(routes):
        raise ValueError("CitizenAssist route categories must be present and unique")
    return tuple(routes)


def _decision_schema(categories: Sequence[str]) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "intent": {
                "type": "string",
                "enum": ["CHAT", "INFORMATION", "CLARIFICATION", "REPORT"],
            },
            "category": {"type": "string", "enum": ["NONE", *categories]},
            "urgency": {
                "type": "string",
                "enum": ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
            },
            "response": {"type": "string", "minLength": 1, "maxLength": 1200},
            "requiresImmediateGps": {"type": "boolean"},
            "extractedEntities": {"type": "object"},
            "missingFields": {"type": "array", "items": {"type": "string"}},
            "readyForSubmission": {"type": "boolean"},
            "followUpQuestion": {"type": ["string", "null"]},
            "rationale": {"type": "string", "minLength": 1, "maxLength": 600},
        },
        "required": [
            "intent",
            "category",
            "urgency",
            "response",
            "requiresImmediateGps",
            "extractedEntities",
            "missingFields",
            "readyForSubmission",
            "followUpQuestion",
            "rationale",
        ],
        "additionalProperties": False,
    }


def _decision_from_payload(
    payload: Mapping[str, Any], routes: Sequence[AgencyRoute]
) -> AssistanceDecision:
    categories = tuple(route.category for route in routes)
    validated = parse_structured_output(
        json.dumps(dict(payload)),
        StructuredOutputSpec("citizen_assist_decision", _decision_schema(categories)),
        provider="citizen-assist",
    )
    decision = AssistanceDecision(
        intent=validated["intent"],
        category=validated["category"],
        urgency=validated["urgency"],
        response=validated["response"],
        requires_immediate_gps=validated["requiresImmediateGps"],
        extracted_entities=validated["extractedEntities"],
        missing_fields=tuple(validated["missingFields"]),
        ready_for_submission=validated["readyForSubmission"],
        follow_up_question=validated["followUpQuestion"],
        rationale=validated["rationale"],
    )
    if decision.intent != "REPORT" and decision.category != "NONE":
        raise ValueError("Only REPORT decisions may select a route category")
    if decision.intent == "REPORT" and decision.category == "NONE":
        raise ValueError("REPORT decisions must select an approved category")
    if decision.ready_for_submission and decision.missing_fields:
        raise ValueError("Ready reports cannot have missing fields")
    if (
        decision.intent == "REPORT"
        and not decision.ready_for_submission
        and (not decision.follow_up_question or not decision.follow_up_question.strip())
    ):
        raise ValueError("Incomplete reports need a follow-up question")
    return decision


def _resolve_route(
    decision: AssistanceDecision, routes: Sequence[AgencyRoute]
) -> tuple[AgencyRoute | None, str]:
    """Resolve a validated report to data-owned routing; never dispatch externally."""
    if decision.intent != "REPORT":
        return None, "NOT_A_REPORT"
    if not decision.ready_for_submission:
        return None, "NEEDS_MORE_INFORMATION"
    route = next((item for item in routes if item.category == decision.category), None)
    if route is None:  # Defensive guard if routing data changes after validation.
        raise ValueError(f"No approved route exists for {decision.category!r}")
    return route, "READY_FOR_REVIEW"


def _system_instruction(routes: Sequence[AgencyRoute]) -> str:
    categories = ", ".join(route.category for route in routes)
    return f"""You are CitizenAssist, a concise public-service intake assistant.
Classify one user message and draft a helpful reply. This demo does not create
incidents, contact agencies, make emergency calls, or provide official advice.
Ask for missing details instead of assuming them. Do not claim a report was sent.

Use REPORT only when the user is reporting a municipal issue. REPORT categories
must be one of: {categories}. Use category NONE for every other intent. A report
is ready only when its location and a concise problem description are present.
Return only JSON that matches the requested schema."""


def generate_decision(
    provider: LLMProvider, model: str, message: str, routes: Sequence[AgencyRoute]
) -> AssistanceDecision:
    """Make the single live LLM call and validate its structured result."""
    if not message.strip():
        raise ValueError("Message must not be empty")
    output_spec = StructuredOutputSpec(
        "citizen_assist_decision", _decision_schema(tuple(route.category for route in routes))
    )
    response = provider.generate(
        LLMRequest(
            model=model,
            messages=(
                Message("system", _system_instruction(routes)),
                Message("user", message.strip()),
            ),
            max_output_tokens=800,
            temperature=0.1,
            response_format=output_spec if provider.capabilities.structured_output else None,
        )
    )
    payload = response.parsed_output
    if payload is None:
        payload = parse_structured_output(response.text, output_spec, provider=response.provider)
    return _decision_from_payload(payload, routes)


def replay() -> CitizenAssistResult:
    """Load a saved LLM report decision and resolve it with local fixture data."""
    capture = json.loads(REPLAY_PATH.read_text(encoding="utf-8"))
    if not isinstance(capture, Mapping):
        raise ValueError("CitizenAssist replay fixture must be an object")
    message, payload = capture.get("message"), capture.get("result")
    if not isinstance(message, str) or not message.strip() or not isinstance(payload, Mapping):
        raise ValueError("CitizenAssist replay needs a message and object result")
    routes = _load_routes()
    decision = _decision_from_payload(payload, routes)
    route, status = _resolve_route(decision, routes)
    return CitizenAssistResult(message, decision, route, status, "replay", "stored-fixture")


def run(*, message: str = DEFAULT_MESSAGE, allow_live: bool = False) -> CitizenAssistResult:
    """Run one configured live LLM call; no mock-provider fallback exists."""
    factory = ProviderFactory()
    if factory.kind == "mock":
        raise ConfigurationError(
            "No live LLM model is configured. Use --replay to inspect the stored CitizenAssist result."
        )
    if not allow_live:
        raise ConfigurationError("Live model detected: pass --live, or use --replay instead.")

    routes = _load_routes()
    selected = factory.create(allow_live=True)
    provider = selected.provider
    try:
        decision = generate_decision(provider, selected.model, message, routes)
        route, status = _resolve_route(decision, routes)
        return CitizenAssistResult(message, decision, route, status, provider.name, selected.model)
    finally:
        close = getattr(provider, "close", None)
        if callable(close):
            close()


def _print_result(result: CitizenAssistResult) -> None:
    print("# CitizenAssist result\n")
    print(json.dumps(asdict(result), indent=2, ensure_ascii=False))


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run the one-call CitizenAssist routing example.")
    parser.add_argument("--live", action="store_true", help="Authorize one configured LLM call.")
    parser.add_argument(
        "--replay", action="store_true", help="Print stored output; no provider call."
    )
    parser.add_argument("--message", default=DEFAULT_MESSAGE, help="Citizen message for --live.")
    args = parser.parse_args(argv)

    if args.replay:
        _print_result(replay())
        return

    factory = ProviderFactory()
    if factory.kind == "mock":
        print("No live LLM model is configured. Run with --replay to inspect the saved example.")
        return
    if not args.live:
        print("A live LLM model is configured. Run with --live, or use --replay instead.")
        return
    _print_result(run(message=args.message, allow_live=True))


if __name__ == "__main__":
    main()
