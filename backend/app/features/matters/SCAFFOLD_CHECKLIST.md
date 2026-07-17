# Matters Backend Scaffold Checklist

- [x] Read `AGENTS.md`.
- [x] Read `backend/docs/backend_playbook.md`.
- [x] Confirm API, data, auth, RBAC, errors, observability, and validation impact.
- [x] Register router module in `backend/app/core/setup/routers.py`.
- [x] Add repository and service providers in `backend/app/core/setup/dependencies.py`.
- [x] Protect endpoints with the authenticated read-access dependency.
- [x] Replace placeholder OpenAPI metadata in `openapi.py`.
- [x] Update `backend/docs/operations/api_endpoints.md`.
- [x] Review `backend/docs/operations/authorization_matrix.md`; authenticated read routes were
  added and no new configurable permission was required.
- [x] Review `backend/docs/operations/error_mapping.md`; existing `NotFoundError` and validation
  mappings cover matters without changing the error contract.
- [x] Add Alembic migration for the `matters` model and constraints.
- [x] Run `python -m pytest backend/tests` (328 passed).
- [x] Run the backend coverage gate (328 passed, 100.00%).

Completed for CORE-002 on 2026-07-12. Detailed evidence is recorded in
`docs/product/plans/implemented/CORE-002_GESTION_ASUNTOS_PLAN.md`.
