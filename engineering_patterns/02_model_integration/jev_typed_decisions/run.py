"""Route a civic intake message with TypeSafe Jev's typed System One API.

The default replay is deterministic and never sends data.  Live modes use the
same state and question contract through either the official Python SDK or the
raw REST endpoint.
"""

from __future__ import annotations

import argparse
import json
import os
from collections.abc import Callable, Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from applied_ai.core import ConfigurationError

DEFAULT_MESSAGE = "The streetlight outside 18 River Walk has been off for two nights."
DEFAULT_MODEL = "jev-latest"
DATA_PATH = Path(__file__).with_name("data") / "citizen_intake_replay.json"
API_BASE_URL = "https://api.typesafe.ai/v1"
MIN_CONFIDENCE = 0.75

# These synthetic choices are adapted from the CitizenAssist application's
# intake boundary.  Only this local table determines a review destination.
APPROVED_ROUTES = {
    "STREETLIGHT": "public-works/street-lighting",
    "WASTE_COLLECTION": "environmental-services/waste",
    "ROAD_HAZARD": "public-works/road-safety",
}
INTENT_CHOICES = {
    "REPORT": "The message reports a civic issue or requests it be handled.",
    "INFORMATION": "The message asks for procedures, eligibility, or service information.",
    "CLARIFICATION": "The message appears to report an issue but lacks details needed to act.",
    "CHAT": "The message is casual conversation, acknowledgement, or unrelated text.",
}
CATEGORY_CHOICES = {
    "STREETLIGHT": "A public streetlight is broken, dark, flickering, or unsafe.",
    "WASTE_COLLECTION": "A municipal waste collection or rubbish issue is reported.",
    "ROAD_HAZARD": "A pothole, damaged road, obstruction, or road-safety hazard is reported.",
    "NONE": "No listed civic report category applies.",
}


@dataclass(frozen=True, slots=True)
class JevDecision:
    """Normalized, application-owned result of one typed decision request."""

    intent: str
    category: str
    category_confidence: float
    location_present_probability: float
    urgency_score: float
    outcome: str
    review_destination: str | None
    model: str


def build_questions() -> dict[str, dict[str, Any]]:
    """Return a single mixed Choice/Noul/Score System One question set."""
    return {
        "intent": {
            "type": "choice",
            "instructions": "What is the main intent of `message`?",
            "criteria": INTENT_CHOICES,
        },
        "category": {
            "type": "choice",
            "instructions": "Which civic category best describes `message`? Use NONE when none apply.",
            "criteria": CATEGORY_CHOICES,
        },
        "location_present": {
            "type": "noul",
            "instructions": "Does `message` contain a usable location or landmark for a civic report?",
            "criteria": {
                "true": "A dispatcher could identify where the issue is without guessing.",
                "false": "The message lacks a usable location or landmark.",
            },
        },
        "urgency": {
            "type": "score",
            "instructions": "How urgent is the issue described in `message`?",
            "criteria": [
                "Routine service request with no immediate safety risk.",
                "Needs timely attention but has no stated imminent danger.",
                "Potential immediate public-safety risk requiring human review.",
            ],
        },
    }


def build_payload(message: str, *, model: str = DEFAULT_MODEL) -> dict[str, Any]:
    if not message.strip():
        raise ValueError("Message must not be empty")
    if not model.strip():
        raise ValueError("Model must not be empty")
    return {
        "model": model.strip(),
        "state": {"message": message.strip()},
        "questions": build_questions(),
    }


def _number(value: object, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"Jev answer {field!r} must be numeric")
    result = float(value)
    if not 0.0 <= result <= 1.0 and field != "urgency.score":
        raise ValueError(f"Jev answer {field!r} must be between 0 and 1")
    return result


def _choice(answers: Mapping[str, Any], name: str, allowed: Mapping[str, str]) -> tuple[str, float]:
    answer = answers.get(name)
    if not isinstance(answer, Mapping) or answer.get("type") != "choice":
        raise ValueError(f"Jev response is missing choice answer {name!r}")
    choice = answer.get("choice")
    if not isinstance(choice, str) or choice not in allowed:
        raise ValueError(f"Jev response has invalid {name!r} choice")
    return choice, _number(answer.get("confidence"), f"{name}.confidence")


def normalize_response(response: Mapping[str, Any]) -> JevDecision:
    """Validate Jev's typed answers before local routing policy uses them."""
    model = response.get("model")
    answers = response.get("answers")
    if not isinstance(model, str) or not model.strip() or not isinstance(answers, Mapping):
        raise ValueError("Jev response needs a model and named answers")

    intent, _ = _choice(answers, "intent", INTENT_CHOICES)
    category, category_confidence = _choice(answers, "category", CATEGORY_CHOICES)
    location = answers.get("location_present")
    urgency = answers.get("urgency")
    if not isinstance(location, Mapping) or location.get("type") != "noul":
        raise ValueError("Jev response is missing noul answer 'location_present'")
    if not isinstance(urgency, Mapping) or urgency.get("type") != "score":
        raise ValueError("Jev response is missing score answer 'urgency'")
    location_probability = _number(location.get("noul"), "location_present.noul")
    urgency_score = _number(urgency.get("score"), "urgency.score")

    if intent != "REPORT":
        if category != "NONE":
            raise ValueError("Only REPORT decisions may choose a civic category")
        return JevDecision(
            intent,
            category,
            category_confidence,
            location_probability,
            urgency_score,
            "NOT_A_REPORT",
            None,
            model,
        )
    if category == "NONE" or category_confidence < MIN_CONFIDENCE:
        outcome, destination = "NEEDS_HUMAN_REVIEW", None
    elif location_probability < MIN_CONFIDENCE:
        outcome, destination = "NEEDS_LOCATION", None
    else:
        outcome, destination = "READY_FOR_REVIEW", APPROVED_ROUTES[category]
    return JevDecision(
        intent,
        category,
        category_confidence,
        location_probability,
        urgency_score,
        outcome,
        destination,
        model,
    )


