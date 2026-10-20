"""Store explicit facts and retrieve them by lexical relevance."""

from applied_ai.knowledge import LongTermMemory


def main() -> None:
    memory = LongTermMemory()
    memory.remember("preference", "User prefers concise technical explanations.")
    memory.remember("ideal", "User ideal on something.")
    print([fact.id for fact in memory.recall("technical explanations")])


if __name__ == "__main__":
    main()
