# Frontend Foundation Status

## Purpose

Capture the current frontend foundation state as a single source of truth focused on what exists now.
This document replaces backlog-style historical tracking for frontend foundation decisions.

## Current Foundation Snapshot

Status date: `2026-08-08`

- Foundation maturity: `ready for feature delivery with documented remediation gaps`.
- Architecture baseline enforced:
  - `app -> features -> shared` dependency direction.
  - Centralized route composition in `src/app/routes.tsx`.
- Runtime and quality contracts active:
  - API contract sync and drift prevention.
  - API consumer/error matrix.
  - Mutation/query policy contracts; non-idempotent retry remediation remains open.
  - Runtime config validation and fail-fast boot.
  - Browser security artifact checks; response-header enforcement remains open.
  - Observability and runtime error pipeline; request-path redaction remediation remains open.
  - Accessibility baseline gate with explicitly documented coverage limits.
  - Performance budget gate.
  - E2E smoke baseline with explicitly documented scenario gaps.

The current ABOGADO_FACIL JavaScript budget is `836000` raw bytes and `247000` gzip bytes. Its CSS
budget is `32100` raw bytes and `9000` gzip bytes. These product-specific values remain enforced;
their approval history belongs to the linked product plans in
`docs/operations/performance_budget.md`.

## Known Remediation Gaps

- `docs/operations/browser_security_baseline.md`: CSP delivered through `meta` cannot enforce
  `frame-ancestors`, and the repository does not configure the required CSP or Permissions Policy
  response headers.
- `docs/operations/observability_events.md`: API diagnostics can include user-entered query values
  in logged request paths.
- `docs/operations/mutation_policy.md`: default retry currently reaches non-idempotent writes such
  as payment creation without proven end-to-end idempotency.
- `docs/operations/api_consumer_matrix.md`: AI insights, AI feedback, and matter calculation
  consumers contain known runtime response-validation gaps.
- `docs/operations/e2e_smoke_suite.md` and `docs/operations/accessibility_gate.md`: the exact current
  coverage and omitted scenarios are recorded and must not be overdeclared.

These are current-state disclosures, not accepted exceptions to the intended contracts. Close each
gap in implementation/configuration and tests before removing it from this snapshot.

## Active Guardrails

- Canonical engineering rules: `docs/frontend_playbook.md`.
- Canonical runtime contracts: `docs/operations/*.md`.
- Request workflows for AI execution: `docs/templates/*.md`.
- Documentation contracts: `src/contracts/docs.contract.test.ts`.
- Performance documentation thresholds are contract-checked against
  `performance/bundle_budget.json`.

## Required Validation Gates

Run these from `frontend/` before delivery:

- `npm run check`
- `npm run test:e2e:ci` (required when auth/routing/error journeys are affected)
- `npm run build`

## Change Management Rules

1. Keep this file current when foundation rules/contracts/gates change.
1. Update affected operation docs in the same PR as behavior changes.
1. Keep templates aligned with AI request expectations and reviewer needs.
1. Do not add backlog/history tracking documents for foundation unless explicitly requested.
