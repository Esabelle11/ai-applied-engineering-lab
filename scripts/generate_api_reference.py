"""Reproduce a public API index directly from SDK exports (no paid API requests)."""

from __future__ import annotations

import argparse
import inspect
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import applied_ai  # noqa: E402

SECTIONS = {
    "Shared request/response": {
        "Message",
        "LLMRequest",
        "LLMResponse",
        "TokenUsage",
        "StructuredOutputSpec",
        "ProviderCapabilities",
    },
    "Provider abstraction": {
        "AppliedAIClient",
        "LLMProvider",
        "MockProvider",
        "ProviderFactory",
    },
    "Reliability": {"ReliableProvider", "RetryPolicy", "LLMError"},
    "Configuration": {"RuntimeConfig", "Settings"},
}


def generate() -> str:
    exported = set(applied_ai.__all__) - {"__version__"}
    covered = set().union(*SECTIONS.values())
    if exported != covered:
        raise ValueError(
            f"Undocumented exports={sorted(exported - covered)}; retired={sorted(covered - exported)}"
        )
    lines = [
        "# Public Python SDK API — " + applied_ai.__version__,
        "",
        "Generated from `applied_ai.__all__` using `scripts/generate_api_reference.py`.",
        "Exports listed here are the supported import surface for the current pre-1.0 release.",
        "Other modules are experimental unless explicitly documented.",
        "",
    ]
    for heading, names in SECTIONS.items():
        lines.extend([f"## {heading}", ""])
        for name in sorted(names):
            obj = getattr(applied_ai, name)
            source = inspect.getmodule(obj)
            module = source.__name__ if source else "applied_ai"
            if module.startswith("applied_ai."):
                link = "../src/" + module.replace(".", "/") + ".py"
            else:
                link = "../src/applied_ai/__init__.py"
            description = (
                inspect.getdoc(obj) or "No public class-level docstring; inspect implementation."
            )
            lead = description.splitlines()[0].replace("|", r"\|")
            lines.extend([f"### `{name}`", "", f"Defined in [`{module}`]({link}).", "", lead, ""])
            if inspect.isclass(obj):
                try:
                    signature = inspect.signature(obj)
                except (TypeError, ValueError):
                    signature = None
                if signature is not None:
                    lines.extend(
                        [
                            "```python",
                            f"{name}{re.sub(r'<built-in method random of Random object at 0x[0-9a-fA-F]+>', '<random callable>', str(signature))}",
                            "```",
                            "",
                        ]
                    )
    lines.extend(
        [
            "## Minimal offline example",
            "",
            "```python",
            "from applied_ai import LLMRequest, Message, MockProvider",
            "",
            'response = MockProvider(default_text="Hello!").generate(',
            '    LLMRequest("mock-model", (Message("user", "Hi"),))',
            ")",
            "print(response.text)",
            "```",
            "",
            "Live providers require credentials and explicit opt-in in the examples. Availability, JSON-schema support, and models vary by provider.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    target = ROOT / "docs" / "API_REFERENCE.md"
    content = generate()
    if args.check:
        if not target.exists() or target.read_text(encoding="utf-8") != content:
            raise SystemExit("API reference is stale: run python scripts/generate_api_reference.py")
        print("API reference is current")
    else:
        target.write_text(content, encoding="utf-8")
        print(f"Wrote {target}")


if __name__ == "__main__":
    main()
