"""Reusable, redaction-safe Server-Sent Events helpers for future AI providers."""

import asyncio
import logging
from collections.abc import AsyncGenerator, AsyncIterable, AsyncIterator, Mapping
from contextlib import suppress
from dataclasses import dataclass
from time import perf_counter
from typing import Any
from uuid import uuid4

from fastapi.sse import ServerSentEvent

from app.core.common.observability import log_layer_event

AIStreamChunk = Mapping[str, Any]


@dataclass(frozen=True)
class AIStreamContract:
    """Stable names and transport settings shared by future AI stream consumers."""

    started: str = "started"
    delta: str = "delta"
    heartbeat: str = "heartbeat"
    completed: str = "completed"
    error: str = "error"
    heartbeat_interval_seconds: float = 15.0


AI_STREAM_CONTRACT = AIStreamContract()


def new_execution_id() -> str:
    """Create an opaque execution identifier that is safe to expose to a client."""

    return uuid4().hex


def _event(name: str, data: Mapping[str, Any], *, execution_id: str, sequence: int) -> ServerSentEvent:
    return ServerSentEvent(
        event=name,
        id=f"{execution_id}:{sequence}",
        data=dict(data),
    )


def _log_stream_event(
    logger: logging.Logger,
    *,
    event: str,
    request_id: str,
    execution_id: str,
    duration_ms: float | None = None,
    chunks: int | None = None,
    error_type: str | None = None,
    level: int = logging.INFO,
) -> None:
    fields: dict[str, Any] = {
        "request_id": request_id,
        "execution_id": execution_id,
    }
    if duration_ms is not None:
        fields["duration_ms"] = round(duration_ms, 2)
    if chunks is not None:
        fields["chunks"] = chunks
    if error_type is not None:
        fields["error_type"] = error_type
    log_layer_event(logger, layer="ai_stream", event=event, level=level, **fields)


async def _poll_next_chunk(
    iterator: AsyncIterator[AIStreamChunk],
    pending: asyncio.Future[AIStreamChunk] | None,
    *,
    timeout: float,
) -> tuple[AIStreamChunk | None, asyncio.Future[AIStreamChunk] | None, bool]:
    """Poll the provider iterator, retaining a pending read across heartbeats."""

    if pending is None:
        pending = asyncio.ensure_future(iterator.__anext__())
    try:
        return await asyncio.wait_for(asyncio.shield(pending), timeout=timeout), None, False
    except TimeoutError:
        return None, pending, True
    except StopAsyncIteration:
        return None, None, False
    finally:
        if pending.done():
            pending = None


async def stream_ai_events(
    source: AsyncIterable[AIStreamChunk],
    *,
    request_id: str,
    execution_id: str | None = None,
    logger: logging.Logger | None = None,
    heartbeat_interval_seconds: float = AI_STREAM_CONTRACT.heartbeat_interval_seconds,
) -> AsyncGenerator[ServerSentEvent]:
    """Wrap provider chunks in a cancelable, correlated SSE lifecycle.

    The source owns provider-specific data. This wrapper never logs chunk contents,
    prompts, document text, credentials, or provider error messages.
    """

    if heartbeat_interval_seconds <= 0:
        raise ValueError("heartbeat_interval_seconds must be greater than zero")

    stream_logger = logger or logging.getLogger("app.ai_stream")
    resolved_execution_id = execution_id or new_execution_id()
    started_at = perf_counter()
    sequence = 0
    chunks = 0
    iterator = source.__aiter__()
    next_chunk: asyncio.Future[AIStreamChunk] | None = None

    _log_stream_event(
        stream_logger,
        event="ai_stream_started",
        request_id=request_id,
        execution_id=resolved_execution_id,
    )
    yield _event(
        AI_STREAM_CONTRACT.started,
        {"execution_id": resolved_execution_id},
        execution_id=resolved_execution_id,
        sequence=sequence,
    )

    try:
        while True:
            chunk, next_chunk, timed_out = await _poll_next_chunk(
                iterator,
                next_chunk,
                timeout=heartbeat_interval_seconds,
            )
            if timed_out:
                sequence += 1
                yield _event(
                    AI_STREAM_CONTRACT.heartbeat,
                    {"execution_id": resolved_execution_id},
                    execution_id=resolved_execution_id,
                    sequence=sequence,
                )
                continue
            if chunk is None:
                break

            chunks += 1
            sequence += 1
            yield _event(
                AI_STREAM_CONTRACT.delta,
                {"sequence": chunks, "data": dict(chunk)},
                execution_id=resolved_execution_id,
                sequence=sequence,
            )
    except asyncio.CancelledError:
        _log_stream_event(
            stream_logger,
            event="ai_stream_cancelled",
            request_id=request_id,
            execution_id=resolved_execution_id,
            duration_ms=(perf_counter() - started_at) * 1000,
            chunks=chunks,
            level=logging.WARNING,
        )
        raise
    except Exception as exc:
        _log_stream_event(
            stream_logger,
            event="ai_stream_failed",
            request_id=request_id,
            execution_id=resolved_execution_id,
            duration_ms=(perf_counter() - started_at) * 1000,
            chunks=chunks,
            error_type=type(exc).__name__,
            level=logging.ERROR,
        )
        sequence += 1
        yield _event(
            AI_STREAM_CONTRACT.error,
            {"code": "provider_error", "execution_id": resolved_execution_id},
            execution_id=resolved_execution_id,
            sequence=sequence,
        )
        return
    finally:
        if next_chunk is not None and not next_chunk.done():
            next_chunk.cancel()
            with suppress(asyncio.CancelledError):
                await next_chunk
        if hasattr(iterator, "aclose"):
            with suppress(Exception):
                await iterator.aclose()  # type: ignore[attr-defined]

    _log_stream_event(
        stream_logger,
        event="ai_stream_completed",
        request_id=request_id,
        execution_id=resolved_execution_id,
        duration_ms=(perf_counter() - started_at) * 1000,
        chunks=chunks,
    )
    sequence += 1
    yield _event(
        AI_STREAM_CONTRACT.completed,
        {"execution_id": resolved_execution_id, "chunks": chunks},
        execution_id=resolved_execution_id,
        sequence=sequence,
    )
