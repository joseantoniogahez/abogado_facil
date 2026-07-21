import asyncio
from types import SimpleNamespace
from typing import cast

import pytest
from fastapi import FastAPI, Request
from starlette.testclient import TestClient

from app.core.config.settings import ApiSettings
from app.core.errors.domain import DomainError, DomainErrorType
from app.core.rate_limit import MemoryCounterStore, RateLimiter, RateLimitRule, RedisCounterStore
from app.core.setup.factory import configure_request_context_middleware


def _request() -> Request:
    return cast(
        Request,
        SimpleNamespace(
            client=SimpleNamespace(host="198.51.100.10"),
            state=SimpleNamespace(),
        ),
    )


def test_memory_limiter_allows_configured_quota_then_rejects() -> None:
    settings = ApiSettings(RATE_LIMIT_ENABLED=True, RATE_LIMIT_LOGIN=2, RATE_LIMIT_WINDOW_SECONDS=60)
    limiter = RateLimiter(settings, store=MemoryCounterStore())
    rule = RateLimitRule("login", 2)
    request = _request()

    asyncio.run(limiter.check(request, rule))
    asyncio.run(limiter.check(request, rule))

    with pytest.raises(DomainError) as raised:
        asyncio.run(limiter.check(request, rule))

    assert raised.value.error_type is DomainErrorType.RATE_LIMITED
    assert raised.value.headers is not None
    assert raised.value.headers["Retry-After"].isdigit()
    assert request.state.rate_limit_headers["X-RateLimit-Remaining"] == "0"


def test_memory_limiter_recovers_after_window(monkeypatch: pytest.MonkeyPatch) -> None:
    clock = iter((100.0, 100.0, 161.0))
    monkeypatch.setattr("app.core.rate_limit.monotonic", lambda: next(clock))
    limiter = RateLimiter(
        ApiSettings(RATE_LIMIT_ENABLED=True, RATE_LIMIT_LOGIN=1, RATE_LIMIT_WINDOW_SECONDS=60),
        store=MemoryCounterStore(),
    )
    rule = RateLimitRule("login", 1)
    request = _request()

    asyncio.run(limiter.check(request, rule))
    with pytest.raises(DomainError):
        asyncio.run(limiter.check(request, rule))
    asyncio.run(limiter.check(request, rule))


def test_production_rate_limiting_requires_redis() -> None:
    with pytest.raises(ValueError, match="shared Redis"):
        ApiSettings(APP_ENV="production", RATE_LIMIT_ENABLED=True, RATE_LIMIT_STORAGE="memory")


def test_rate_limit_settings_reject_invalid_storage_and_url() -> None:
    with pytest.raises(ValueError, match="memory or redis"):
        ApiSettings(RATE_LIMIT_STORAGE="database")
    with pytest.raises(ValueError, match="redis://"):
        ApiSettings(REDIS_URL="http://localhost")


def test_rate_limit_headers_are_copied_to_success_response() -> None:
    app = FastAPI()
    configure_request_context_middleware(app)

    @app.get("/headers")
    async def headers(request: Request) -> dict[str, bool]:
        request.state.rate_limit_headers = {"X-RateLimit-Remaining": "1"}
        return {"ok": True}

    response = TestClient(app).get("/headers")
    assert response.headers["X-RateLimit-Remaining"] == "1"


def test_redis_counter_store_executes_atomic_script(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeRedis:
        def register_script(self, script: str):
            assert "INCR" in script

            async def execute(*, keys: list[str], args: list[int]) -> list[int]:
                assert (keys, args) == (["key"], [60])
                return [2, 59]

            return execute

    monkeypatch.setattr("redis.asyncio.Redis.from_url", lambda *args, **kwargs: FakeRedis())
    store = RedisCounterStore("redis://localhost")
    assert asyncio.run(store.increment("key", 60)) == (2, 59)
