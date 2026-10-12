"""A fully offline, deterministic prompt composition example."""

from string import Template


def build_prompt(topic: str, audience: str, sentences: int) -> str:
    """Compose a reusable prompt without making a network or model request."""
    if not topic.strip() or not audience.strip() or sentences < 1:
        raise ValueError("Provide topic, audience, and a positive sentence count")
    template = Template("Explain $topic to $audience in $sentences sentences.")
    return template.substitute(topic=topic, audience=audience, sentences=str(sentences))


def main() -> None:
    print(build_prompt("retrieval-augmented generation", "a beginner", 2))


if __name__ == "__main__":
    main()
