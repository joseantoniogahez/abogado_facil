# Feature-Based Backend Architecture

## Goal

Use a strict feature-based layout with a small shared core.

Current top-level shape:

- `app/core`
- `app/features`
- `app/integrations`

## Object storage port and adapter

- `app/integrations/files.py` owns the provider-neutral `FileStoragePort` and safe error types.
- The port supports storing bytes, streaming reads in bounded chunks, and idempotent-aware deletion.
- `app/integrations/s3.py` is the only production module allowed to import the boto3 S3 SDK.
- `utils/testing_support/file_storage.py` provides the in-memory test adapter; production packages do not ship test fakes.
- Features pass bucket/path contracts through the port and never receive SDK exceptions or credentials.
- Provider failures are translated to messages that omit endpoints, credentials, and response details.
- S3 connection/read timeouts and path-style addressing are runtime configuration, allowing MinIO locally
  and another S3-compatible endpoint in production.
- Automated tests replace the storage dependency with the in-memory adapter or inject a mocked S3 client;
  they never require a reachable object-storage service.

## PDF text extraction port and adapter

- `app/integrations/pdf_text.py` owns `PdfTextExtractorPort` and the local `pypdf` adapter.
- The matter-document service invokes the port only for validated PDFs and persists normalized text.
- Empty text layers and parser failures are explicit, non-fatal states; OCR and external providers
  are outside this adapter.
- Parser exceptions are wrapped and never expose document content or parser details through the API.

## AI provider port and adapters

- `app/integrations/ai_providers.py` owns the provider-neutral `AiProviderPort`, request/response
  contracts, and `OpenAIProvider`, `GeminiProvider`, and `MockProvider` adapters.
- OpenAI and Gemini use an injected HTTP transport so tests never call external providers and future
  runtime wiring can own timeouts, retries, and observability.
- Provider credentials are transported only in headers. Gemini uses `x-goog-api-key`; credentials
  must never be placed in URLs that can be retained by access logs or intermediaries.
- Provider errors are normalized to `AiProviderError` with a closed provider-neutral code, public
  message, and explicit retry decision. API keys, URLs, response bodies, and provider error details
  are never included in the exception or its public contract. The canonical catalog and HTTP
  translation live in `docs/operations/ai_provider_errors.md`.
- This port does not decide whether a user has a valid BYOK credential or persist results.
  `app/features/ai_execution/service.py` owns the implemented BYOK validation and provider
  construction policy. `app/features/ai_jobs` owns the persistent, tenant-scoped execution
  lifecycle; future AI use-case services will validate and supply structured results.

## Background job port and RQ adapter

- `app/integrations/jobs.py` owns the provider-neutral `JobSchedulerPort`.
- `app/integrations/rq_jobs.py` implements RQ/Redis dispatch with JSON serialization.
- The adapter accepts only catalogued job names and opaque `execution_id` values.
- Deterministic IDs plus RQ uniqueness prevent duplicate enqueues; timeout, TTL and retry/backoff
  policy come from validated settings.
- RQ never owns legal context or AI results. Workers reconstruct authorized context from
  PostgreSQL, and `AIJob` remains the lifecycle source of truth.

## Ownership

`app/core` owns cross-feature concerns only:

- config
- database runtime and Unit of Work
- shared authorization primitives
- shared security helpers
- shared error types and handlers
- shared OpenAPI/error helpers
- app factory and router registration

`app/features/<feature>` owns vertical slices:

- router
- feature service
- feature repository
- feature schemas
- feature models
- feature-local OpenAPI metadata

Current features:

- `ai_credentials`
- `ai_execution`
- `ai_jobs`
- `audit_log`
- `auth`
- `clients`
- `dashboard`
- `health`
- `matter_calculations`
- `matter_checklists`
- `matter_documents`
- `matter_notes`
- `matter_payments`
- `matter_tasks`
- `matters`
- `outbox`
- `rbac`

`outbox`, `ai_execution`, and `ai_jobs` are service capabilities without public routers. The
remaining routed features are registered through `app/core/setup/routers.py`.

## Dependency direction

Preferred direction:

`feature router -> feature service -> feature repository -> core db/runtime`

Allowed shared imports:

- features may import `app/core/*`
- a feature may import another feature only for explicitly shared records/models that already exist in production flow
- feature-local authorization aliases may import `app.features.auth.principal` when they need the authenticated principal type
- repositories must not depend on router or setup modules

## Practical rules

Routers:

- own HTTP concerns only
- do not build services directly
- do not contain business logic

Services:

- own use-case orchestration
- depend on ports/contracts where useful
- do not depend on FastAPI wiring

Repositories:

- own ORM access and query construction
- translate persistence failures before they cross upward

`__init__.py`:

- package markers and re-exports only
- no runtime logic

## Adding a new feature

When introducing a new vertical slice:

1. Create `app/features/<feature>/`.
1. Add `router.py`, `service.py`, `repository.py`, `schemas/api.py`, `schemas/app.py`.
1. Add `models.py` only if the feature owns persistence tables.
1. Register the router in `app/core/setup/routers.py`.
1. Add tests and docs for the new public surface.

## Anti-patterns

- rebuilding global cross-feature layers that bypass `app/features/<feature>` ownership
- moving feature-specific helpers into `app/core` too early
- putting business logic in dependency providers
- leaving public permissions undocumented
