---
name: frontend-code-reviewer
description: Review React frontend diffs, branches, pull requests, or readiness states for correctness, accessibility, security, regressions, API and route drift, missing tests, and validation gaps. Use when changes touch routes, pages, shared UI, API consumers, auth or RBAC screens, TanStack Query flows, runtime config, observability, e2e coverage, performance, or frontend documentation.
---

# Frontend Code Reviewer

## Workflow

1. Read `AGENTS.md`, `frontend/docs/frontend_playbook.md`, and
   `frontend/docs/foundation_status.md`.
1. Inspect the changed-file set and nearby code before choosing affected operation documents.
1. Trace each changed screen from route and access guard through API consumer, contract parser,
   query or mutation behavior, and rendered user states.
1. Compare behavior with route inventory, API consumer matrix, OpenAPI artifact, mutation policy,
   runtime configuration, security, observability, accessibility, e2e, and performance contracts.
1. Inspect focused tests and run the smallest relevant checks needed to prove or disprove suspected
   issues.
1. Report findings first, ordered by severity, with file and line references. Do not modify code
   unless the user also requests fixes.

## Review Gates

- Preserve `app -> features -> shared` dependency direction and centralized route composition.
- Confirm public, protected, and permission-gated routes match navigation visibility and direct
  navigation behavior.
- Confirm API calls use shared HTTP/error handling, validate responses, and remain synchronized with
  backend OpenAPI.
- Confirm mutation retry and invalidation behavior cannot duplicate writes or leave stale views.
- Confirm loading, empty, error, unauthorized, disabled, and success states are accessible and use
  catalogued user-facing text.
- Confirm structured diagnostics are redaction-safe and runtime errors remain observable.
- Confirm relevant component, contract, accessibility, e2e, and performance coverage moves with the
  behavior.
- Distinguish proven defects from open questions and validation gaps.

## Validation

Prefer targeted tests while investigating. For release-level confidence, use the frontend gates
from `AGENTS.md`: `check`, affected e2e journeys, OpenAPI sync/check, and production build.

## Output

Use this order:

1. Findings by severity.
1. Open questions or assumptions.
1. Validation performed and gaps.
1. Concise summary and residual risk.

For every finding, state the concrete defect, impact, evidence, and smallest viable correction. If
no findings remain, say so explicitly and identify any checks that were not run.
