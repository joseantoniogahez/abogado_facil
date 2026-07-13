# Matters Frontend Scaffold Checklist

- [x] Read `AGENTS.md`.
- [x] Read `frontend/docs/frontend_playbook.md`.
- [x] Confirm route, API, auth, state, UX, a11y, observability, performance, and validation impact.
- [x] Load matter route components from `frontend/src/app/routes.tsx`; lazy loading keeps route
  ownership centralized and produces a dedicated matter chunk.
- [x] Add protected list, create, detail, and edit routes under `/matters`.
- [x] Add user-facing text keys to `frontend/src/shared/i18n/ui-text.ts`.
- [x] Update `frontend/docs/operations/route_inventory.md`.
- [x] Update `frontend/docs/operations/api_consumer_matrix.md`.
- [x] Update `frontend/docs/operations/e2e_smoke_suite.md` with the CORE-002 coverage boundary.
- [x] Add contract/component tests and preserve route, architecture, accessibility, and e2e gates.
- [x] Run `npm --prefix frontend run check` (198 passed; coverage thresholds pass).
- [x] Run `npm --prefix frontend run test:e2e:ci` (12 passed).
- [x] Run `npm --prefix frontend run build` (build and approved performance budgets pass).

Completed for CORE-002 on 2026-07-12. A dedicated Playwright matter journey was reviewed and
deferred; API isolation and matter behavior are covered by backend tests and frontend contracts.
