"""Offline tracing and logging demonstration."""

from applied_ai.evaluation import TraceLog


def main() -> None:
    trace = TraceLog()
    trace.add("retrieve", source="rag")
    trace.add("genetative", source="llm")
    print(trace.snapshot())


if __name__ == "__main__":
    main()
