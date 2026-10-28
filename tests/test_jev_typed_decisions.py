"""Offline contracts for the TypeSafe Jev typed-decision handbook pattern."""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "engineering_patterns/02_model_integration/jev_typed_decisions/run.py"
SPEC = importlib.util.spec_from_file_location("jev_typed_decisions", PATH)
assert SPEC and SPEC.loader
jev = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = jev
SPEC.loader.exec_module(jev)


def test_payload_uses_one_mixed_typed_question_set() -> None:
    payload = jev.build_payload("A pothole is outside the library.")
    assert payload["model"] == "jev-latest"
    assert payload["state"] == {"message": "A pothole is outside the library."}
    assert {item["type"] for item in payload["questions"].values()} == {"choice", "noul", "score"}
    assert payload["questions"]["category"]["criteria"]["NONE"]


def test_replay_resolves_only_a_local_approved_destination() -> None:
    decision = jev.replay()
    assert decision.intent == "REPORT"
    assert decision.category == "STREETLIGHT"
    assert decision.outcome == "READY_FOR_REVIEW"
    assert decision.review_destination == "public-works/street-lighting"


def test_non_report_cannot_select_a_civic_destination() -> None:
    response = {
        "model": "jev-latest",
        "answers": {
            "intent": {"type": "choice", "choice": "CHAT", "confidence": 0.9},
            "category": {"type": "choice", "choice": "ROAD_HAZARD", "confidence": 0.9},
            "location_present": {"type": "noul", "noul": 0.9},
            "urgency": {"type": "score", "score": 1.0, "confidence": 0.9},
        },
    }
    with pytest.raises(ValueError, match="Only REPORT"):
        jev.normalize_response(response)


def test_direct_http_uses_the_documented_endpoint_and_bearer_auth() -> None:
    received: dict[str, Any] = {}

    def post(url: str, headers: dict[str, str], payload: dict[str, Any]) -> dict[str, Any]:
        received.update(url=url, headers=headers, payload=payload)
        return {
            "model": "jev-test",
            "answers": {
                "intent": {"type": "choice", "choice": "REPORT", "confidence": 0.9},
                "category": {"type": "choice", "choice": "ROAD_HAZARD", "confidence": 0.9},
                "location_present": {"type": "noul", "noul": 0.2},
                "urgency": {"type": "score", "score": 2.0, "confidence": 0.9},
            },
        }

    result = jev.live_http("There is a pothole.", api_key="test-key", post=post)
    assert received["url"] == "https://api.typesafe.ai/v1/systemone"
    assert received["headers"]["Authorization"] == "Bearer test-key"
    assert result.outcome == "NEEDS_LOCATION"
    assert result.review_destination is None


def test_sdk_mode_uses_the_same_question_contract(monkeypatch: pytest.MonkeyPatch) -> None:
    received: dict[str, Any] = {}

    class Question:
        def __init__(self, **kwargs: object) -> None:
            self.kwargs = kwargs

    class Answer:
        def __init__(self, **kwargs: object) -> None:
            self.__dict__.update(kwargs)

    class Client:
        def __init__(self, **kwargs: object) -> None:
            received["client"] = kwargs

        def __enter__(self) -> Client:
            return self

        def __exit__(self, *_: object) -> None:
            return None

        def system_one(self, **kwargs: object) -> object:
            received.update(kwargs)
            return types.SimpleNamespace(
                model="jev-sdk-test",
                answers={
                    "intent": Answer(choice="REPORT", confidence=0.95),
                    "category": Answer(choice="WASTE_COLLECTION", confidence=0.92),
                    "location_present": Answer(noul=0.93),
                    "urgency": Answer(score=1.0, confidence=0.8),
                },
            )

    monkeypatch.setitem(
        sys.modules,
        "typesafe_sdk",
        types.SimpleNamespace(
            Choice=Question, Noul=Question, Score=Question, TypeSafeClient=Client
        ),
    )
    result = jev.live_sdk("Waste has not been collected at Maple Street.", api_key="test-key")
    assert received["client"] == {"api_key": "test-key"}
    assert received["model"] == "jev-latest"
    assert set(received["questions"]) == {"intent", "category", "location_present", "urgency"}
    assert result.review_destination == "environmental-services/waste"
