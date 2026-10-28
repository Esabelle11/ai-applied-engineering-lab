"""Playground API boundaries, whitelisted execution, access control, and offline invariants."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from apps.playground.backend.app import PlaygroundConfig, create_app
from apps.playground.backend.service import (
    EXAMPLES,
    compare,
    discover_patterns,
    execute,
)

AUTH_TOKEN = "playground-testing-token-that-is-long"
ORIGIN = {"origin": "http://testserver"}


def client(
    *, max_units: int = 20, token: str | None = None, enable_live: bool = False
) -> TestClient:
    return TestClient(
        create_app(
            PlaygroundConfig(
                token=token,
                enable_live=enable_live,
                max_units=max_units,
            )
        )
    )


def test_pattern_discovery_is_registry_not_executable_code() -> None:
    patterns = discover_patterns()
    assert len(patterns) >= 14
    assert any(p["id"] == "model_integration.basic_api_integration" for p in patterns)
    assert all("entrypoint" not in p and "script" not in p for p in patterns)
    assert {e.id for e in EXAMPLES} == {
        "generation",
        "prompt_template",
        "retry",
        "grounded_retrieval",
        "state_graph",
        "verification",
    }


@pytest.mark.parametrize("example_id", [e.id for e in EXAMPLES])
def test_all_curated_examples_are_offline_and_bounded(example_id: str) -> None:
    argument = "Compute 17 * 23 + 9" if example_id == "verification" else "passport renewal"
    result = execute(example_id, argument)
    assert result["example"] == example_id
    assert result["provider"] == "mock"
    assert result["cost_usd"] is None
    assert result["trace"]
    assert result["output"]
    assert result["latency_ms"] >= 0


def test_validation_and_recovery_traces() -> None:
    retry = execute("retry", "test")
    assert retry["attempts"] == 2
    assert retry["trace"][0]["status"] == "rate_limit"
    reasoning = execute("verification", "Compute 17 * 23 + 9")
    assert reasoning["validation"]["status"] == "passed"
    assert reasoning["attempts"] == 2


def test_grounded_retrieval_blocks_unmatched_questions() -> None:
    with pytest.raises(LookupError):
        execute("grounded_retrieval", "monochromatic quasar galactic core")


def test_invalid_inputs_and_unapproved_examples() -> None:
    for bad in ("", " ", "a" * 501):
        with pytest.raises(ValueError):
            execute("generation", bad)
    with pytest.raises(ValueError):
        execute("../../scripts/check_no_secrets.py", "some prompt")
    with pytest.raises(ValueError):
        execute("state_graph", "x", live=True)
    with pytest.raises(ValueError):
        compare("nonexistent", "test")


def test_comparison_same_fault_sequence_and_no_code_execution() -> None:
    result = compare("retry_recovery", "hello")
    assert result["results"][0]["status"] == "error"
    assert result["results"][1]["status"] == "completed"
    assert [r["attempts"] for r in result["results"]] == [1, 2]
    prompts = compare("prompt_construction", "attention mechanisms")
    assert prompts["results"][0]["attempts"] == 0
    assert prompts["results"][1]["output"].startswith("Explain attention mechanisms")


def test_http_navigation_and_data() -> None:
    with client() as http:
        page = http.get("/")
        assert page.status_code == 200 and "Engineering AI" in page.text
        assert http.get("/static/app.js").status_code == 200
        assert http.get("/api/health").json() == {"status": "ok"}
        catalog = http.get("/api/catalog").json()
        assert len(catalog["examples"]) == 6
        assert len(catalog["comparisons"]) == 2
        assert "default-src 'none'" in page.headers["content-security-policy"]
        assert page.headers["x-frame-options"] == "DENY"


def test_http_run_and_comparison_cost_two_budget_units() -> None:
    with client(max_units=3) as http:
        first = http.post(
            "/api/run", headers=ORIGIN, json={"example_id": "retry", "value": "example prompt"}
        )
        assert first.status_code == 200
        assert first.json()["result"]["attempts"] == 2
        assert first.json()["quota"]["remaining"] == 2
        pair = http.post(
            "/api/compare",
            headers=ORIGIN,
            json={"comparison_id": "retry_recovery", "value": "example prompt"},
        )
        assert pair.status_code == 200
        assert pair.json()["quota"]["remaining"] == 0
        denied = http.post(
            "/api/run", headers=ORIGIN, json={"example_id": "generation", "value": "example prompt"}
        )
        assert denied.status_code == 429


def test_auth_origin_and_token_controls() -> None:
    with client(token=AUTH_TOKEN) as http:
        assert http.get("/api/catalog").status_code == 401
        assert (
            http.get("/api/catalog", headers={"Authorization": "Bearer incorrect"}).status_code
            == 401
        )
        good = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        assert http.get("/api/catalog", headers=good).status_code == 200
        cross_site = {**good, "Origin": "https://hostile.invalid"}
        denied = http.post(
            "/api/run", headers=cross_site, json={"example_id": "generation", "value": "Hello"}
        )
        assert denied.status_code == 403
        assert (
            http.post(
                "/api/run",
                headers={**good, **ORIGIN},
                json={"example_id": "generation", "value": "Hello"},
            ).status_code
            == 200
        )


def test_no_token_requires_same_origin_write() -> None:
    with client() as http:
        result = http.post("/api/run", json={"example_id": "generation", "value": "Hello"})
        assert result.status_code == 403
        assert (
            http.post(
                "/api/run", headers=ORIGIN, json={"example_id": "generation", "value": "Hello"}
            ).status_code
            == 200
        )


def test_live_is_disabled_and_never_calls_provider() -> None:
    with patch("apps.playground.backend.service._live_generate") as generate, client() as http:
        response = http.post(
            "/api/run",
            headers=ORIGIN,
            json={"example_id": "generation", "value": "test", "live": True},
        )
        assert response.status_code == 403
        generate.assert_not_called()


def test_live_config_needs_long_token_and_explicit_enable() -> None:
    with pytest.raises(ValueError):
        PlaygroundConfig(enable_live=True)
    with pytest.raises(ValueError):
        PlaygroundConfig(token="short", enable_live=True)
    config = PlaygroundConfig(token=AUTH_TOKEN, enable_live=True)
    assert config.enable_live


def test_browser_has_no_generated_code_execution_route() -> None:
    with client() as http:
        assert (
            http.post(
                "/api/execute-python", headers=ORIGIN, json={"code": "print('hello')"}
            ).status_code
            == 404
        )
        assert (
            http.post(
                "/api/run",
                headers=ORIGIN,
                json={"example_id": "../../case_studies/loop_tool_agent/run.py", "value": "oops"},
            ).status_code
            == 400
        )
        assert (
            http.post(
                "/api/compare",
                headers=ORIGIN,
                json={"comparison_id": "../../etc/passwd", "value": "oops"},
            ).status_code
            == 400
        )


def test_frontend_uses_safe_dom_and_local_assets() -> None:
    frontend = Path(__file__).resolve().parents[1] / "apps/playground/frontend"
    js = (frontend / "app.js").read_text(encoding="utf-8")
    assert "innerHTML" not in js
    assert "localStorage" not in js
    assert "eval(" not in js
    html = (frontend / "index.html").read_text(encoding="utf-8")
    assert "https://" not in html


def test_remote_client_without_token_is_denied() -> None:
    with TestClient(create_app(PlaygroundConfig()), client=("203.0.113.10", 51000)) as http:
        assert http.get("/api/catalog").status_code == 403


def test_live_request_requires_full_authorization_and_is_bounded() -> None:
    fake_result = execute("generation", "fixture")
    with (
        patch(
            "apps.playground.backend.service._live_generate", return_value=fake_result
        ) as generator,
        client(token=AUTH_TOKEN, enable_live=True) as http,
    ):
        data = {"example_id": "generation", "value": "Explain RAG", "live": True}
        assert http.post("/api/run", headers=ORIGIN, json=data).status_code == 401
        accepted = http.post(
            "/api/run", headers={"Authorization": f"Bearer {AUTH_TOKEN}", **ORIGIN}, json=data
        )
        assert accepted.status_code == 200
        generator.assert_called_once_with("generation", "Explain RAG")
        denied = http.post(
            "/api/run",
            headers={"Authorization": f"Bearer {AUTH_TOKEN}", **ORIGIN},
            json={
                "example_id": "state_graph",
                "value": "Should coding be mandatory?",
                "live": True,
            },
        )
        assert denied.status_code == 400
