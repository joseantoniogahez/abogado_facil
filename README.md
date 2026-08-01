# Abogado Fácil

SaaS web para abogados independientes y despachos pequeños con expedientes, tareas, documentos e IA BYOK.

- Backend: FastAPI + SQLAlchemy (async) + Alembic
- Frontend: Vite + React 19 + TypeScript
- Database: PostgreSQL 18.2 (`postgres:18.2`)
- Background jobs: RQ 2.10 + Redis
- Orchestration: Docker Compose

## README Map

- `README.md` (this file): repository architecture and multi-service run flow.
- `backend/README.md`: backend-only setup, API behavior, migrations, and backend tests.
- `frontend/README.md`: frontend-only setup, scripts, tests, and API client configuration.
- `docs/product/README.md`: current product capabilities, backlog, and implementation-plan indexes.
- `AGENTS.md`: AI assistant operating guide for this starter kit.
- `docs/ai/start_new_project.md`: new-project bootstrap workflow for turning this starter kit into
  a named application.

## Project Structure

- `backend/`: FastAPI API, models, services, migrations, backend tests
- `backend/docs/`: backend documentation (API endpoints, auth, RBAC, DI, OpenAPI pattern)
- `frontend/`: React SPA and frontend tests
- `frontend/docs/`: frontend documentation (routing, API sync, runtime config, quality gates)
- `docs/product/`: current functional capabilities, backlog, and pending/implemented plans
- `docs/ai/`: repository-level AI request templates and new-project bootstrap instructions
- `scripts/`: repository-level developer and AI workflow helpers
- `.github/workflows/ci.yaml`: CI validation for repository hooks, backend, and frontend
- `compose.yaml`: base multi-container stack
- `compose.override.yaml`: local development overrides loaded automatically by `docker compose`
- `compose.test.yaml`: isolated services for backend/frontend test runs
- `compose.prod.yaml`: production overrides (restart policy, persistent DB volume, prod project name)
- `.env_examples`: environment template used to create `.env`
- `.env`: environment file used by compose

## Prerequisites

- Docker Desktop (or Docker Engine + Compose plugin)
- Optional for local non-Docker workflows:
  - Python 3.14
  - Node.js >=22.23.1 (Node.js 22.23.1 is used by Docker/CI)
  - npm >=12.0.1

## Environment Setup

Create `.env` from `.env_examples` at repository root:

```bash
# macOS/Linux
cp .env_examples .env

# Windows PowerShell
Copy-Item .env_examples .env
```

See `.env_examples` for variable descriptions.

## Use This As a New Project Starter

Start with the detailed guide:

```bash
docs/ai/start_new_project.md
```

Quick flow:

```powershell
# preview identity changes
.\.venv\Scripts\python.exe scripts/bootstrap_new_app.py --app-name "Example Portal" --description "A portal for example workflows."

# apply after reviewing the preview
.\.venv\Scripts\python.exe scripts/bootstrap_new_app.py --app-name "Example Portal" --description "A portal for example workflows." --write
```

Then review `git diff`, create `.env` from `.env_examples`, run the validation gates listed in
`docs/ai/start_new_project.md`, and start the stack with `docker compose up --build`.

## Run Full Stack (Docker)

From repository root:

```bash
docker compose up --build
```

Endpoints:

- Frontend: `http://localhost:3000`
- API docs: `http://localhost:8000/docs`
- MinIO S3 API: `http://localhost:9000`
- MinIO console: `http://localhost:9001`

Notes:

- Backend runs Alembic migrations during startup (`backend/prestart.sh`); `ai-worker` clears that
  image entrypoint and waits for the backend healthcheck, so it never applies migrations.
- `ai-worker` runs one RQ worker with scheduler support, JSON serialization, bounded retries, and
  Redis payloads limited to opaque execution IDs.
- `compose.override.yaml` is loaded automatically for local runs and enables backend hot reload via bind mount.
- Frontend API target is controlled by `VITE_API_ORIGIN` and `VITE_API_BASE_PATH`.
- Vite env vars are baked into build output; rebuild frontend image after changing them.
- Compose creates the private `S3_BUCKET` idempotently. Object data lives in the named
  `object_storage_data` volume and survives container recreation.

## Run Tests (Docker Compose)

From repository root:

