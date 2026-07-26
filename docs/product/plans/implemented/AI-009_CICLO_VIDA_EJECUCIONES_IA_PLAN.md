# AI-009 - Ciclo de vida de ejecuciones de IA

## Tracking Status

- ID: `AI-009`
- Type: Backend
- Priority: P0-IA
- Plan status: Complete
- Implementation status: Hecho
- Last updated: 2026-07-25
- Backlog source: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objective

Proveer una capacidad backend persistente y aislada por despacho para registrar cada ejecución de IA
desde su creación hasta su éxito o fallo, con intentos, versiones y correlación suficientes para
auditoría y observabilidad sin almacenar prompts, credenciales ni detalles inseguros de proveedor.

## Starting Point

El backend ya dispone de proveedores normalizados, validación BYOK, Unit of Work, correlación de
streaming y logging seguro. No existe aún un registro persistente que conecte una ejecución con su
despacho, usuario, función, proveedor, versiones, estado, resultado o error.

## Scope

### Included

- Modelo y migración `AIJob` aislados por `firm_id` y `user_id`.
- Estados `queued`, `running`, `succeeded`, `failed` y `cancelled`.
- Transiciones válidas, conteo de intentos y timestamps de inicio/finalización.
- Versiones explícitas de prompt y schema.
- Resultado JSON estructurado o código de error seguro, nunca ambos.
- Correlación mediante `request_id` y `execution_id`.
- Repositorio, servicio interno, DI, pruebas y documentación de arquitectura.

### Excluded

- Endpoint público o interfaz frontend.
- Ejecución de proveedores y persistencia de prompts o contexto.
- Reintentos, backoff y prevención de duplicados (`AI-010`).
- Taxonomía completa de proveedores (`AI-011`).
- Métricas agregadas y dashboard (`AI-006`, `OBS-001`, `OBS-002`).

## Dependencies and Decisions

- Dependencies: `AI-003`, `AI-004`, `AI-005` y `SEC-001A`, ya completados.
- Decisions closed: capacidad interna sin router; IDs de ejecución opacos; errores persistidos sólo
  como códigos seguros; cada lectura y mutación exige `user_id` y `firm_id`.
- Open questions: ninguna que bloquee la implementación.

## Acceptance Criteria

- [x] `AIJob` conserva estado, intentos, versiones, resultado/error y correlación.
- [x] El repositorio aplica aislamiento por despacho y usuario en lecturas y transiciones.
- [x] El servicio rechaza transiciones inválidas y usa Unit of Work para cada escritura.
- [x] No se persisten prompts, API keys, texto documental ni mensajes de error de proveedor.
- [x] Migración, metadata de Alembic y DI están sincronizadas.
- [x] Pruebas cubren ciclo exitoso, fallo, cancelación, aislamiento y transiciones inválidas.
- [x] Required documentation is synchronized with delivered behavior.
- [x] Required validation gates pass and are recorded below.
- [x] Mandatory human approvals are recorded, or explicitly not applicable.

## Affected Contracts and Files

| Surface | Expected files or contracts                                 | Change required |
| ------- | ----------------------------------------------------------- | --------------- |
| Runtime | `app/features/ai_jobs/*`, DI, Alembic metadata/migration    | yes             |
| Tests   | `backend/tests/features/ai_jobs/*`, documentation contracts | yes             |
| Docs    | clean architecture, DI, UoW, AI streaming/observability     | yes             |

## Work Plan

### Implementation

- [x] Crear modelo, schemas, repositorio y servicio de ciclo de vida.
- [x] Añadir migración y registrar el modelo en Alembic.
- [x] Añadir proveedores tipados de repositorio y servicio.

### Tests and Documentation

- [x] Add or update tests with the behavior change.
- [x] Review all documentation surfaces required by `AGENTS.md`.
- [x] Update canonical documents affected by the code diff.

### Validation