def replay() -> JevDecision:
    """Read a captured System One response without contacting TypeSafe."""
    fixture = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    if not isinstance(fixture, Mapping) or not isinstance(fixture.get("response"), Mapping):
        raise ValueError("Jev replay fixture must contain an object response")
    return normalize_response(fixture["response"])


HttpPost = Callable[[str, Mapping[str, str], Mapping[str, Any]], Mapping[str, Any]]


def _post_json(
    url: str, headers: Mapping[str, str], payload: Mapping[str, Any]
) -> Mapping[str, Any]:
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=dict(headers),
        method="POST",
    )
    try:
        with urlopen(request, timeout=30) as response:  # noqa: S310 - fixed HTTPS endpoint by default
            body = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise RuntimeError(f"TypeSafe API returned HTTP {exc.code}") from exc
    except URLError as exc:
        raise RuntimeError("TypeSafe API request failed") from exc
    if not isinstance(body, Mapping):
        raise ValueError("TypeSafe API returned a non-object response")
    return body


def live_http(
    message: str,
    *,
    api_key: str | None = None,
    model: str = DEFAULT_MODEL,
    post: HttpPost = _post_json,
) -> JevDecision:
    """Call Jev directly through POST /v1/systemone using the documented JSON contract."""
    token = api_key or os.getenv("TYPESAFE_API_KEY")
    if not token:
        raise ConfigurationError("Set TYPESAFE_API_KEY before using --live-http")
    base_url = os.getenv("TYPESAFE_BASE_URL", API_BASE_URL).rstrip("/")
    response = post(
        f"{base_url}/systemone",
        {"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        build_payload(message, model=model),
    )
    return normalize_response(response)


def live_sdk(
    message: str, *, api_key: str | None = None, model: str = DEFAULT_MODEL
) -> JevDecision:
    """Call Jev through TypeSafe's official Python SDK (``typesafe-sdk`` extra)."""
    if not (api_key or os.getenv("TYPESAFE_API_KEY")):
        raise ConfigurationError("Set TYPESAFE_API_KEY before using --live-sdk")
    try:
        from typesafe_sdk import Choice, Noul, Score, TypeSafeClient
    except ImportError as exc:
        raise ConfigurationError("Install the optional SDK: uv sync --extra jev") from exc

    questions = build_questions()
    # Passing the key explicitly keeps this callable usable outside the CLI too;
    # the SDK falls back to TYPESAFE_API_KEY when api_key is None.
    with TypeSafeClient(api_key=api_key) as client:
        sdk_response = client.system_one(
            model=model,
            state={"message": message.strip()},
            questions={
                "intent": Choice(
                    instructions=questions["intent"]["instructions"], criteria=INTENT_CHOICES
                ),
                "category": Choice(
                    instructions=questions["category"]["instructions"], criteria=CATEGORY_CHOICES
                ),
                "location_present": Noul(
                    instructions=questions["location_present"]["instructions"],
                    criteria=questions["location_present"]["criteria"],
                ),
                "urgency": Score(
                    instructions=questions["urgency"]["instructions"],
                    criteria=questions["urgency"]["criteria"],
                ),
            },
        )
    answers = sdk_response.answers
    response = {
        "model": getattr(sdk_response, "model", model),
        "answers": {
            "intent": {
                "type": "choice",
                "choice": answers["intent"].choice,
                "confidence": answers["intent"].confidence,
            },
            "category": {
                "type": "choice",
                "choice": answers["category"].choice,
                "confidence": answers["category"].confidence,
            },
            "location_present": {"type": "noul", "noul": answers["location_present"].noul},
            "urgency": {
                "type": "score",
                "score": answers["urgency"].score,
                "confidence": answers["urgency"].confidence,
            },
        },
    }
    return normalize_response(response)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--live-sdk", action="store_true", help="use the official typesafe-sdk")
    modes.add_argument("--live-http", action="store_true", help="POST directly to /v1/systemone")
    parser.add_argument("--message", default=DEFAULT_MESSAGE)
    parser.add_argument("--model", default=os.getenv("TYPESAFE_DEFAULT_MODEL", DEFAULT_MODEL))
    args = parser.parse_args(argv)

    if args.live_sdk:
        result = live_sdk(args.message, model=args.model)
    elif args.live_http:
        result = live_http(args.message, model=args.model)
    else:
        result = replay()
    print(json.dumps(asdict(result), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
