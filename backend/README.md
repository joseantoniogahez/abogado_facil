# backend (FastAPI API)

Reusable FastAPI backend template organized by feature.

For repository-level setup and multi-service Docker flows, see `../README.md`.

## Technical Documentation Map

- `docs/backend_playbook.md`: canonical architecture and engineering rules.
- `docs/foundation_status.md`: canonical snapshot of current backend foundation state and quality gates.
- `docs/README.md`: role-based reading order for AI, reviewer, and requester workflows.
- `docs/operations/*.md`: API/auth/authz/error runtime contracts.
- `docs/architecture/*.md`: DI, UoW, router registration, and OpenAPI design patterns.
- `docs/templates/*.md`: templates to request AI-driven features, integrations, and code changes.

## Development Environment (Local Python)

This project uses the repository virtual environment `../.venv`.

From repo root:

```bash
python -m venv .venv
```

Activate:

```bash
# Windows PowerShell
.venv/Scripts/Activate.ps1

# macOS/Linux
source .venv/bin/activate
```

Install dependencies:

```powershell
# requirements.txt at repo root is the umbrella manifest used by CI.
# It includes backend runtime dependencies, backend test dependencies, and shared tooling.
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Runtime Configuration

Default local profile when backend environment variables are unset outside Docker (SQLite):

- `APP_ENV=local`
- `DB_TYPE=sqlite+aiosqlite`
- `DB_NAME=app.db`
- `API_PATH=`
- `API_CORS_ORIGINS=`
- `LOG_LEVEL=WARNING`

When configured, `API_CORS_ORIGINS` is a comma-separated list of explicit `http`/`https` browser
origins without paths. The API permits only `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, and `OPTIONS`,
and only `Accept`, `Authorization`, and `Content-Type` request headers. Credentials are enabled for
those explicit origins and `X-Request-ID` is exposed for frontend error correlation. Wildcard origins
are rejected in every environment.

JWT defaults for `local/test`:

- `JWT_SECRET_KEY=local-dev-jwt-secret-change-me-now`
- `JWT_ALGORITHM=HS256`
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30`
- `JWT_ISSUER=abogado-facil`
- `JWT_AUDIENCE=abogado-facil-api`

BYOK credential encryption:

- `AI_CREDENTIAL_ENCRYPTION_KEY` must be URL-safe base64 that decodes to exactly 32 bytes.
- Direct local execution uses a development-only default when the variable is unset.
- Production requires an explicit unique value and rejects the local default. Generate one with
  `.\.venv\Scripts\python.exe -c "import base64, secrets; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"`.

Required object storage configuration:

- Define `S3_ENDPOINT_URL`, `S3_REGION`, `S3_BUCKET`, `S3_ACCESS_KEY`, and `S3_SECRET_KEY` in every environment.
- Compose supplies the values from the repository `.env`; direct backend execution must export them first.
- `S3_PATH_STYLE` defaults to `true`.
- Connection/read timeouts default to 3/10 seconds.
- `MATTER_DOCUMENT_MAX_SIZE_BYTES` defaults to 10 MiB and `MATTER_DOCUMENT_MAX_PER_MATTER`
  defaults to 50. Uploads are serialized per matter in PostgreSQL while enforcing the quota.
- `AI_INPUT_MAX_CHARS` defaults to 20,000 and `AI_OUTPUT_MAX_TOKENS` defaults to 1,200.
- `DOCUMENT_DRAFT_FIELD_MAX_CHARS` defaults to 20,000 per field and
  `DOCUMENT_DRAFT_OUTPUT_MAX_TOKENS` defaults to 1,800. Values above defensive schema ceilings are
  rejected at startup.

Features consume `FileStoragePort`; provider code is isolated in `app/integrations/s3.py`, and tests
use a test-only `FakeFileStorage` or a mocked SDK client without Docker or network access. No feature should
import `boto3` directly.

AI observability is metadata-only: prompts, document text, credentials, tokens, authorization
headers, and provider exception details must not be passed to technical logs. OpenAI and Gemini use
their pinned official asynchronous Python SDKs through injectable clients, with SDK retries disabled
for OpenAI so RQ remains the retry owner. Use
`app.core.common.observability.log_layer_event` for structured events; sensitive field names are
redacted centrally and tests enforce the negative contract. Provider credentials belong in
provider authentication details, including credentials, never enter application URLs or contracts.

AI background work uses RQ 2.10 over the shared Redis service. The producer uses JSON serialization
and enqueues only the opaque `execution_id`; prompts, credentials, context, results, and provider
errors remain outside Redis. `AI_QUEUE_JOB_TIMEOUT_SECONDS`, `AI_QUEUE_MAX_RETRIES`,
`AI_QUEUE_RETRY_BACKOFF_SECONDS`, queue/result/failure TTLs, and `AI_QUEUE_NAME` control the worker.
Compose starts one worker with scheduler support by default so delayed retry intervals work.

PDF uploads are parsed locally through `PdfTextExtractorPort`. When a text layer is available, its
normalized content is stored with the document metadata for future AI workflows. Scanned PDFs are
kept with an `empty` extraction state and are not sent through OCR; parser failures are non-fatal and
record `failed`. Existing documents remain `unprocessed`, and non-PDF files are `not_applicable`.

Repository-level Docker Compose uses `.env` values from `.env_examples` and runs the backend against PostgreSQL by default (`DB_TYPE=postgresql+asyncpg`, `DB_HOST=abogado_facil_db`, `DB_NAME=abogado_facil_main`).

For network databases, set:

- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`
- `DB_NAME`

