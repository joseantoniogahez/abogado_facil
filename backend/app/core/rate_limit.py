from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from time import monotonic
from typing import Protocol

from fastapi import Request

from app.core.config.settings import ApiSettings
from app.core.errors.domain import DomainError, DomainErrorType


class CounterStore(Protocol):
    async def increment(self, key: str, window_seconds: int) -> tuple[int, int]: ...


class MemoryCounterStore:
    def __init__(self) -> None:
        self._counters: dict[str, tuple[int, float]] = {}

    async def increment(self, key: str, window_seconds: int) -> tuple[int, int]:
        now = monotonic()
        count, expires_at = self._counters.get(key, (0, now + window_seconds))
        if expires_at <= now:
            count, expires_at = 0, now + window_seconds
        count += 1
        self._counters[key] = (count, expires_at)
        return count, max(1, int(expires_at - now))


class RedisCounterStore:
    _SCRIPT = """
    local count = redis.call('INCR', KEYS[1])
    if count == 1 then redis.call('EXPIRE', KEYS[1], ARGV[1]) end
    return {count, redis.call('TTL', KEYS[1])}
    """

    def __init__(self, redis_url: str) -> None:
        from redis.asyncio import Redis

        self._client = Redis.from_url(redis_url, decode_responses=False)
        self._script = self._client.register_script(self._SCRIPT)

    async def increment(self, key: str, window_seconds: int) -> tuple[int, int]:
        count, ttl = await self._script(keys=[key], args=[window_seconds])
        return int(count), max(1, int(ttl))


@dataclass(frozen=True)
class RateLimitRule:
    name: str
    limit: int


class RateLimiter:
    def __init__(self, settings: ApiSettings, store: CounterStore | None = None) -> None:
        self.enabled = settings.RATE_LIMIT_ENABLED
        self.window_seconds = settings.RATE_LIMIT_WINDOW_SECONDS
        self._limits = {
            "login": settings.RATE_LIMIT_LOGIN,
            "register": settings.RATE_LIMIT_REGISTER,
            "upload": settings.RATE_LIMIT_UPLOAD,
        }
        self._store = store or (
            RedisCounterStore(settings.REDIS_URL) if settings.RATE_LIMIT_STORAGE == "redis" else MemoryCounterStore()
        )

    async def check(self, request: Request, rule: RateLimitRule) -> None:
        if not self.enabled:
            return
        client_host = request.client.host if request.client else "unknown"
        key = f"abogado-facil:rate-limit:{rule.name}:{client_host}"
        limit = self._limits.get(rule.name, rule.limit)
        count, retry_after = await self._store.increment(key, self.window_seconds)
        remaining = max(0, limit - count)
        request.state.rate_limit_headers = {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(retry_after),
        }
        if count > limit:
            raise DomainError(
                DomainErrorType.RATE_LIMITED,
                "Too many requests. Try again later.",
                details={"retry_after_seconds": retry_after},
                headers={**request.state.rate_limit_headers, "Retry-After": str(retry_after)},
            )


def rate_limit_dependency(rule: RateLimitRule) -> Callable[[Request], Awaitable[None]]:
    async def dependency(request: Request) -> None:
        limiter: RateLimiter = request.app.state.rate_limiter
        await limiter.check(request, rule)

    return dependency


LOGIN_RATE_LIMIT = RateLimitRule("login", 10)
REGISTER_RATE_LIMIT = RateLimitRule("register", 5)
UPLOAD_RATE_LIMIT = RateLimitRule("upload", 30)
