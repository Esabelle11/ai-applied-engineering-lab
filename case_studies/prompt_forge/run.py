from __future__ import annotations

import argparse
import json
from collections.abc import Mapping
from dataclasses import dataclass
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

DEFAULT_PROMPT = "Build me a portfolio webpage for software engineering purpose."
DATA_PATH = Path(__file__).resolve().parent / "data" / "portfolio_webpage_easy_analysis.json"

# Study step 1: this is the complete instruction given to the one LLM agent.
PROMPT_LINTER_SYSTEM = """You are a Prompt Linter: a developer-experience tool
that helps developers write better prompts for AI coding agents. Analyze the
developer's request before code generation. Evaluate product purpose, target
users, required features, technical requirements, architecture, data or
integrations, UI/UX, security, scalability, and expected output.

For improvedPrompt, rewrite the request as a structured software specification.
Preserve the original intent. Add missing detail only where appropriate. Do not
invent unnecessary features. Return no code."""


def _object_schema(properties: dict[str, Any], required: tuple[str, ...]) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": properties,
        "required": list(required),
        "additionalProperties": False,
    }


# Study step 2: this contract makes the LLM result safe to display and reuse.
ISSUE_SCHEMA = _object_schema(
    {
        "title": {"type": "string", "minLength": 1},
        "severity": {"type": "string", "enum": ["high", "medium", "low"]},
        "description": {"type": "string", "minLength": 1},
    },
    ("title", "severity", "description"),
)

EXPLANATION_SCHEMA = _object_schema(
    {
        "change": {"type": "string", "minLength": 1},
        "reason": {"type": "string", "minLength": 1},
    },
    ("change", "reason"),
)

ANALYSIS_SCHEMA = _object_schema(
    {
        "score": {"type": "integer", "minimum": 0, "maximum": 100},
        "issues": {"type": "array", "items": ISSUE_SCHEMA},
        "suggestions": {"type": "array", "items": {"type": "string"}},
        "improvedPrompt": {"type": "string", "minLength": 1},
        "explanation": {"type": "array", "items": EXPLANATION_SCHEMA},
    },
    ("score", "issues", "suggestions", "improvedPrompt", "explanation"),
)


@dataclass(frozen=True, slots=True)
class PromptLinterResult:
    prompt: str
    analysis: Mapping[str, Any]
    provider: str
    model: str


# Study step 3: replay a captured real result without pretending it is live.
def captured_portfolio_analysis() -> dict[str, Any]:
    """Load the real portfolio response captured from the user's PromptForge app."""
    analysis = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    if not isinstance(analysis, dict):
        raise ValueError("Captured PromptForge analysis must be a JSON object")
    parse_structured_output(
        json.dumps(analysis),
        StructuredOutputSpec("prompt_linter_analysis", ANALYSIS_SCHEMA),
        provider="replay",
    )
    return analysis


# Study step 4: create one provider request and validate the response.
def analyze_prompt(provider: LLMProvider, model: str, prompt: str) -> dict[str, Any]:
    """Run the single live linter agent and validate its JSON response."""
    if not prompt.strip():
        raise ValueError("Prompt must not be empty")
    output_spec = StructuredOutputSpec("prompt_linter_analysis", ANALYSIS_SCHEMA)
    request = LLMRequest(
        model,
        (
            Message("system", PROMPT_LINTER_SYSTEM),
            Message(
                "user",
                "Developer prompt:\n\n"
                + prompt
                + "\n\nReturn only valid JSON matching this schema:\n"
                + json.dumps(ANALYSIS_SCHEMA, indent=2),
            ),
        ),
        max_output_tokens=2_000,
        temperature=0.1,
        response_format=output_spec if provider.capabilities.structured_output else None,
    )
    response = provider.generate(request)
    if response.parsed_output is not None:
        return response.parsed_output
    return parse_structured_output(response.text, output_spec, provider=provider.name)


def _close(provider: LLMProvider) -> None:
    close = getattr(provider, "close", None)
    if callable(close):
        close()


# Study step 5: live mode is explicit and never falls back to a mock model.
def run(*, prompt: str = DEFAULT_PROMPT, allow_live: bool = False) -> PromptLinterResult:
    """Run only with a configured live provider and explicit network authorization."""
    factory = ProviderFactory()
    if factory.kind == "mock":
        raise ConfigurationError(
            "No live LLM model is configured. Use --replay to view the captured portfolio output."
        )
    if not allow_live:
        raise ConfigurationError("Live model detected: pass --live, or use --replay instead.")
    selected = factory.create(allow_live=True)
    try:
        analysis = analyze_prompt(selected.provider, selected.model, prompt)
        return PromptLinterResult(prompt, analysis, selected.provider.name, selected.model)
    finally:
        _close(selected.provider)


def _print_replay() -> None:
    print("# Captured PromptForge portfolio analysis\n")
    print(f"Original prompt: {DEFAULT_PROMPT}\n")
    print(json.dumps(captured_portfolio_analysis(), indent=2, ensure_ascii=False))


def _print_design() -> None:
    """Show the exact prompt and contract without making a provider request."""
    print("# Prompt Linter agent instruction\n")
    print(PROMPT_LINTER_SYSTEM)
    print("\n# Required JSON Schema\n")
    print(json.dumps(ANALYSIS_SCHEMA, indent=2))


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run the one-agent Prompt Linter case study.")
    parser.add_argument("--live", action="store_true", help="Authorize one provider call.")
    parser.add_argument(
        "--replay", action="store_true", help="Print captured portfolio output; no provider call."
    )
    parser.add_argument(
        "--show-design",
        action="store_true",
        help="Print the agent instruction and output schema; no provider call.",
    )
    parser.add_argument(
        "--prompt", default=DEFAULT_PROMPT, help="Developer prompt to analyze live."
    )
    args = parser.parse_args(argv)

    if args.replay:
        _print_replay()
        return
    if args.show_design:
        _print_design()
        return

    factory = ProviderFactory()
    if factory.kind == "mock":
        print(
            "No live LLM model is configured. Run with --replay to inspect the portfolio example."
        )
        return
    if not args.live:
        print("A live LLM model is configured. Run with --live, or use --replay instead.")
        return

    result = run(prompt=args.prompt, allow_live=True)
    print(f"# Prompt Linter result ({result.provider}/{result.model})\n")
    print(json.dumps(result.analysis, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
