# OPS-006 - CORS endurecido

## Tracking Status

- ID: `OPS-006`
- Type: `Backend`
- Priority: `P1`
- Plan status: `Ready`
- Implementation status: `Hecho`
- Last updated: `2026-07-19`
- Backlog source: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objective

Reducir la superficie de CORS mediante una política explícita y segura por entorno.

## Starting Point

`configure_cors` permite todos los métodos y headers cuando existen orígenes configurados, además
de credenciales.

## Scope

### Included

- Configurar métodos y headers permitidos explícitamente.
- Validar compatibilidad con frontend, preflight y credenciales.
- Documentar variables y política.

### Excluded

- Cambiar autenticación JWT.
- Resolver políticas del reverse proxy fuera del backend.

## Dependencies and Decisions

- Dependencies: `AUDIT-001`, frontend runtime config.
- Decisions closed: no usar comodines innecesarios en producción.
- Open questions: lista final de orígenes productivos debe definirse mediante despliegue.

## Acceptance Criteria

- [x] CORS productivo rechaza orígenes no permitidos.
- [x] Preflight y requests autorizados funcionan.
- [x] Tests cubren configuración segura y documentación actualizada.

## Affected Contracts and Files

| Surface | Expected files or contracts                | Change required |
| ------- | ------------------------------------------ | --------------- |
| Runtime | `backend/app/core/setup/cors.py`, settings | yes             |
| Tests   | CORS/factory tests                         | yes             |
| Docs    | runtime/browser security docs              | yes             |

## Work Plan

- [x] Inventariar consumidores y orígenes.
- [x] Implementar política explícita.
- [x] Añadir pruebas y actualizar contratos.

## Validation

- [ ] `python -m pytest backend/tests`
- [ ] `npm --prefix frontend run check` si cambia el contrato de runtime
- [ ] pre-commit sobre archivos modificados

## Progress Log

| Date       | State    | Completed                                                       | Pending / next safe action     |
| ---------- | -------- | --------------------------------------------------------------- | ------------------------------ |
| 2026-07-19 | Complete | Explicit policy, validation, preflight tests and docs delivered | No further implementation work |

## Validation Results

`.venv\Scripts\python.exe -m pytest backend/tests --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=100`: 383 passed, 100% coverage.
`git diff --check`: passed. `pre-commit` was not runnable because hooks could not be downloaded without network access.

## Pause / Handoff Record

- Current state: implementación completada.
- Pending work: none for implementation; pre-commit remains an environment validation limitation.
- Blockers or approvals: la lista final de orígenes productivos debe configurarse por despliegue.
- Residual risks: no se permiten orígenes con rutas; reverse proxy permanece fuera de alcance.
- Next safe action: validar backend y cerrar el ticket.

## Completion Summary

- Delivered: CORS explícito, validación segura de orígenes, credenciales y correlación `X-Request-ID`.
- Validation: suite focalizada aprobada; suite completa y pre-commit pendientes.
- Residual risk: lista productiva concreta aún depende del entorno de despliegue.
