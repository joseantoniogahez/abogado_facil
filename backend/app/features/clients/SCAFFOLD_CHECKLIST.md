# Clients Backend Scaffold Checklist

- [ ] Read `AGENTS.md`.
- [ ] Read `backend/docs/backend_playbook.md`.
- [ ] Confirm API, data, auth, RBAC, errors, observability, and validation impact.
- [ ] Register router module in `backend/app/core/setup/routers.py` when endpoints are added.
- [ ] Add dependency providers in `backend/app/core/setup/dependencies.py` when needed.
- [ ] Add authorization dependencies when endpoints are protected.
- [ ] Replace placeholder OpenAPI metadata in `openapi.py`.
- [ ] Update `backend/docs/operations/api_endpoints.md` when endpoint behavior changes.
- [ ] Update `backend/docs/operations/authorization_matrix.md` when permissions change.
- [ ] Update `backend/docs/operations/error_mapping.md` when domain errors change.
- [ ] Add Alembic migration if models or constraints change.
- [ ] Run `python -m pytest backend/tests`.
- [ ] Run `python -m pytest backend/tests --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=100`.
