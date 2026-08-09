# Frontend E2E Smoke Suite

This document defines the deterministic end-to-end smoke baseline for the frontend foundation.

## Scope

- Registration, email login, and profile journeys.
- Canonical dashboard navigation, legacy `/welcome` redirect, and protected route behavior.
- Protected `/settings/ai` BYOK status, save, and delete journey with authenticated API requests.
- Protected client creation, detail, editing, list, and search journey.
- Matter detail smoke covers embedded note CRUD and document upload, list, authenticated download,
  and confirmed deletion with strict API mocks. The same scenario covers the initial-narrative AI
  preview, execution, human review, and conversion into a matter note.
- Error fallback behavior for protected session validation.
- Admin protected route error diagnostics for RBAC `403 forbidden` responses.
- Admin audit-log route visibility for sessions with `audit_logs:read`.
- Admin assignments and permissions diagnostics plus direct-navigation redirects for missing
  permissions.

## Coverage Gaps

- The Playwright suite does not currently exercise logout. Logout behavior is covered by
  `src/shared/routing/RootLayout.test.tsx`, not by this e2e baseline.
- The client e2e scenario does not verify a post-mutation dashboard counter or dashboard action.
- `/ai/insights` and `/document-templates` do not currently have dedicated Playwright scenarios.

These gaps must not be described as delivered e2e coverage. Add or update Playwright scenarios when
one of these journeys becomes a release requirement.

## Runner Contract

- Runner: Playwright (`@playwright/test`).
- Config: `playwright.config.ts`.
- Browser baseline: Chromium only for foundation smoke determinism.
- Test files: `e2e/foundation-smoke.spec.ts`.

## Deterministic Setup

- Frontend app server is started by Playwright via `webServer` in `playwright.config.ts`.
- API calls are mocked per test with strict route handlers for `**/v1/**`.
- Unhandled API requests fail tests immediately to expose drift or accidental network dependency.
- Authenticated-user fixtures include email, first/middle/last name, display name, firm name,
  disabled status, and permissions; legacy username-only fixtures are not valid.
- The registration scenario verifies required legal-name inputs, editable display name, normalized
  email feedback, and an explicit transition to login without implicit authentication.
- The profile scenario verifies that the returned product profile replaces cached session state;
  dashboard headings use `display_name`; dashboard API mocks are firm-scoped and deterministic.

## Execution Commands

- Local smoke run: `npm --prefix frontend run test:e2e`
- CI-equivalent smoke run: `npm --prefix frontend run test:e2e:ci`
- Browser install (required once per environment): `npm --prefix frontend run e2e:install`

## Failure Artifacts

- Trace on failure: `test-results/**/trace.zip`
- Screenshot on failure: `test-results/**`
- CI output uses line reporter for fast triage.

## Ownership

- Any auth/routing/error behavior changes must update smoke tests when expected behavior changes.
- Any API-path contract change affecting smoke scenarios must update route mocks and this document.