```bash
# Backend tests
docker compose -f compose.test.yaml run --rm backend-test

# Frontend tests
docker compose -f compose.test.yaml run --rm frontend-test

# Both (sequential)
docker compose -f compose.test.yaml run --rm backend-test && docker compose -f compose.test.yaml run --rm frontend-test
```

`compose.test.yaml` sets `name: abogado-facil-tests`, so test resources stay isolated from local development.

## GitHub Actions CI

The repository includes a GitHub Actions workflow at `.github/workflows/ci.yaml` for push and pull request validation.

It runs three independent quality gates:

- `pre-commit`: runs repository hooks in CI for both `pre-commit` and `pre-push` stages
- `backend`: runs `python -m pytest backend/tests --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=100`
- `frontend`: runs frontend quality gate (`npm --prefix frontend run check`), smoke e2e (`npm --prefix frontend run test:e2e:ci`), and production build

## Run Production Profile (Docker Compose)

From repository root:

```bash
docker compose -f compose.yaml -f compose.prod.yaml up --build -d
```

Production secrets and credentials:

- `compose.prod.yaml` sets `APP_ENV=prod`.
- Define `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`, `JWT_ISSUER`, and `JWT_AUDIENCE` in `.env` before starting.
- Define `AI_CREDENTIAL_ENCRYPTION_KEY` as URL-safe base64 for exactly 32 random bytes. Generate a
  production value with
  `.\.venv\Scripts\python.exe -c "import base64, secrets; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"`.
  Production startup rejects the local default from `.env_examples`.
- Define `S3_ENDPOINT_URL`, `S3_REGION`, `S3_BUCKET`, `S3_ACCESS_KEY`, and `S3_SECRET_KEY`; production
  has no object-storage credential defaults and does not publish MinIO ports.

Stop production stack:

```bash
docker compose -f compose.yaml -f compose.prod.yaml down
```

Before deployment, follow the PostgreSQL backup and restore-drill runbook in
`backend/docs/operations/postgresql_backups.md`.

`compose.prod.yaml` sets `name: abogado-facil-prod`, so production resources stay isolated from dev/test projects.

If production `database` keeps restarting due to an old volume mount path, recreate the production volume:

```bash
docker compose -f compose.yaml -f compose.prod.yaml down -v
docker compose -f compose.yaml -f compose.prod.yaml up --build -d
```

## API Base Path Contract (`/v1`)

- Backend routes are mounted under `/v1`.
- Frontend default is `VITE_API_BASE_PATH=/v1`.
- `API_PATH` controls FastAPI `root_path` metadata for proxy deployments only; it does not remount routes.

## Repository Tooling (Root)

The repository uses a root virtual environment for shared tooling and hooks.

Local `pre-commit` hooks depend on more than the root Python environment:

- Python 3.14 for Python-based hooks
- Node.js >=22.23.1 (Node.js 22.23.1 in Docker/CI) and npm 12.0.1+ for frontend ESLint and typecheck hooks
- Docker Desktop (or Docker Engine + Compose plugin) for `hadolint` and `docker compose config` hooks
- A local `.env` copied from `.env_examples`, because compose validation hooks resolve environment variables from it

Create and activate:

```bash
# from repo root
python -m venv .venv

# Windows PowerShell
.venv/Scripts/Activate.ps1

# macOS/Linux
source .venv/bin/activate
```

Install tooling:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
npm --prefix frontend install
.\.venv\Scripts\python.exe -m pre_commit install --install-hooks --hook-type pre-commit --hook-type pre-push
```

The root `requirements.txt` is the umbrella Python manifest used by CI; it includes backend runtime dependencies, backend test dependencies, and repository tooling.

Before running hooks, make sure Docker is running so local Docker-based hooks can start successfully.

Run repository hooks:

```powershell
.\.venv\Scripts\python.exe -m pre_commit run --all-files
```

Run heavier pre-push hooks locally:

```powershell
.\.venv\Scripts\python.exe -m pre_commit run --all-files --hook-stage pre-push
```

## AI Workflow Helpers

Preview feature scaffolds:

```powershell
.\.venv\Scripts\python.exe scripts/scaffold_feature.py full-stack audit-log --route /admin/audit-log --with-model --dry-run
```

Preview new-app identity bootstrap:

```powershell
.\.venv\Scripts\python.exe scripts/bootstrap_new_app.py --app-name "Example Portal" --description "A portal for example workflows."
```
