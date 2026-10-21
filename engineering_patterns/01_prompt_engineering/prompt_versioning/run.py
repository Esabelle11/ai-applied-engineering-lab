"""Immutable prompt versions with explicit activation and rendering."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from applied_ai.prompting import PromptTemplate


@dataclass(frozen=True, slots=True)
class PromptVersion:
    name: str
    version: str
    template: str

    def __post_init__(self) -> None:
        if not all(
            isinstance(value, str) and value.strip()
            for value in (self.name, self.version, self.template)
        ):
            raise ValueError("Prompt version fields must be non-empty text")
        PromptTemplate(self.template)


class PromptRegistry:
    def __init__(self) -> None:
        self._versions: dict[tuple[str, str], PromptVersion] = {}
        self._active: dict[str, str] = {}

    def publish(self, version: PromptVersion) -> None:
        key = (version.name, version.version)
        if key in self._versions:
            raise ValueError(f"Version already exists: {version.name}@{version.version}")
        self._versions[key] = version

    def activate(self, name: str, version: str) -> None:
        if (name, version) not in self._versions:
            raise KeyError(f"Unknown version: {name}@{version}")
        self._active[name] = version

    def render(self, name: str, values: Mapping[str, str]) -> str:
        if name not in self._active:
            raise KeyError(f"No active version for {name}")
        version = self._versions[(name, self._active[name])]
        return PromptTemplate(version.template).render(values)


def main() -> None:
    registry = PromptRegistry()
    registry.publish(PromptVersion("summarize", "1.0.0", "Summarize {topic} in one sentence."))
    registry.activate("summarize", "1.0.0")
    print(registry.render("summarize", {"topic": "retrieval-augmented generation"}))


if __name__ == "__main__":
    main()
