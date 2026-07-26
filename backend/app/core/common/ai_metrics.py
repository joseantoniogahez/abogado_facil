"""Bounded, content-free metrics for AI provider calls."""

import math
import re
from dataclasses import dataclass
from threading import Lock

_METRIC_LABEL_PATTERN = re.compile(r"^[a-z][a-z0-9_.-]{0,63}$")
_OUTCOMES = {"success", "failure"}


@dataclass(frozen=True, order=True)
class AIMetricKey:
    provider: str
    function: str
    outcome: str
    error_code: str | None = None


@dataclass(frozen=True)
class AIMetricSnapshot:
    key: AIMetricKey
    call_count: int
    total_duration_ms: float
    max_duration_ms: float

    @property
    def average_duration_ms(self) -> float:
        return self.total_duration_ms / self.call_count


@dataclass
class _AIMetricValue:
    call_count: int = 0
    total_duration_ms: float = 0
    max_duration_ms: float = 0


class AIMetricsRegistry:
    """Process-local registry with validated, low-cardinality labels."""

    def __init__(self) -> None:
        self._values: dict[AIMetricKey, _AIMetricValue] = {}
        self._lock = Lock()

    def record(
        self,
        *,
        provider: str,
        function: str,
        outcome: str,
        duration_ms: float,
        error_code: str | None = None,
    ) -> None:
        for label, value in (("provider", provider), ("function", function)):
            if _METRIC_LABEL_PATTERN.fullmatch(value) is None:
                raise ValueError(f"{label} is not a safe metric label")
        if outcome not in _OUTCOMES:
            raise ValueError("outcome is not supported")
        if (outcome == "success") != (error_code is None):
            raise ValueError("error_code must be present only for failures")
        if error_code is not None and _METRIC_LABEL_PATTERN.fullmatch(error_code) is None:
            raise ValueError("error_code is not a safe metric label")
        if not math.isfinite(duration_ms) or duration_ms < 0:
            raise ValueError("duration_ms must be finite and non-negative")

        key = AIMetricKey(
            provider=provider,
            function=function,
            outcome=outcome,
            error_code=error_code,
        )
        with self._lock:
            value = self._values.setdefault(key, _AIMetricValue())
            value.call_count += 1
            value.total_duration_ms += duration_ms
            value.max_duration_ms = max(value.max_duration_ms, duration_ms)

    def snapshot(self) -> tuple[AIMetricSnapshot, ...]:
        with self._lock:
            return tuple(
                AIMetricSnapshot(
                    key=key,
                    call_count=value.call_count,
                    total_duration_ms=value.total_duration_ms,
                    max_duration_ms=value.max_duration_ms,
                )
                for key, value in sorted(self._values.items())
            )


AI_METRICS = AIMetricsRegistry()
