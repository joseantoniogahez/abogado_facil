from typing import Annotated, cast

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config.settings import AiCredentialSettings, AuthSettings, MatterDocumentSettings, ObjectStorageSettings
from app.core.db.database import get_async_session_factory
from app.core.db.ports import UnitOfWorkPort
from app.core.db.uow import UnitOfWork
from app.core.security.service import Argon2PasswordService, JwtTokenService, PasswordServicePort, TokenServicePort
from app.core.security.service.encryption import AesGcmSecretEncryption, SecretEncryptionPort
from app.features.ai_credentials.repository import AiCredentialsRepository
from app.features.ai_credentials.service import AiCredentialsService
from app.features.ai_jobs.repository import AIJobsRepository
from app.features.ai_jobs.service import AIJobsService
from app.features.audit_log.repository import AuditLogRepository
from app.features.audit_log.service import AuditLogService, AuditLogServicePort
from app.features.auth.repository import AuthRepository
from app.features.auth.service import AuthService, AuthServicePort
from app.features.clients.repository import ClientsRepository
from app.features.clients.service import ClientsService, ClientsServicePort
from app.features.dashboard.service import DashboardService, DashboardServicePort
from app.features.matter_calculations.repository import MatterCalculationsRepository
from app.features.matter_calculations.service import MatterCalculationsService
from app.features.matter_checklists.repository import MatterChecklistsRepository
from app.features.matter_checklists.service import MatterChecklistsService, MatterChecklistsServicePort
from app.features.matter_documents.repository import MatterDocumentsRepository
from app.features.matter_documents.service import MatterDocumentsService, MatterDocumentsServicePort
from app.features.matter_notes.repository import MatterNotesRepository
from app.features.matter_notes.service import MatterNotesService, MatterNotesServicePort
from app.features.matter_payments.repository import MatterPaymentsRepository
from app.features.matter_payments.service import MatterPaymentsService, MatterPaymentsServicePort
from app.features.matter_tasks.repository import MatterTasksRepository
from app.features.matter_tasks.service import MatterTasksService, MatterTasksServicePort
from app.features.matters.repository import MattersRepository
from app.features.matters.service import MattersService, MattersServicePort
from app.features.outbox.repository import OutboxRepository
from app.features.outbox.service import OutboxService, OutboxServicePort
from app.features.rbac.repository import RBACRepository
from app.features.rbac.service import RBACService, RBACServicePort
from app.integrations.files import FileStoragePort
from app.integrations.pdf_text import PdfTextExtractorPort, PyPdfTextExtractor
from app.integrations.s3 import S3FileStorage

PermissionScopeCache = dict[tuple[int, str], str | None]
_PERMISSION_SCOPE_CACHE_STATE_KEY = "_permission_scope_cache"


def create_async_session() -> AsyncSession:
    return get_async_session_factory()()


async def get_db_session():
    async with create_async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


DbSessionDependency = Annotated[AsyncSession, Depends(get_db_session)]


async def get_unit_of_work(session: DbSessionDependency) -> UnitOfWorkPort:
    return UnitOfWork(session=session)


UnitOfWorkDependency = Annotated[UnitOfWorkPort, Depends(get_unit_of_work)]


async def get_request_permission_scope_cache(request: Request) -> PermissionScopeCache:
    cache = getattr(request.state, _PERMISSION_SCOPE_CACHE_STATE_KEY, None)
    if isinstance(cache, dict):
        return cast(PermissionScopeCache, cache)

    request_scope_cache: PermissionScopeCache = {}
    setattr(request.state, _PERMISSION_SCOPE_CACHE_STATE_KEY, request_scope_cache)
    return request_scope_cache


PermissionScopeCacheDependency = Annotated[PermissionScopeCache, Depends(get_request_permission_scope_cache)]


async def get_auth_repository(session: DbSessionDependency):
    return AuthRepository(session=session)


AuthRepositoryDependency = Annotated[AuthRepository, Depends(get_auth_repository)]


async def get_clients_repository(session: DbSessionDependency):
    return ClientsRepository(session=session)


ClientsRepositoryDependency = Annotated[ClientsRepository, Depends(get_clients_repository)]


async def get_matters_repository(session: DbSessionDependency):
    return MattersRepository(session=session)


MattersRepositoryDependency = Annotated[MattersRepository, Depends(get_matters_repository)]


async def get_matter_notes_repository(session: DbSessionDependency):
    return MatterNotesRepository(session=session)


MatterNotesRepositoryDependency = Annotated[MatterNotesRepository, Depends(get_matter_notes_repository)]


async def get_matter_tasks_repository(session: DbSessionDependency):
    return MatterTasksRepository(session=session)


MatterTasksRepositoryDependency = Annotated[MatterTasksRepository, Depends(get_matter_tasks_repository)]


async def get_matter_payments_repository(session: DbSessionDependency):
    return MatterPaymentsRepository(session=session)


MatterPaymentsRepositoryDependency = Annotated[MatterPaymentsRepository, Depends(get_matter_payments_repository)]


async def get_matter_calculations_repository(session: DbSessionDependency):
    return MatterCalculationsRepository(session=session)


