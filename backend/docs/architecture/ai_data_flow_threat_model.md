# AI Data Flow and Threat Model

## Scope

This document joins the backend AI contracts into one trust-boundary view. It covers the current
public AI assistance and document-draft flows after all P0-IA gates were completed.

## Data Flow

```mermaid
flowchart LR
    U[Authenticated user] --> A[Product use case]
    A --> J[(PostgreSQL AIJob)]
    A --> Q[RQ / Redis]
    Q --> W[AI worker]
    W --> J
    W --> C[Minimized context builder]
    C --> P[Provider adapter]
    K[(Encrypted BYOK)] --> W
    P --> V[Schema validator]
    V --> J
    J --> A
```

1. The product use case authenticates the user and retrieves matter data scoped by `firm_id` and
   `user_id`.
1. It creates an `AIJob` containing correlation, provider, model, function and schema versions, but
   no prompt, credential or document text.
1. RQ/Redis receives only the catalogued handler and opaque `execution_id`.
1. The worker reloads the tenant-scoped job and data from PostgreSQL, decrypts the user's BYOK key
   in memory, and builds context through `build_minimized_ai_context`.
1. The provider receives only the sealed `MinimizedAIContext`. Provider text remains untrusted.
1. `validate_ai_output` parses the complete response against the function's Pydantic schema and
   returns a sealed `ValidatedAIOutput`.
1. `AIJobsService.succeed` verifies the schema version and persists a defensive copy of validated
   JSON. Logs and metrics contain operational metadata only.

## Trust Boundaries

| Boundary                      | Untrusted input                   | Required control                                                                                                    |
| ----------------------------- | --------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| Browser to API                | identity claims, request data     | authentication, tenant-scoped authorization, input schemas                                                          |
| PostgreSQL to worker          | mutable product/document data     | reload by job `firm_id` and `user_id`; explicit allowlist                                                           |
| Application to Redis          | producer-controlled job command   | catalogued handler, JSON serializer, opaque execution ID only                                                       |
| Stored credential to provider | encrypted secret at rest          | production key wiring, scoped lookup, decrypt only in memory                                                        |
| Document/context to model     | legal and user-authored text      | minimization, escaped untrusted-data envelope, separate system instruction, no tools                                |
| Provider to application       | arbitrary text and malformed JSON | closed error taxonomy and sealed schema validation result                                                           |
| Runtime to logs/metrics       | correlation and failure metadata  | allowlisted fields and content-free context/output representations; no prompts, documents, responses or credentials |

## Threats and Controls

| Threat                          | Current control                                                                                | Residual risk / next gate                                                                    |
| ------------------------------- | ---------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| Cross-firm or cross-user access | every `AIJob` read and mutation requires both IDs; context must be loaded with the same scope  | negative multi-user tests remain mandatory per feature                                       |
| Credential disclosure           | AES-GCM at rest, keys omitted from API and logs, provider headers only                         | operational key rotation and incident procedures remain deployment responsibilities          |
| Sensitive data in Redis         | JSON payload contains only `execution_id`; deterministic catalogued jobs                       | real handlers must preserve this boundary                                                    |
| Context over-collection         | sealed builder requires authorized and necessary fields and bounded payloads                   | product allowlists must be reviewed per function                                             |
| Forged validation marker        | `MinimizedAIContext` and `ValidatedAIOutput` reject direct construction                        | Python process memory is trusted application code; unsafe reflection is outside the boundary |
| Mutating a validated result     | callers receive a defensive copy and persistence receives a fresh copy                         | schemas still need `extra="forbid"` and function-specific constraints                        |
| Provider error/content leakage  | normalized errors, redacted logs and content-free metrics                                      | provider SDK/transport changes require contract tests                                        |
| Prompt injection in documents   | trusted instruction and escaped untrusted data use separate provider channels; tools are empty | model output remains probabilistic and must pass schema validation plus `LEGAL-002A` review  |
| Autonomous legal action         | no tools; review is required and conversion is an explicit later action                        | users can still misuse a reviewed draft outside the application                              |

## Gate status and residual risk

`SEC-001B`, `SEC-001C`, `SEC-002`, `SEC-004`, `LEGAL-002A` and the structured-output, redaction and
BYOK gates are implemented and tested for the current synchronous product flows. Adding a new
function still requires its own closed schema, context allowlist, negative tenant tests and review
consumer tests. RQ remains an available transport contract; current assistance and document-draft
use cases execute synchronously and must not be described as queued handlers.

Residual risks are model bias or fabrication that remains schema-valid, provider availability and
quota, user misuse after copying, operational key rotation, and lack of production outcome samples.
None of these controls make the model a legal decision maker.

Canonical detailed contracts are:

- `../operations/ai_job_lifecycle.md`
- `../operations/rq_ai_queue.md`
- `../operations/ai_context_minimization.md`
- `../operations/document_prompt_injection.md`
- `../operations/structured_ai_outputs.md`
- `../operations/ai_provider_errors.md`
- `../operations/streaming_observability.md`
- `../operations/ai_metrics.md`