## Run Backend Locally

From repo root:

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- API docs: `http://localhost:8000/docs`
- Base API namespace: `/v1`

## Migrations and Bootstrap

From `backend/`:

```bash
..\.venv\Scripts\python.exe -m alembic upgrade head
```

Create a migration:

```powershell
..\.venv\Scripts\python.exe -m alembic revision --autogenerate -m "describe change"
```

Seed RBAC baseline after migrations:

```powershell
..\.venv\Scripts\python.exe -m utils.rbac_bootstrap --admin-email admin@example.com --admin-password "StrongSeed9"
```

If you started services with `docker compose up --build` and want to run bootstrap from local PowerShell (without entering the container), run from `backend/`:

```powershell
$env:DB_TYPE = "postgresql+asyncpg"; $env:DB_HOST = "localhost"; $env:DB_PORT = "5432"; $env:DB_NAME = "abogado_facil_main"; $env:DB_USER = "my_admin"; $env:DB_PASSWORD = "{{DB_PASSWORD}}"; ..\.venv\Scripts\python.exe -m utils.rbac_bootstrap --admin-email admin@example.com --admin-password "StrongSeed9"
```

macOS/Linux (bash/zsh) equivalent:

```bash
DB_TYPE="postgresql+asyncpg" DB_HOST="localhost" DB_PORT="5432" DB_NAME="abogado_facil_main" DB_USER="my_admin" DB_PASSWORD="{{DB_PASSWORD}}" ../.venv/bin/python -m utils.rbac_bootstrap --admin-email admin@example.com --admin-password "StrongSeed9"
```

Note: use `DB_HOST=localhost` for host-side execution.

This bootstrap command:

- upserts base permissions,
- creates missing base roles,
- creates the admin user only if missing,
- ensures admin role assignment.

Base permissions:

- `audit_logs:read`
- `roles:manage`
- `role_permissions:manage`
- `user_roles:manage`
- `users:manage`

## Testing and Validation

Run from repo root:

```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests
```

CI-equivalent coverage gate:

```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=100
```

Dockerized backend test run (isolated):

```bash
docker compose -f compose.test.yaml run --rm backend-test
```

## Production Preparation and Run

Before production startup (`APP_ENV=prod`), set strong values for:

- `JWT_SECRET_KEY`
- `JWT_ALGORITHM`
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`
- `JWT_ISSUER`
- `JWT_AUDIENCE`
- `AI_CREDENTIAL_ENCRYPTION_KEY`
- `S3_ENDPOINT_URL`, `S3_REGION`, `S3_BUCKET`, `S3_ACCESS_KEY`, and `S3_SECRET_KEY`

Run production stack from repo root:

```bash
docker compose -f compose.yaml -f compose.prod.yaml up --build -d
```

Stop production stack:

```bash
docker compose -f compose.yaml -f compose.prod.yaml down
```

## Current Backend Layout

The backend keeps shared runtime concerns in `app/core`, integrations in `app/integrations`, and
vertical product slices in `app/features`:

- `app/core`: shared runtime, config, security, authorization, db, setup
- `app/integrations`: S3-compatible storage, PDF text extraction, jobs, broker, search, and outbox adapters
- `app/features/auth`: register, login, current-user profile
- `app/features/audit_log`: administrator audit log review
- `app/features/health`: health endpoint
- `app/features/rbac`: roles, permissions, user-role assignment
- `app/features/dashboard`: firm-scoped dashboard summary
- `app/features/clients`: client management
- `app/features/matters`: matter management
- `app/features/matter_notes`: matter notes
- `app/features/matter_checklists`: matter checklists
- `app/features/matter_tasks`: matter tasks and upcoming reminders
- `app/features/matter_payments`: matter fees and payments
- `app/features/matter_calculations`: deterministic matter calculations
- `app/features/matter_documents`: matter document metadata and storage operations
- `app/features/outbox`: outbox capability
- `app/features/ai_credentials`: encrypted per-user BYOK credential management
- `app/features/ai_execution`: scoped BYOK validation before provider construction