- [x] `python -m pytest backend/tests/features/ai_jobs backend/tests/docs`
- [x] `python -m pytest backend/tests`
- [x] `python -m pytest backend/tests --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=100`
- [x] Pre-commit on changed files.

## Progress Log

| Date       | State       | Completed                                                                                | Pending / next safe action                            |
| ---------- | ----------- | ---------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| 2026-07-25 | En progreso | Alcance, exclusiones, contratos y validaciones definidos                                 | Implementar el slice interno `ai_jobs` y su migración |
| 2026-07-25 | Hecho       | Modelo, migración, servicio transaccional, aislamiento, pruebas y contratos documentados | Sin trabajo pendiente en AI-009                       |

## Validation Results

| Date       | Command                                                                                                | Result | Notes                                                                       |
| ---------- | ------------------------------------------------------------------------------------------------------ | ------ | --------------------------------------------------------------------------- |
| 2026-07-25 | `python scripts/scaffold_feature.py --dry-run backend ai-jobs`                                         | Passed | Rutas previstas revisadas; no se crea router porque la capacidad es interna |
| 2026-07-25 | `python -m pytest backend/tests/features/ai_jobs backend/tests/docs -q`                                | Passed | 15 pruebas focalizadas                                                      |
| 2026-07-25 | `python -m pytest backend/tests`                                                                       | Failed | 448 pasaron; `__all__` infringía el guardrail de `__init__.py`; corregido   |
| 2026-07-25 | `python -m pytest backend/tests --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=100` | Failed | 449 pruebas pasaron; cobertura inicial 99.91%; se añadieron pruebas         |
| 2026-07-25 | `python -m pytest backend/tests --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=100` | Passed | 451 pruebas, cobertura 100%                                                 |
| 2026-07-25 | `python -m alembic -c alembic.ini heads` desde `backend/`                                              | Passed | `ai_jobs_20260725 (head)`                                                   |
| 2026-07-25 | `pre-commit run --all-files`                                                                           | Passed | Todos los hooks pasan tras el ajuste automático de Markdown                 |

## Pause / Handoff Record

- Current state: capacidad interna `ai_jobs` implementada y validada.
- Changed files and contracts: modelo/migración, schemas, repositorio, servicio, DI, pruebas y
  contratos backend de arquitectura, UoW, lifecycle, streaming y observabilidad.
- Pending work: ninguno dentro de AI-009.
- Blockers or approvals: ninguno.
- Residual risks: las funciones IA futuras deberán integrar explícitamente este servicio; retries y
  taxonomía completa permanecen en AI-010/AI-011.
- Next safe action: continuar con AI-010 usando `AIJobsService` como lifecycle persistente.

## Completion Documentation Review

- [x] Root and service READMEs reviewed.
- [x] Backend operation and architecture docs reviewed.
- [x] Frontend operation docs and inventories reviewed.
- [x] Foundation status files reviewed and changed only if a foundation contract moved.
- [x] AI governance docs, templates, and checklists reviewed.
- [x] Item plan and summary backlog synchronized.

Record documents intentionally unchanged and why:

- Root `README.md` y `backend/README.md`: sin cambio; no cambian setup ni operación del usuario.
- API, autenticación, autorización y errores: sin cambio; no existe router público.
- Docs frontend: sin cambio; no existe consumidor ni contrato OpenAPI nuevo.
- Foundation status: sin cambio; se añadió una capacidad, no una regla o gate de fundación.

## Completion Summary

- Delivered: lifecycle persistente y tenant-scoped de `AIJob`, con transiciones serializadas,
  intentos, versiones, correlación y resultado/error mutuamente excluyentes.
- Validation: 451 pruebas backend y 100% cobertura; Alembic reconoce una cabeza; pre-commit completo.
- Skipped validation: migración contra PostgreSQL real no ejecutada; la revisión estática de Alembic
  y la suite no requieren servicio externo.
- Human approvals: not applicable.
- Residual risk: integración desde una función IA real, retries y taxonomía pertenecen a tickets
  posteriores.
