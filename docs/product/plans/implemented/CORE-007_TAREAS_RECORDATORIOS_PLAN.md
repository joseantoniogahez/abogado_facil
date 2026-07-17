# CORE-007 - Tareas y recordatorios simples

## Tracking Status

- ID: `CORE-007`
- Type: `Full-stack`
- Priority: `P1`
- Plan status: `Complete`
- Implementation status: `Hecho`
- Last updated: `2026-07-16`
- Backlog source: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objective

Permitir registrar tareas con fecha límite dentro de un asunto, editarlas y marcarlas como
completadas, manteniendo aislamiento por despacho y mostrando los pendientes próximos en dashboard.

## Starting Point

El detalle del asunto ya integra notas, checklist y documentos. El dashboard contiene placeholders
para tareas pendientes y próximos vencimientos, pero no existe persistencia ni API de tareas.

## Scope

### Included

- Crear, listar y editar tareas asociadas a un asunto.
- Registrar título obligatorio, fecha límite y estado completado.
- Ordenar pendientes antes de completadas y por fecha límite.
- Mostrar contador y próximos pendientes en dashboard.
- Integrar UI accesible en el detalle del asunto.

### Excluded

- Notificaciones por correo, calendario, push o WhatsApp.
- Recurrencia, asignación multiusuario, prioridades y tareas sin asunto.
- Eliminación, historial y recordatorios automáticos.

## Dependencies and Decisions

- Dependencies: `CORE-002`.
- Decisions closed: fecha límite obligatoria como fecha local; estado booleano; edición parcial;
  dashboard muestra hasta cinco pendientes próximos.
- Open questions: none.

## Acceptance Criteria

- [x] Un usuario crea una tarea con título y fecha límite dentro de un asunto propio.
- [x] Puede editar título/fecha y marcar o desmarcar la tarea como completada.
- [x] El listado es determinista y distingue pendientes, vencidas y completadas.
- [x] Dashboard muestra contador y hasta cinco pendientes próximos del despacho.
- [x] Recursos ajenos o inexistentes producen el mismo `404`.
- [x] Required documentation is synchronized with delivered behavior.
- [x] Required validation gates pass and are recorded below.
- [x] Mandatory human approvals are recorded, or explicitly not applicable.

## Affected Contracts and Files

| Surface | Expected files or contracts                                      | Change required |
| ------- | ---------------------------------------------------------------- | --------------- |
| Runtime | backend slice/migration/DI/router/dashboard; matter UI/dashboard | yes             |
| Tests   | backend feature/dashboard; frontend task/dashboard contracts     | yes             |
| Docs    | endpoints, access, consumers, mutation policy, tracking          | yes             |

## Work Plan

### Implementation

- [x] Add the matter-tasks vertical slice, migration, DI and router registration.
- [x] Extend dashboard metrics and upcoming items from task persistence.
- [x] Add frontend consumer, task UI and dashboard rendering.

### Tests and Documentation

- [x] Add or update tests with the behavior change.
- [x] Review all documentation surfaces required by `AGENTS.md`.
- [x] Update canonical documents affected by the code diff.

### Validation

- [x] Backend tests and 100% coverage gate.
- [x] OpenAPI sync and frontend check/build.
- [x] Pre-commit on all files.

## Progress Log

| Date       | State       | Completed                                                    | Pending / next safe action             |
| ---------- | ----------- | ------------------------------------------------------------ | -------------------------------------- |
| 2026-07-16 | En progreso | Scope, decisions and scaffold preview completed              | Implement backend slice and migration. |
| 2026-07-16 | Hecho       | Runtime, tests, contracts, docs and required gates completed | None.                                  |

## Validation Results

| Date       | Command                                                                                                                       | Result | Notes                                                                                       |
| ---------- | ----------------------------------------------------------------------------------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------- |
| 2026-07-16 | `.\.venv\Scripts\python.exe -m pytest backend/tests --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=100 -q` | Passed | 369 passed; 100% coverage; cache warning only.                                              |
| 2026-07-16 | `npm --prefix frontend run openapi:sync`                                                                                      | Passed | OpenAPI artifact regenerated.                                                               |
| 2026-07-16 | `npm --prefix frontend run check`                                                                                             | Passed | 52 files and 228 tests; coverage, OpenAPI and dependency audit passed.                      |
| 2026-07-16 | `npm --prefix frontend run build`                                                                                             | Passed | Production build and performance budgets passed.                                            |
| 2026-07-16 | `SKIP=hadolint-docker pre-commit run --all-files`                                                                             | Passed | All available hooks passed; hadolint skipped because Docker Desktop daemon was unavailable. |

## Pause / Handoff Record

- Current state: complete and validated.
- Changed files and contracts: task persistence/API, dashboard summary, matter detail UI, OpenAPI,
  endpoint/access/consumer/mutation docs and tracking.
- Pending work: none for CORE-007.
- Blockers or approvals: none.
- Residual risks: date-only deadlines intentionally do not encode a notification time.
- Next safe action: proceed to the next backlog item.

## Completion Documentation Review

- [x] Root and service READMEs reviewed.
- [x] Backend operation and architecture docs reviewed.
- [x] Frontend operation docs and inventories reviewed.
- [x] Foundation status files reviewed and changed only if a foundation contract moved.
- [x] AI governance docs, templates, and checklists reviewed.
- [x] Item plan and summary backlog synchronized.

Documents intentionally unchanged:

- Root/backend/frontend READMEs: no setup or service workflow changed.
- Foundation status files: no foundation rule or validation gate changed.
- Route inventory and e2e smoke docs: no route, auth or global error journey changed.
- Error mapping: existing normalized `400`, `401`, `404` and `500` contracts are reused.

## Completion Summary

- Delivered: firm-scoped matter tasks with due dates, editing, completion state, dashboard count and
  upcoming task links.
- Validation: backend 369 tests/100% coverage; frontend check 228 tests; OpenAPI sync; build and
  performance budgets; pre-commit except the daemon-dependent hadolint hook.
- Skipped validation: e2e smoke was not required because routes, auth and global error journeys did
  not change; `hadolint-docker` could not run because Docker Desktop was not active.
- Human approvals: not applicable.
- Residual risk: date-only reminders do not send notifications or encode a time of day, by design.
