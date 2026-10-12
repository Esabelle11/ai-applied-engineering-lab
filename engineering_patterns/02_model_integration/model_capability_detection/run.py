"""Executable, offline Applied AI handbook pattern."""

from applied_ai import LLMRequest, Message, MockProvider, StructuredOutputSpec
from applied_ai.core.exceptions import CapabilityNotSupportedError


def main() -> None:
    spec = StructuredOutputSpec(
        "answer",
        {
            "type": "object",
            "properties": {"value": {"type": "integer"}},
            "required": ["value"],
            "additionalProperties": False,
        },
    )
    request = LLMRequest("mock", (Message("user", "Return JSON"),), response_format=spec)
    limited = MockProvider(supports_structured_output=False)
    try:
        limited.generate(request)
    except CapabilityNotSupportedError:
        print("Structured output rejected: unsupported capability")


if __name__ == "__main__":
    main()
