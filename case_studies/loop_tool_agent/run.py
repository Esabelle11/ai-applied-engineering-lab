from __future__ import annotations

import argparse
import sys
import time
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from applied_ai.core.exceptions import LLMError  # noqa: E402
from applied_ai.execution import LocalKernelSandbox, SandboxPool  # noqa: E402
from applied_ai.providers.factory import ProviderFactory  # noqa: E402
from applied_ai.reasoning import majority_consensus  # noqa: E402
from case_studies.loop_tool_agent.agent import AgentAttempt, Provider, run_agent_attempt  # noqa: E402
from case_studies.loop_tool_agent.data import MathQuestion, load_questions, select_questions  # noqa: E402

MAX_LIVE_REQUESTS = 4
DEFAULT_MAX_OUTPUT_TOKENS = 800
DEFAULT_MAX_TURNS = 3


@dataclass(frozen=True, slots=True)
class QuestionResult:
    """Evaluation result for one dataset row."""

    index: int
    expected: str
    attempts: tuple[AgentAttempt, ...]
    selected_answer: str | None
    correct: bool
    elapsed_seconds: float
    error: str | None = None


def run_sample(
    provider: Provider,
    model: str,
    questions: Sequence[MathQuestion],
    pool: SandboxPool,
    *,
    attempts: int,
    max_turns: int = DEFAULT_MAX_TURNS,
    max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
) -> tuple[QuestionResult, ...]:
    """Run bounded independent attempts, then choose a deterministic consensus."""
    results: list[QuestionResult] = []
    for question in questions:
        started = time.perf_counter()
        agent_attempts: list[AgentAttempt] = []
        error: str | None = None
        try:
            for _ in range(attempts):
                with pool.lease() as executor:
                    agent_attempts.append(
                        run_agent_attempt(
                            provider,
                            model,
                            question,
                            executor,
                            max_turns=max_turns,
                            max_output_tokens=max_output_tokens,
                        )
                    )
        except LLMError as exc:
            error = f"{exc.category}: {exc}"
        except (RuntimeError, TimeoutError, ValueError) as exc:
            error = str(exc)
        consensus = majority_consensus(tuple(attempt.answer for attempt in agent_attempts))
        results.append(
            QuestionResult(
                question.index,
                question.expected,
                tuple(agent_attempts),
                consensus.answer,
                consensus.answer == question.expected,
                time.perf_counter() - started,
                error,
            )
        )
    return tuple(results)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--live", action="store_true", help="Authorize network calls to the configured provider"
    )
    parser.add_argument(
        "--trusted-local-kernel",
        action="store_true",
        help="Authorize model-generated Python in a local Jupyter kernel",
    )
    parser.add_argument("--questions", type=int, default=1, help="Number of dataset rows to sample")
    parser.add_argument("--attempts", type=int, default=1, help="Independent attempts per question")
    parser.add_argument("--max-turns", type=int, default=DEFAULT_MAX_TURNS)
    parser.add_argument("--seed", type=int, default=7, help="Deterministic dataset sample seed")
    parser.add_argument(
        "--max-output-tokens",
        type=int,
        default=DEFAULT_MAX_OUTPUT_TOKENS,
        help="Per-request completion budget, bounded to protect free-tier quotas",
    )
    args = parser.parse_args()
    if not args.live:
        parser.error("Live calls are disabled; pass --live to authorize API and quota usage")
    if not args.trusted_local_kernel:
        parser.error("Python execution is disabled; pass --trusted-local-kernel to authorize it")
    if args.questions < 1 or args.attempts < 1 or args.max_turns < 2:
        parser.error("--questions and --attempts must be positive; --max-turns must be at least 2")
    if not 128 <= args.max_output_tokens <= 1200:
        parser.error("--max-output-tokens must be between 128 and 1200")
    request_limit = args.questions * args.attempts * args.max_turns
    if request_limit > MAX_LIVE_REQUESTS:
        parser.error(
            f"This runner allows at most {MAX_LIVE_REQUESTS} possible API requests; "
            "reduce questions, attempts, or turns"
        )

    factory = ProviderFactory()
    if factory.kind == "mock":
        parser.error("Configure a real AI_LAB_PROVIDER before using --live")
    sample = select_questions(load_questions(), count=args.questions, seed=args.seed)
    selection = factory.create(allow_live=True)
    try:
        with SandboxPool((LocalKernelSandbox(timeout_seconds=8.0),)) as pool:
            results = run_sample(
                selection.provider,
                selection.model,
                sample,
                pool,
                attempts=args.attempts,
                max_turns=args.max_turns,
                max_output_tokens=args.max_output_tokens,
            )
    finally:
        close = getattr(selection.provider, "close", None)
        if callable(close):
            close()

    for result in results:
        status = "correct" if result.correct else "incorrect"
        if result.error:
            status = f"error ({result.error})"
        tool_calls = sum(attempt.tool_calls for attempt in result.attempts)
        turns = sum(attempt.turns for attempt in result.attempts)
        print(
            f"Question {result.index}: {status}; expected={result.expected}; "
            f"received={result.selected_answer}; turns={turns}; tool_calls={tool_calls}; "
            f"elapsed={result.elapsed_seconds:.2f}s"
        )
    completed = [result for result in results if result.error is None]
    correct = sum(result.correct for result in completed)
    print(
        f"Completed {len(completed)}/{len(results)} questions; at most {request_limit} live request(s); "
        f"accuracy={correct}/{len(completed) if completed else 0}; model={selection.model}"
    )


if __name__ == "__main__":
    main()
