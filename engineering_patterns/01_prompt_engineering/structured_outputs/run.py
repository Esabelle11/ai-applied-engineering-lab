"""Executable, offline Applied AI handbook pattern."""

from applied_ai import LLMRequest, Message, MockProvider, StructuredOutputSpec


def main() -> None:
    spec = StructuredOutputSpec(
        "result",
        {
            "type": "object",
            "properties": {"count": {"type": "integer"}},
            "required": ["count"],
            "additionalProperties": False,
        },
    )
    result = MockProvider(default_text='{"count": 3}').generate(
        LLMRequest("mock", (Message("user", "Return a count"),), response_format=spec)
    )
    print(result.parsed_output)


if __name__ == "__main__":
    main()