MatterCalculationsRepositoryDependency = Annotated[
    MatterCalculationsRepository, Depends(get_matter_calculations_repository)
]


async def get_matter_checklists_repository(session: DbSessionDependency):
    return MatterChecklistsRepository(session=session)


MatterChecklistsRepositoryDependency = Annotated[MatterChecklistsRepository, Depends(get_matter_checklists_repository)]


async def get_matter_documents_repository(session: DbSessionDependency):
    return MatterDocumentsRepository(session=session)


MatterDocumentsRepositoryDependency = Annotated[MatterDocumentsRepository, Depends(get_matter_documents_repository)]


async def get_rbac_repository(session: DbSessionDependency):
    return RBACRepository(session=session)


RBACRepositoryDependency = Annotated[RBACRepository, Depends(get_rbac_repository)]


async def get_audit_log_repository(session: DbSessionDependency):
    return AuditLogRepository(session=session)


AuditLogRepositoryDependency = Annotated[AuditLogRepository, Depends(get_audit_log_repository)]


async def get_outbox_repository(session: DbSessionDependency):
    return OutboxRepository(session=session)


OutboxRepositoryDependency = Annotated[OutboxRepository, Depends(get_outbox_repository)]


async def get_auth_settings() -> AuthSettings:
    return AuthSettings()


AuthSettingsDependency = Annotated[AuthSettings, Depends(get_auth_settings)]


async def get_file_storage() -> FileStoragePort:
    return S3FileStorage()


FileStorageDependency = Annotated[FileStoragePort, Depends(get_file_storage)]


async def get_pdf_text_extractor() -> PdfTextExtractorPort:
    return PyPdfTextExtractor()


PdfTextExtractorDependency = Annotated[PdfTextExtractorPort, Depends(get_pdf_text_extractor)]


async def get_object_storage_settings() -> ObjectStorageSettings:
    return ObjectStorageSettings()


ObjectStorageSettingsDependency = Annotated[ObjectStorageSettings, Depends(get_object_storage_settings)]


async def get_matter_document_settings() -> MatterDocumentSettings:
    return MatterDocumentSettings()


MatterDocumentSettingsDependency = Annotated[MatterDocumentSettings, Depends(get_matter_document_settings)]


async def get_password_service() -> PasswordServicePort:
    return Argon2PasswordService()


PasswordServiceDependency = Annotated[PasswordServicePort, Depends(get_password_service)]


async def get_token_service(auth_settings: AuthSettingsDependency) -> TokenServicePort:
    return JwtTokenService(auth_settings)


TokenServiceDependency = Annotated[TokenServicePort, Depends(get_token_service)]


async def get_auth_service(
    auth_repository: AuthRepositoryDependency,
    auth_settings: AuthSettingsDependency,
    token_service: TokenServiceDependency,
    password_service: PasswordServiceDependency,
    unit_of_work: UnitOfWorkDependency,
    permission_scope_cache: PermissionScopeCacheDependency,
) -> AuthServicePort:
    return AuthService(
        auth_repository=auth_repository,
        unit_of_work=unit_of_work,
        auth_settings=auth_settings,
        token_service=token_service,
        password_service=password_service,
        permission_scope_cache=permission_scope_cache,
    )


AuthServiceDependency = Annotated[AuthServicePort, Depends(get_auth_service)]


async def get_ai_credential_settings() -> AiCredentialSettings:
    return AiCredentialSettings()


async def get_secret_encryption(
    settings: Annotated[AiCredentialSettings, Depends(get_ai_credential_settings)],
) -> SecretEncryptionPort:
    import base64

    return AesGcmSecretEncryption(base64.urlsafe_b64decode(settings.AI_CREDENTIAL_ENCRYPTION_KEY.get_secret_value()))


async def get_ai_credentials_repository(session: DbSessionDependency) -> AiCredentialsRepository:
    return AiCredentialsRepository(session=session)


async def get_ai_credentials_service(
    repository: Annotated[AiCredentialsRepository, Depends(get_ai_credentials_repository)],
    unit_of_work: UnitOfWorkDependency,
    encryption: Annotated[SecretEncryptionPort, Depends(get_secret_encryption)],
) -> AiCredentialsService:
    return AiCredentialsService(repository=repository, unit_of_work=unit_of_work, encryption=encryption)


AiCredentialsServiceDependency = Annotated[AiCredentialsService, Depends(get_ai_credentials_service)]


async def get_ai_jobs_repository(session: DbSessionDependency) -> AIJobsRepository:
    return AIJobsRepository(session=session)


async def get_ai_jobs_service(
    repository: Annotated[AIJobsRepository, Depends(get_ai_jobs_repository)],
    unit_of_work: UnitOfWorkDependency,
) -> AIJobsService:
    return AIJobsService(repository=repository, unit_of_work=unit_of_work)


AiJobsServiceDependency = Annotated[AIJobsService, Depends(get_ai_jobs_service)]


async def get_rbac_service(
    rbac_repository: RBACRepositoryDependency,
    unit_of_work: UnitOfWorkDependency,
) -> RBACServicePort:
    return RBACService(
        rbac_repository=rbac_repository,
        unit_of_work=unit_of_work,
    )


