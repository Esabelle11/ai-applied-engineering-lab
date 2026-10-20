"""Bounded conversation memory with explicit token-independent limits."""

from __future__ import annotations

from collections import deque

from applied_ai.core.messages import Message


class ConversationMemory:
    def __init__(self, *, max_messages: int = 20) -> None:
        if max_messages < 1:
            raise ValueError("max_messages must be positive")
        self._messages: deque[Message] = deque(maxlen=max_messages)

    def add(self, message: Message) -> None:
        self._messages.append(message)

    def extend(self, messages: tuple[Message, ...] | list[Message]) -> None:
        for message in messages:
            self.add(message)

    def messages(self) -> tuple[Message, ...]:
        return tuple(self._messages)

    def clear(self) -> None:
        self._messages.clear()
