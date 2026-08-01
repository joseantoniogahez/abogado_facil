import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from starlette.requests import Request

from app.core.config.settings import AiCredentialSettings, AILimitSettings, AIQueueSettings, AuthSettings
from app.core.security.service.encryption import AesGcmSecretEncryption
from app.core.setup import dependencies
from app.core.setup.dependencies import (
    get_ai_assistance_repository,
    get_ai_assistance_service,
    get_ai_credentials_repository,
    get_ai_credentials_service,
    get_ai_insights_repository,
    get_ai_insights_service,
    get_ai_jobs_repository,
    get_ai_jobs_service,
    get_ai_limit_settings,
    get_ai_provider_factory,
    get_ai_queue_settings,
    get_audit_log_repository,
    get_audit_log_service,
    get_document_templates_service,
    get_file_storage,
    get_job_scheduler,
    get_outbox_repository,
    get_outbox_service,
    get_request_permission_scope_cache,
    get_secret_encryption,
)
from app.features.ai_assistance.repository import AIAssistanceRepository
from app.features.ai_assistance.service import AIAssistanceService
from app.features.ai_credentials.repository import AiCredentialsRepository
from app.features.ai_credentials.service import AiCredentialsService
from app.features.ai_execution.service import AiProviderFactory
from app.features.ai_insights.repository import AIInsightsRepository
from app.features.ai_insights.service import AIInsightsService
from app.features.ai_jobs.repository import AIJobsRepository
from app.features.ai_jobs.service import AIJobsService
from app.features.audit_log.repository import AuditLogRepository
from app.features.audit_log.service import AuditLogService
from app.features.document_templates.service import DocumentTemplatesService
from app.features.outbox.repository import OutboxRepository
from app.features.outbox.service import OutboxService
from app.integrations.rq_jobs import RQJobScheduler
from utils.testing_support.file_storage import FakeFileStorage


def _request(path: str) -> Request:
    return Request(
        {
            "type": "http",
            "method": "GET",
            "path": path,
            "headers": [],
            "query_string": b"",
            "scheme": "http",
            "http_version": "1.1",
            "client": ("testclient", 50000),
            "server": ("testserver", 80),
        }
    )


def test_get_request_permission_scope_cache_reuses_request_state_cache() -> None:
    request = _request("/permission-cache")

    async def run_test() -> None:
        first_cache = await get_request_permission_scope_cache(request)
        first_cache[(10, "roles:manage")] = "any"

        second_cache = await get_request_permission_scope_cache(request)
        assert second_cache is first_cache
        assert second_cache[(10, "roles:manage")] == "any"

    asyncio.run(run_test())


def test_get_outbox_repository_builds_outbox_repository() -> None:
    session = MagicMock()

    async def run_test() -> None:
        repository = await get_outbox_repository(session)

        assert isinstance(repository, OutboxRepository)
        assert repository.session is session

    asyncio.run(run_test())


def test_get_audit_log_repository_builds_audit_log_repository() -> None:
    session = MagicMock()

    async def run_test() -> None:
        repository = await get_audit_log_repository(session)

        assert isinstance(repository, AuditLogRepository)
        assert repository.session is session

    asyncio.run(run_test())


def test_get_audit_log_service_builds_audit_log_service() -> None:
    audit_log_repository = MagicMock()

    async def run_test() -> None:
        service = await get_audit_log_service(audit_log_repository=audit_log_repository)

        assert isinstance(service, AuditLogService)
        assert service.audit_log_repository is audit_log_repository

    asyncio.run(run_test())


def test_get_outbox_service_builds_outbox_service() -> None:
    outbox_repository = MagicMock()
    unit_of_work = MagicMock()
    unit_of_work.__aenter__ = AsyncMock(return_value=unit_of_work)
    unit_of_work.__aexit__ = AsyncMock(return_value=None)

    async def run_test() -> None:
        service = await get_outbox_service(outbox_repository=outbox_repository, unit_of_work=unit_of_work)

        assert isinstance(service, OutboxService)
        assert service.outbox_repository is outbox_repository
        assert service.unit_of_work is unit_of_work

    asyncio.run(run_test())


