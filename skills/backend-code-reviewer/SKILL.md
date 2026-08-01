---
name: backend-code-reviewer
description: Review FastAPI backend diffs, branches, pull requests, or readiness states for correctness, security, regressions, contract drift, missing tests, and validation gaps. Use when changes touch backend routers, services, repositories, schemas, models, migrations, auth, RBAC, integrations, AI execution, OpenAPI, or backend documentation.
---

# Backend Code Reviewer

## Workflow

1. Read `AGENTS.md`, `backend/docs/backend_playbook.md`, and
   `backend/docs/foundation_status.md`.
1. Inspect the changed-file set and nearby code before choosing affected operation and architecture
   documents.
1. Treat the official FastAPI skill routed by `skills/fastapi-agents/SKILL.md` as mandatory when
   FastAPI or Starlette behavior is involved.
1. Trace each changed route through dependency injection, service orchestration, repository or
   integration boundaries, transaction handling, and response/error mapping.
1. Compare observable behavior with endpoint, authentication, authorization, error, OpenAPI, and
   product contracts.
1. Inspect focused tests and run the smallest relevant checks needed to prove or disprove suspected
   issues.
1. Report findings first, ordered by severity, with file and line references. Do not modify code
   unless the user also requests fixes.

## Review Gates

- Confirm protected endpoints use the intended authentication or permission dependency and preserve
  tenant isolation.
- Confirm writes use the documented UnitOfWork boundary and repositories do not commit directly.
- Confirm migrations preserve data integrity, downgrade expectations, constraints, and model parity.
- Confirm provider and storage failures are normalized, redacted, observable, and tested.
- Confirm router registration, OpenAPI output, endpoint inventory, permission matrix, and error
  mapping remain synchronized.
- Confirm tests cover successful behavior, validation, authorization, not-found isolation, failure
  paths, and regression-prone boundaries.
- Distinguish proven defects from open questions and validation gaps.

## Validation

Prefer targeted tests while investigating. For release-level confidence, use the backend gates from
`AGENTS.md`, including the 100% coverage command and OpenAPI sync/check when the public contract is
affected.

## Output

Use this order:

1. Findings by severity.
1. Open questions or assumptions.
1. Validation performed and gaps.
1. Concise summary and residual risk.

For every finding, state the concrete defect, impact, evidence, and smallest viable correction. If
no findings remain, say so explicitly and identify any checks that were not run.
