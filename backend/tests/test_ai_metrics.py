import math

import pytest

from app.core.common.ai_metrics import AIMetricsRegistry


def test_ai_metrics_aggregate_count_and_latency_by_safe_labels() -> None:
    registry = AIMetricsRegistry()

    registry.record(
        provider="openai",
        function="matter_summary",
        outcome="success",
        duration_ms=10.5,
    )
    registry.record(
        provider="openai",
        function="matter_summary",
        outcome="success",
        duration_ms=20.5,
    )
    registry.record(
        provider="gemini",
        function="matter_summary",
        outcome="failure",
        error_code="provider_timeout",
        duration_ms=30,
    )

    success, failure = registry.snapshot()
    assert success.call_count == 1
    assert success.key.error_code == "provider_timeout"
    assert failure.call_count == 2
    assert failure.total_duration_ms == 31
    assert failure.max_duration_ms == 20.5
    assert failure.average_duration_ms == 15.5


@pytest.mark.parametrize(
    "changes",
    [
        {"provider": "Open AI"},
        {"function": "Matter Summary"},
        {"outcome": "unknown"},
        {"outcome": "success", "error_code": "provider_timeout"},
        {"outcome": "failure", "error_code": None},
        {"outcome": "failure", "error_code": "unsafe error"},
        {"duration_ms": -1},
        {"duration_ms": math.inf},
    ],
)
def test_ai_metrics_reject_unsafe_or_inconsistent_observations(changes) -> None:
    values = {
        "provider": "openai",
        "function": "matter_summary",
        "outcome": "success",
        "duration_ms": 1,
        "error_code": None,
    }
    values.update(changes)

    registry = AIMetricsRegistry()
    with pytest.raises(ValueError):
        registry.record(**values)

    assert registry.snapshot() == ()
