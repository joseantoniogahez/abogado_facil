import asyncio
from datetime import UTC, datetime, timedelta
from functools import wraps
from types import SimpleNamespace
from typing import cast
from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors.services import NotFoundError
from app.features.ai_insights.repository import AIInsightsRepository
from app.features.ai_insights.router import _firm_id, get_insights, save_feedback
from app.features.ai_insights.schemas import AIResultFeedbackRequest
from app.features.ai_insights.service import AIInsightsService
from app.features.auth.principal import CurrentPrincipal


def run_async(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        return asyncio.run(function(*args, **kwargs))

    return wrapper


class Uow:
    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        return None


class ScalarRows:
    def __init__(self, rows):
        self.rows = rows

    def all(self):
        return self.rows


@run_async
async def test_repository_aggregates_operational_and_product_metrics() -> None:
    now = datetime.now(UTC)
    jobs = [
        SimpleNamespace(
            status="succeeded",
            started_at=now - timedelta(seconds=2),
            completed_at=now,
            updated_at=now,
            attempt_count=2,
            error_code=None,
        ),
        SimpleNamespace(
            status="failed",
            started_at=now - timedelta(seconds=1),
            completed_at=now,
            updated_at=now,
            attempt_count=1,
            error_code="provider_timeout",
        ),
        SimpleNamespace(
            status="running",
            started_at=now - timedelta(minutes=20),
            completed_at=None,
            updated_at=now - timedelta(minutes=20),
            attempt_count=1,
            error_code=None,
        ),
    ]
    results = [
        SimpleNamespace(
            review_status="accepted",
            reviewed_content={"x": 2},
            generated_content={"x": 1},
            converted_actions=[{"type": "note"}],
            source_snapshot={"regenerates_result_id": 1},
        ),
        SimpleNamespace(
            review_status="pending",
            reviewed_content=None,
            generated_content={"x": 1},
            converted_actions=[],
            source_snapshot={},
        ),
    ]
    feedback = [SimpleNamespace(category="useful"), SimpleNamespace(category="needs_correction")]
    session = SimpleNamespace(
        scalars=AsyncMock(side_effect=[ScalarRows(jobs), ScalarRows(results), ScalarRows(feedback)])
    )
    metrics = await AIInsightsRepository(cast(AsyncSession, session)).insights(firm_id=7)
    assert metrics.operational.total_jobs == 3
    assert metrics.operational.success_rate == 33.33
    assert metrics.operational.retry_count == 1
    assert metrics.operational.stuck_jobs == 1
    assert metrics.operational.cost_usd is None
    assert metrics.product.edited_results == 1
    assert metrics.product.converted_results == 1
    assert metrics.product.regenerated_results == 1
    assert metrics.product.abandoned_results == 1


@run_async
async def test_repository_empty_metrics_and_feedback_upsert_paths() -> None:
    empty_session = SimpleNamespace(scalars=AsyncMock(side_effect=[ScalarRows([]), ScalarRows([]), ScalarRows([])]))
    empty = await AIInsightsRepository(cast(AsyncSession, empty_session)).insights(firm_id=9)
    assert empty.operational.success_rate == 0
    assert empty.operational.average_latency_ms == 0

    existing = SimpleNamespace(category="useful")
    session = SimpleNamespace(
        scalar=AsyncMock(side_effect=[SimpleNamespace(id=1), existing]), flush=AsyncMock(), refresh=AsyncMock()
    )
    repository = AIInsightsRepository(cast(AsyncSession, session))
    assert await repository.upsert_feedback(result_id=1, user_id=2, firm_id=3, category="fabricated") is existing
    assert existing.category == "fabricated"

    add_session = SimpleNamespace(
        scalar=AsyncMock(side_effect=[SimpleNamespace(id=1), None]), add=Mock(), flush=AsyncMock(), refresh=AsyncMock()
    )
    created = await AIInsightsRepository(cast(AsyncSession, add_session)).upsert_feedback(
        result_id=1, user_id=2, firm_id=3, category="useful"
    )
    assert created.category == "useful"
    missing_session = SimpleNamespace(scalar=AsyncMock(return_value=None))
    assert (
        await AIInsightsRepository(cast(AsyncSession, missing_session)).upsert_feedback(
            result_id=1, user_id=2, firm_id=3, category="useful"
        )
        is None
    )


@run_async
async def test_service_and_router_delegate_scoped_identity() -> None:
    repository = SimpleNamespace(
        insights=AsyncMock(return_value="metrics"),
        upsert_feedback=AsyncMock(return_value=SimpleNamespace(category="useful")),
    )
    service = AIInsightsService(repository, Uow())
    assert await service.get_insights(firm_id=3) == "metrics"
    assert (await service.save_feedback(result_id=1, user_id=2, firm_id=3, category="useful")).category == "useful"
    repository.upsert_feedback.return_value = None
    with pytest.raises(NotFoundError):
        await service.save_feedback(result_id=1, user_id=2, firm_id=3, category="useful")

    user = cast(CurrentPrincipal, SimpleNamespace(id=2, firm_id=3))
    router_service = SimpleNamespace(
        get_insights=AsyncMock(return_value="metrics"), save_feedback=AsyncMock(return_value="saved")
    )
    assert await get_insights(user, router_service) == "metrics"
    assert await save_feedback(1, AIResultFeedbackRequest(category="useful"), user, router_service) == "saved"
    assert _firm_id(user) == 3
    with pytest.raises(ValueError):
        _firm_id(cast(CurrentPrincipal, SimpleNamespace(firm_id=None)))