RBACServiceDependency = Annotated[RBACServicePort, Depends(get_rbac_service)]


async def get_audit_log_service(
    audit_log_repository: AuditLogRepositoryDependency,
) -> AuditLogServicePort:
    return AuditLogService(audit_log_repository=audit_log_repository)


AuditLogServiceDependency = Annotated[AuditLogServicePort, Depends(get_audit_log_service)]


async def get_dashboard_service(
    clients_repository: ClientsRepositoryDependency,
    matters_repository: MattersRepositoryDependency,
    tasks_repository: MatterTasksRepositoryDependency,
) -> DashboardServicePort:
    return DashboardService(
        clients_repository=clients_repository,
        matters_repository=matters_repository,
        tasks_repository=tasks_repository,
    )


DashboardServiceDependency = Annotated[DashboardServicePort, Depends(get_dashboard_service)]


async def get_clients_service(
    repository: ClientsRepositoryDependency, unit_of_work: UnitOfWorkDependency
) -> ClientsServicePort:
    return ClientsService(repository=repository, unit_of_work=unit_of_work)


ClientsServiceDependency = Annotated[ClientsServicePort, Depends(get_clients_service)]


async def get_matters_service(
    repository: MattersRepositoryDependency,
    clients_repository: ClientsRepositoryDependency,
    unit_of_work: UnitOfWorkDependency,
) -> MattersServicePort:
    return MattersService(repository=repository, clients_repository=clients_repository, unit_of_work=unit_of_work)


MattersServiceDependency = Annotated[MattersServicePort, Depends(get_matters_service)]


async def get_matter_notes_service(
    repository: MatterNotesRepositoryDependency,
    matters_repository: MattersRepositoryDependency,
    unit_of_work: UnitOfWorkDependency,
) -> MatterNotesServicePort:
    return MatterNotesService(repository=repository, matters_repository=matters_repository, unit_of_work=unit_of_work)


MatterNotesServiceDependency = Annotated[MatterNotesServicePort, Depends(get_matter_notes_service)]


async def get_matter_tasks_service(
    repository: MatterTasksRepositoryDependency,
    matters_repository: MattersRepositoryDependency,
    unit_of_work: UnitOfWorkDependency,
) -> MatterTasksServicePort:
    return MatterTasksService(repository=repository, matters_repository=matters_repository, unit_of_work=unit_of_work)


MatterTasksServiceDependency = Annotated[MatterTasksServicePort, Depends(get_matter_tasks_service)]


async def get_matter_payments_service(
    repository: MatterPaymentsRepositoryDependency,
    matters_repository: MattersRepositoryDependency,
    unit_of_work: UnitOfWorkDependency,
) -> MatterPaymentsServicePort:
    return MatterPaymentsService(
        repository=repository, matters_repository=matters_repository, unit_of_work=unit_of_work
    )


MatterPaymentsServiceDependency = Annotated[MatterPaymentsServicePort, Depends(get_matter_payments_service)]


async def get_matter_calculations_service(
    repository: MatterCalculationsRepositoryDependency,
    matters_repository: MattersRepositoryDependency,
    unit_of_work: UnitOfWorkDependency,
):
    return MatterCalculationsService(repository, matters_repository, unit_of_work)


MatterCalculationsServiceDependency = Annotated[MatterCalculationsService, Depends(get_matter_calculations_service)]


async def get_matter_checklists_service(
    repository: MatterChecklistsRepositoryDependency,
    matters_repository: MattersRepositoryDependency,
    unit_of_work: UnitOfWorkDependency,
) -> MatterChecklistsServicePort:
    return MatterChecklistsService(
        repository=repository, matters_repository=matters_repository, unit_of_work=unit_of_work
    )


MatterChecklistsServiceDependency = Annotated[MatterChecklistsServicePort, Depends(get_matter_checklists_service)]


async def get_matter_documents_service(
    repository: MatterDocumentsRepositoryDependency,
    matters_repository: MattersRepositoryDependency,
    unit_of_work: UnitOfWorkDependency,
    storage: FileStorageDependency,
    storage_settings: ObjectStorageSettingsDependency,
    settings: MatterDocumentSettingsDependency,
    pdf_text_extractor: PdfTextExtractorDependency,
) -> MatterDocumentsServicePort:
    return MatterDocumentsService(
        repository=repository,
        matters_repository=matters_repository,
        unit_of_work=unit_of_work,
        storage=storage,
        storage_settings=storage_settings,
        settings=settings,
        pdf_text_extractor=pdf_text_extractor,
    )


MatterDocumentsServiceDependency = Annotated[MatterDocumentsServicePort, Depends(get_matter_documents_service)]


async def get_outbox_service(
    outbox_repository: OutboxRepositoryDependency,
    unit_of_work: UnitOfWorkDependency,
) -> OutboxServicePort:
    return OutboxService(
        outbox_repository=outbox_repository,
        unit_of_work=unit_of_work,
    )


OutboxServiceDependency = Annotated[OutboxServicePort, Depends(get_outbox_service)]
