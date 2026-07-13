# Frontend E2E Smoke Suite

This document defines the deterministic end-to-end smoke baseline for the frontend foundation.

## Scope

- Critical registration, email login, profile, and logout journey.
- Canonical dashboard navigation, legacy `/welcome` redirect, and protected route behavior.
- Protected client list, creation, detail, editing, search, and dashboard counter/action journey.
- Matter and embedded note journeys remain covered by route-inventory, architecture, API-contract, component, and
  accessibility gates. CORE-002 did not add a dedicated Playwright matter journey; its firm/client
  isolation and CRUD behavior are exercised by backend router, service, and repository tests.
- Error fallback behavior for protected session validation.
- Admin protected route error diagnostics for RBAC `403 forbidden` responses.
- Admin audit-log route visibility for sessions with `audit_logs:read`.

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
