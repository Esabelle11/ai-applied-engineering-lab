"""Validate multimodal parts and serialize them to an explicit provider payload."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True, slots=True)
class TextPart:
    text: str

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise ValueError("Text part must be non-empty")


@dataclass(frozen=True, slots=True)
class ImagePart:
    url: str
    detail: str = "auto"

    def __post_init__(self) -> None:
        parsed = urlparse(self.url)
        if parsed.scheme not in {"https", "data"}:
            raise ValueError("Image URL must use HTTPS or an inline data URL")
        if self.detail not in {"low", "high", "auto"}:
            raise ValueError("Image detail must be low, high, or auto")


def to_openai_content(parts: tuple[TextPart | ImagePart, ...]) -> list[dict[str, object]]:
    """Convert validated parts to the OpenAI-compatible content shape without making a request."""
    if not parts:
        raise ValueError("At least one multimodal part is required")
    content: list[dict[str, object]] = []
    for part in parts:
        if isinstance(part, TextPart):
            content.append({"type": "input_text", "text": part.text})
        else:
            content.append({"type": "input_image", "image_url": part.url, "detail": part.detail})
    return content


def main() -> None:
    content = to_openai_content(
        (TextPart("What is shown in this image?"), ImagePart("https://example.test/cat.png", "low"))
    )
    print(content)


if __name__ == "__main__":
    main()
