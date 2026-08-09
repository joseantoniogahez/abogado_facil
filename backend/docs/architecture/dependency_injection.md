# Dependency Injection Guide

## Goal

Keep wiring in one place and keep feature modules focused on behavior.

## Current layout

Dependency providers live in `app/core/setup/dependencies.py`.

Main provider groups:

- Request and transaction state: `get_db_session`, `get_unit_of_work`, and
  `get_request_permission_scope_cache`.
- Feature repositories: auth, audit log, RBAC, outbox, clients, matters, notes, checklists, tasks,
  payments, calculations, documents, AI credentials, AI jobs, AI assistance, and AI insights.
- Feature services: auth, audit log, RBAC, outbox, dashboard, clients, matters, notes, checklists,
  tasks, payments, calculations, documents, AI credentials, AI jobs, AI assistance, AI insights,
  and document templates.
- Security and settings: `get_auth_settings`, `get_ai_credential_settings`,
  `get_ai_limit_settings`, `get_secret_encryption`, `get_password_service`, and
  `get_token_service`.
- Integration adapters and settings: `get_file_storage`, `get_pdf_text_extractor`,
  `get_object_storage_settings`, `get_matter_document_settings`, `get_ai_queue_settings`, and
  `get_job_scheduler`, plus `get_ai_provider_factory` for scoped provider construction.

The executable provider catalog is `app/core/setup/dependencies.py`; add new request-scoped wiring
there and update this grouping when a new provider category is introduced.

Feature-local auth dependencies live in:

- `app/features/auth/dependencies.py`
- `app/features/audit_log/dependencies.py`
- `app/features/rbac/dependencies.py`
- `app/core/authorization/dependencies.py`

## Router usage

Routers consume typed dependency aliases instead of constructing services directly.

Example:

```python
@router.get("/roles", response_model=list[RBACRole], **GET_ROLES_DOC)
async def list_roles(
    rbac_service: RBACServiceDependency,
    _authorized_user: RBACRoleAdminAuth,
) -> list[RBACRole]:
    roles = await rbac_service.list_roles()
    return to_role_response_list(roles)
```

## Transaction model

`get_db_session` creates one `AsyncSession` per request.
That same session is reused by repositories and `UnitOfWork`, so one use case runs inside one transaction scope.

Practical effect:

- success path: commit at Unit of Work exit
- failure path: rollback for all pending writes in scope

## Test overrides

Use `app.dependency_overrides` in tests.

```python
from app.core.setup.dependencies import get_db_session
from app.main import app

async def override_db_session():
    async with mock_database.Session() as session:
        yield session

app.dependency_overrides[get_db_session] = override_db_session
```

Clear overrides during teardown:

```python
app.dependency_overrides.clear()
```

External adapters are overridden through their provider function, not by patching concrete classes. Tests
override `get_file_storage` with the test-only `FakeFileStorage`; focused `S3FileStorage` tests inject a mocked
SDK client and do not access the network.
