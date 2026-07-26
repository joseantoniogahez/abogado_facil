"""Validated RQ CLI configuration for the AI worker."""

from app.core.config.settings import AIQueueSettings

_SETTINGS = AIQueueSettings()

REDIS_URL = _SETTINGS.REDIS_URL
QUEUES = [_SETTINGS.AI_QUEUE_NAME]
