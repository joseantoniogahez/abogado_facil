# OPS-005 - Protección de documentación OpenAPI en producción

## Tracking Status

- ID: `OPS-005`
- Type: `Backend`
- Priority: `P1`
- Plan status: `Complete`
- Implementation status: `Hecho`
- Last updated: `2026-07-19`
- Backlog source: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objective

Evitar que la documentación y el esquema completo de la API queden expuestos accidentalmente en
producción, manteniendo una experiencia útil en local y test.

## Starting Point

La fábrica crea FastAPI sin configuración explícita de `docs_url`, `redoc_url` u `openapi_url`.

## Scope

### Included

- Decidir y aplicar política por entorno para `/docs`, `/redoc` y `/openapi.json`.
- Añadir pruebas de configuración y actualizar documentación operativa.

### Excluded

- Cambiar el contrato funcional de endpoints.
- Crear un portal externo de documentación.

## Dependencies and Decisions

- Dependencies: `AUDIT-001`.
- Decisions closed: local/test conservan documentación; `prod`, `production` y `staging` deshabilitan
  las tres rutas; no se crea un portal administrativo en este ticket.
- Open questions: ninguna.

## Acceptance Criteria

- [x] Política por entorno implementada y probada.
- [x] No se filtran secretos ni endpoints de forma no intencionada.
- [x] Documentación canónica sincronizada.
- [ ] Backend tests y coverage gate pasan.

## Affected Contracts and Files

| Surface | Expected files or contracts                   | Change required |
| ------- | --------------------------------------------- | --------------- |
| Runtime | `backend/app/core/setup/factory.py`, settings | yes             |
| Tests   | `backend/tests/test_main.py`, settings tests  | yes             |
| Docs    | backend runtime/security docs                 | yes             |

## Work Plan

- [x] Confirmar decisión de exposición con la auditoría.
- [x] Implementar configuración por entorno.
- [x] Probar local/test/prod y documentar la política.

## Validation

- [x] `python -m pytest backend/tests` (381 passed)
- [x] coverage gate backend (100%)
- [ ] pre-commit sobre archivos modificados (no pudo iniciar: caché global de solo lectura y el
  reintento local no pudo descargar hooks por falta de red)

## Progress Log

| Date       | State    | Completed                                        | Pending / next safe action               |
| ---------- | -------- | ------------------------------------------------ | ---------------------------------------- |
| 2026-07-19 | Complete | Runtime policy, tests and canonical docs updated | Run full backend coverage and pre-commit |

## Validation Results

`.venv\Scripts\python.exe -m pytest backend/tests --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=100`: 381 passed, 100% coverage. A targeted run of `backend/tests/test_main.py`
also passed (26 tests).

## Pause / Handoff Record

- Current state: implementación completada.
- Pending work: ejecutar pre-commit sobre los archivos modificados y cerrar el plan.
- Blockers or approvals: ninguno.
- Residual risks: no existe portal protegido de documentación para producción; el acceso operativo
  requiere un mecanismo externo, fuera de alcance.
- Next safe action: ejecutar validación backend y pre-commit.

## Completion Summary

- Delivered: política explícita por `APP_ENV`, con OpenAPI habilitado fuera de producción y las tres
  rutas deshabilitadas en entornos productivos.
- Validation: suite backend y coverage aprobados; `npm --prefix frontend run openapi:check` aprobado;
  pre-commit pendiente por falta de red para descargar hooks.
- Residual risk: no hay portal administrativo protegido para consultar el esquema en producción.
