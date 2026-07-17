# Clients Backend Scaffold Checklist

- [x] Read `AGENTS.md`.
- [x] Read `backend/docs/backend_playbook.md`.
- [x] Confirm API, data, auth, RBAC, errors, observability, and validation impact.
- [x] Register router module in `backend/app/core/setup/routers.py`.
- [x] Add dependency providers in `backend/app/core/setup/dependencies.py`.
- [x] Add authorization dependencies for protected endpoints.
- [x] Replace placeholder OpenAPI metadata in `openapi.py`.
- [x] Update `backend/docs/operations/api_endpoints.md`.
- [x] Update `backend/docs/operations/authorization_matrix.md`.
- [x] Update `backend/docs/operations/error_mapping.md`.
- [x] Add Alembic migration for the client model and constraints.
- [x] Run `python -m pytest backend/tests`.
- [x] Run the backend 100% coverage gate.

Completed for CORE-001 on 2026-07-12. Detailed evidence is recorded in
`docs/product/plans/implemented/CORE-001_GESTION_CLIENTES_PLAN.md`.
