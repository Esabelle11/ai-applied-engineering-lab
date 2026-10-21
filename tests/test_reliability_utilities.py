from __future__ import annotations

import pytest

from applied_ai.core.exceptions import RateLimitError
from applied_ai.reliability import (
    RequestQueue,
    classify_error,
    full_jitter,
    recover_json_output,
    validate_text_output,
    with_degradation,
)


def test_classification_jitter_and_queue_boundaries() -> None:
    assert classify_error(RateLimitError("slow down")).retryable
    assert full_jitter(8, 0.25) == 2
    with pytest.raises(ValueError):
        full_jitter(1, 2)
    queue = RequestQueue(max_size=1)
    queue.enqueue("one")
    with pytest.raises(OverflowError):
        queue.enqueue("two")
    assert queue.drain(str.upper) == ["ONE"]


def test_validation_recovery_and_degradation_are_explicit() -> None:
    assert validate_text_output(" yes ", allowed={"yes"}) == "yes"
    with pytest.raises(ValueError):
        validate_text_output("no", allowed={"yes"})
    assert recover_json_output('{"answer": 42}', required_keys={"answer"}) == {"answer": 42}
    with pytest.raises(ValueError):
        recover_json_output("[]", required_keys={"answer"})

    def unavailable() -> str:
        raise ConnectionError("offline")

    assert (
        with_degradation(unavailable, lambda: "fallback", recoverable=(ConnectionError,))
        == "fallback"
    )
