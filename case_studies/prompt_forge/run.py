"""A compact Prompt Forge: compare two templates on a tiny synthetic test set."""

from __future__ import annotations

import sys

from applied_ai.core import LLMRequest, Message
from applied_ai.evaluation import EvalCase, evaluate
from applied_ai.prompting import PromptTemplate
from applied_ai.providers.factory import ProviderFactory

BASIC = PromptTemplate("Return only the capital city of {country}.")
CONSTRAINED = PromptTemplate("Respond with only one city name. Country: {country}. No explanation.")
CASES = (EvalCase("France", "Paris"), EvalCase("Japan", "Tokyo"))


def run(*, allow_live: bool = False) -> dict[str, float]:
    config = ProviderFactory()
    # Separate deterministic fixtures intentionally exercise the exact prompts.
    from applied_ai.providers.mock import MockProvider

    selected = config.create(allow_live=allow_live)
    provider = selected.provider
    if config.kind == "mock":
        answers = {
            BASIC.render({"country": "France"}): "Paris",
            BASIC.render({"country": "Japan"}): "Tokyo",
            CONSTRAINED.render({"country": "France"}): "Paris",
            CONSTRAINED.render({"country": "Japan"}): "Tokyo",
        }
        provider = MockProvider(responses=answers)

    def score(template: PromptTemplate) -> float:
        def predict(country: str) -> str:
            prompt = template.render({"country": country})
            return provider.generate(LLMRequest(selected.model, (Message("user", prompt),))).text

        return evaluate(CASES, predict).accuracy

    try:
        scores = {"basic": score(BASIC), "constrained": score(CONSTRAINED)}
    finally:
        close = getattr(provider, "close", None)
        if callable(close):
            close()
    return scores


if __name__ == "__main__":
    print("Prompt Forge evaluation:", run(allow_live="--live" in sys.argv))
