"""Use bounded conversation memory for recent message context."""

from applied_ai import Message
from applied_ai.memory import ConversationMemory


def main() -> None:
    memory = ConversationMemory(max_messages=2)
    memory.extend(
        [Message("user", "hello"), Message("assistant", "hi"), Message("user", "follow up")]
    )
    print([message.content for message in memory.messages()])


if __name__ == "__main__":
    main()
