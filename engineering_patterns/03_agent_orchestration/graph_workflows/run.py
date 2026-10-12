"""Executable, offline Applied AI handbook pattern."""

from applied_ai.orchestration import GraphNode, StateGraph


def main() -> None:
    graph = StateGraph(
        {
            "plan": GraphNode(lambda state: ({"plan": "answer the question"}, "respond")),
            "respond": GraphNode(lambda state: ({"answer": "42"}, None)),
        },
        start="plan",
    )
    checkpoint = graph.execute({"question": "What is 6 × 7?"}, max_steps=1)
    print(f"Checkpoint: {checkpoint.next_node}, history={checkpoint.history}")
    final = graph.execute(checkpoint, max_steps=2)
    print(f"Completed: {final.completed}, answer={final.data['answer']}")


if __name__ == "__main__":
    main()
