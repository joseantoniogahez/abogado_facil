import asyncio
import logging
from collections.abc import AsyncIterator
from unittest.mock import MagicMock

import pytest
from fastapi.sse import ServerSentEvent

from app.core.common.streaming import new_execution_id, stream_ai_events


async def _source(*chunks: dict[str, str]) -> AsyncIterator[dict[str, str]]:
    for chunk in chunks:
        yield chunk


def _event_names(events: list[ServerSentEvent]) -> list[str | None]:
    return [event.event for event in events]


def test_new_execution_id_is_opaque_hex() -> None:
    execution_id = new_execution_id()

    assert len(execution_id) == 32
    assert int(execution_id, 16) >= 0


def test_stream_emits_correlated_lifecycle_and_does_not_log_chunk_content() -> None:
    asyncio.run(_test_stream_emits_correlated_lifecycle_and_does_not_log_chunk_content())


async def _test_stream_emits_correlated_lifecycle_and_does_not_log_chunk_content() -> None:
    logger = MagicMock(spec=logging.Logger)

    events = [
        event
        async for event in stream_ai_events(
            _source({"text": "private legal text"}),
            request_id="req-1",
            execution_id="exec-1",
            logger=logger,
        )
    ]

    assert _event_names(events) == ["started", "delta", "completed"]
    assert events[1].data == {"sequence": 1, "data": {"text": "private legal text"}}
    assert all(event.id is not None and event.id.startswith("exec-1:") for event in events)
    log_text = " ".join(str(call) for call in logger.log.call_args_list)
    assert "private legal text" not in log_text
    assert "req-1" in log_text
    assert "exec-1" in log_text


def test_stream_emits_heartbeat_when_provider_is_slow() -> None:
    asyncio.run(_test_stream_emits_heartbeat_when_provider_is_slow())


async def _test_stream_emits_heartbeat_when_provider_is_slow() -> None:
    async def slow_source() -> AsyncIterator[dict[str, str]]:
        await asyncio.sleep(0.02)
        yield {"text": "chunk"}

    events = [
        event
        async for event in stream_ai_events(
            slow_source(),
            request_id="req-2",
            execution_id="exec-2",
            heartbeat_interval_seconds=0.005,
        )
    ]

    assert _event_names(events)[0] == "started"
    assert "heartbeat" in _event_names(events)
    assert _event_names(events)[-1] == "completed"


def test_stream_converts_provider_failure_to_safe_error_event() -> None:
    asyncio.run(_test_stream_converts_provider_failure_to_safe_error_event())


async def _test_stream_converts_provider_failure_to_safe_error_event() -> None:
    async def failing_source() -> AsyncIterator[dict[str, str]]:
        raise RuntimeError("provider secret details")
        yield {}

    logger = MagicMock(spec=logging.Logger)
    events = [
        event
        async for event in stream_ai_events(failing_source(), request_id="req-3", execution_id="exec-3", logger=logger)
    ]

    assert _event_names(events) == ["started", "error"]
    assert events[-1].data == {"code": "provider_error", "execution_id": "exec-3"}
    assert "provider secret details" not in " ".join(str(call) for call in logger.log.call_args_list)


def test_stream_cancellation_is_logged_and_propagated() -> None:
    asyncio.run(_test_stream_cancellation_is_logged_and_propagated())


async def _test_stream_cancellation_is_logged_and_propagated() -> None:
    release = asyncio.Event()

    async def blocked_source() -> AsyncIterator[dict[str, str]]:
        await release.wait()
        yield {"text": "never"}

    logger = MagicMock(spec=logging.Logger)
    consumer = stream_ai_events(
        blocked_source(), request_id="req-4", execution_id="exec-4", logger=logger, heartbeat_interval_seconds=1
    )
    assert (await consumer.__anext__()).event == "started"
    task: asyncio.Future[ServerSentEvent] = asyncio.ensure_future(consumer.__anext__())
    await asyncio.sleep(0)
    task.cancel()

    with pytest.raises(asyncio.CancelledError):
        await task
    await consumer.aclose()

    log_text = " ".join(str(call) for call in logger.log.call_args_list)
    assert "ai_stream_cancelled" in log_text


def test_stream_rejects_non_positive_heartbeat_interval() -> None:
    asyncio.run(_test_stream_rejects_non_positive_heartbeat_interval())


async def _test_stream_rejects_non_positive_heartbeat_interval() -> None:
    with pytest.raises(ValueError, match="greater than zero"):
        await stream_ai_events(_source(), request_id="req-5", heartbeat_interval_seconds=0).__anext__()


def test_stream_closes_pending_provider_read_after_heartbeat() -> None:
    async def run() -> None:
        release = asyncio.Event()

        async def blocked_source() -> AsyncIterator[dict[str, str]]:
            await release.wait()
            yield {"text": "never"}

        consumer = stream_ai_events(
            blocked_source(), request_id="req-6", execution_id="exec-6", heartbeat_interval_seconds=0.001
        )
        assert (await consumer.__anext__()).event == "started"
        assert (await consumer.__anext__()).event == "heartbeat"
        await consumer.aclose()

    asyncio.run(run())
