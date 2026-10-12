"""Minimal graph-based multi-role debate, with a checkpoint/resume boundary."""

from __future__ import annotations

import sys

from applied_ai.core import LLMRequest, Message
from applied_ai.orchestration import GraphNode, GraphSnapshot, StateGraph
from applied_ai.providers.factory import ProviderFactory


def run(*, allow_live: bool = False) -> GraphSnapshot:
    selected = ProviderFactory().create(allow_live=allow_live, mock_text="A balanced argument.")
    provider = selected.provider
    print("provider:", provider)
    print("selected:", selected)

    def speaker(role: str, question: str, next_node: str | None) -> GraphNode:
        def step(state: dict[str, str]) -> tuple[dict[str, str], str | None]:
            prompt = (
                f"Debate topic: {state['topic']}\nRole: {role}.\n"
                f"Previous contributions: {state.get('opening', '')} {state.get('optimist', '')} {state.get('skeptic', '')}\n"
                f"Task: {question}\nKeep your answer under 70 words."
            )
            # print("prompt:", prompt)
            answer = provider.generate(LLMRequest(selected.model, (Message("user", prompt),))).text
            # print("answer:", answer)
            print("")
            return {role: answer}, next_node

        return GraphNode(step)

    graph = StateGraph(
        {
            "opening": speaker("opening", "Define the issue neutrally", "optimist"),
            "optimist": speaker("optimist", "Make the strongest constructive case", "skeptic"),
            "skeptic": speaker("skeptic", "Challenge assumptions and identify risks", "synthesis"),
            "synthesis": speaker(
                "synthesis", "Summarize agreement, uncertainty, and next steps", None
            ),
        },
        start="opening",
    )
    # print("graph:", graph)
    try:
        checkpoint = graph.execute(
            {"topic": "Should city services use AI assistants?"}, max_steps=2
        )
        assert not checkpoint.completed and checkpoint.next_node == "skeptic"
        return graph.execute(checkpoint, max_steps=2)
    finally:
        close = getattr(provider, "close", None)
        if callable(close):
            close()


if __name__ == "__main__":
    result = run(allow_live="--live" in sys.argv)
    # print("result:", result)
    print("Visited:", " -> ".join(result.history))
    print("Synthesis:", result.data["synthesis"])
