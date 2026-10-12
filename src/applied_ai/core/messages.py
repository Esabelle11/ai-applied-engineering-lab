"""Text-only common message model (multimodal belongs to later milestones)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Role = Literal["system", "developer", "user", "assistant"]


@dataclass(frozen=True, slots=True)
class Message:
    role: Role
    content: str

    def __post_init__(self) -> None:
        if self.role not in {"system", "developer", "user", "assistant"}:
            raise ValueError("Unsupported message role")
        if not isinstance(self.content, str) or not self.content.strip():
            raise ValueError("Message content must be non-empty text")