def test_get_file_storage_builds_configured_adapter(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_storage = FakeFileStorage()
    monkeypatch.setattr(dependencies, "S3FileStorage", lambda: fake_storage)

    async def run_test() -> None:
        assert await get_file_storage() is fake_storage

    asyncio.run(run_test())


def test_ai_credential_dependencies_build_expected_components() -> None:
    session = MagicMock()
    repository = asyncio.run(get_ai_credentials_repository(session))
    assert isinstance(repository, AiCredentialsRepository)
    assert repository.session is session

    encryption = asyncio.run(get_secret_encryption(AiCredentialSettings()))
    assert isinstance(encryption, AesGcmSecretEncryption)

    unit_of_work = MagicMock()
    service = asyncio.run(get_ai_credentials_service(repository, unit_of_work, encryption))
    assert isinstance(service, AiCredentialsService)
    assert service.repository is repository
    assert service.unit_of_work is unit_of_work


def test_get_ai_credential_settings_returns_settings() -> None:
    from app.core.setup.dependencies import get_ai_credential_settings

    settings = asyncio.run(get_ai_credential_settings())
    assert isinstance(settings, AiCredentialSettings)


def test_ai_job_dependencies_build_expected_components() -> None:
    session = MagicMock()
    repository = asyncio.run(get_ai_jobs_repository(session))
    assert isinstance(repository, AIJobsRepository)
    assert repository.session is session

    unit_of_work = MagicMock()
    service = asyncio.run(get_ai_jobs_service(repository, unit_of_work))
    assert isinstance(service, AIJobsService)
    assert service.repository is repository
    assert service.unit_of_work is unit_of_work


def test_ai_assistance_dependencies_build_expected_components() -> None:
    session = MagicMock()
    repository = asyncio.run(get_ai_assistance_repository(session))
    assert isinstance(repository, AIAssistanceRepository)
    credentials = MagicMock()
    factory = asyncio.run(get_ai_provider_factory(credentials))
    assert isinstance(factory, AiProviderFactory)
    matters = MagicMock()
    jobs = MagicMock()
    unit_of_work = MagicMock()
    notes = MagicMock()
    tasks = MagicMock()
    checklists = MagicMock()
    service = asyncio.run(
        get_ai_assistance_service(
            repository,
            matters,
            factory,
            jobs,
            unit_of_work,
            AuthSettings(),
            notes,
            tasks,
            checklists,
            AILimitSettings(),
        )
    )
    assert isinstance(service, AIAssistanceService)
    assert service.repository is repository
    assert service.notes_repository is notes


def test_ai_insights_dependencies_build_expected_components() -> None:
    session = MagicMock()
    repository = asyncio.run(get_ai_insights_repository(session))
    assert isinstance(repository, AIInsightsRepository)
    unit_of_work = MagicMock()
    service = asyncio.run(get_ai_insights_service(repository, unit_of_work))
    assert isinstance(service, AIInsightsService)
    assert service.repository is repository


def test_ai_queue_dependencies_build_expected_components() -> None:
    settings = asyncio.run(get_ai_queue_settings())
    assert isinstance(settings, AIQueueSettings)
    scheduler = asyncio.run(get_job_scheduler(settings))
    assert isinstance(scheduler, RQJobScheduler)
    assert scheduler.handlers == {}


def test_document_templates_dependency_builds_service() -> None:
    provider_factory = MagicMock()
    jobs_service = MagicMock()
    settings = AuthSettings(JWT_SECRET_KEY="secret", JWT_ISSUER="issuer", JWT_AUDIENCE="audience")
    limits = asyncio.run(get_ai_limit_settings())
    service = asyncio.run(get_document_templates_service(provider_factory, jobs_service, settings, limits))
    assert isinstance(service, DocumentTemplatesService)
    assert service.provider_factory is provider_factory
    assert service.jobs_service is jobs_service
