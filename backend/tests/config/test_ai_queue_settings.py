from typing import Any

import pytest
from pydantic import ValidationError

from app.core.config.settings import AIQueueSettings


def test_ai_queue_settings_parse_retry_backoff() -> None:
    settings = AIQueueSettings(
        AI_QUEUE_MAX_RETRIES=3,
        AI_QUEUE_RETRY_BACKOFF_SECONDS="5, 15, 60, 120",
    )
    assert settings.retry_backoff_seconds == [5, 15, 60]


@pytest.mark.parametrize(
    ("values", "message"),
    (
        ({"REDIS_URL": "http://redis"}, "redis://"),
        ({"AI_QUEUE_NAME": "bad queue"}, "AI_QUEUE_NAME"),
        ({"AI_QUEUE_RETRY_BACKOFF_SECONDS": "5,nope"}, "comma-separated"),
        ({"AI_QUEUE_RETRY_BACKOFF_SECONDS": "5,0"}, "positive"),
        (
            {"AI_QUEUE_MAX_RETRIES": 3, "AI_QUEUE_RETRY_BACKOFF_SECONDS": "5,10"},
            "cover every configured retry",
        ),
    ),
)
def test_ai_queue_settings_reject_invalid_values(values: dict[str, Any], message: str) -> None:
    with pytest.raises(ValidationError, match=message):
        AIQueueSettings(**values)
