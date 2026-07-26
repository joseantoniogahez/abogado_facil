from app import rq_config


def test_rq_cli_config_uses_validated_json_worker_settings() -> None:
    assert rq_config.REDIS_URL.startswith(("redis://", "rediss://"))
    assert rq_config.QUEUES == ["ai"]
