# CORE-006 - Checklists base por tipo de asunto

## Tracking Status

- ID: `CORE-006`
- Type: `Full-stack`
- Priority: `P1`
- Plan status: `Complete`
- Implementation status: `Hecho`
- Last updated: `2026-07-14`
- Backlog source: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objective

Permitir gestionar en cada asunto un checklist determinístico, aislado por despacho, con estados
pendiente, completo y no aplica, más elementos personalizados.

## Starting Point

El detalle de asunto ya integra notas y documentos, pero no existe persistencia, API ni UI de
checklists. El tipo de asunto es texto libre.

## Scope

### Included

- Inicializar sin duplicados elementos base para tipos soportados.
- Listar, cambiar estado y agregar elementos personalizados en el detalle del asunto.
- Probar y documentar el aislamiento por despacho y los contratos full-stack.

### Excluded

- Mensajes para cliente e IA/BYOK.
- Edición/eliminación de definiciones base y ordenamiento manual.

## Dependencies and Decisions

- Dependencies: `CORE-002`.
- Decisions closed: inicialización perezosa e idempotente; coincidencia normalizada del tipo; tipos
  no soportados empiezan vacíos y aceptan elementos personalizados.
- Open questions: none.

## Acceptance Criteria

- [x] Un asunto soportado muestra su checklist base sin duplicados.
- [x] Cada elemento admite `pending`, `complete` y `not_applicable`.
- [x] El usuario puede agregar elementos personalizados.
- [x] Todo acceso queda aislado por despacho y requiere sesión.
- [x] Required documentation is synchronized with delivered behavior.
- [x] Required validation gates pass and are recorded below.
- [x] Mandatory human approvals are recorded, or explicitly not applicable.

## Affected Contracts and Files

| Surface | Expected files or contracts                                 | Change required |
| ------- | ----------------------------------------------------------- | --------------- |
| Runtime | backend feature/migration/DI/router; frontend matter detail | yes             |
| Tests   | backend feature tests; frontend component/contracts         | yes             |
| Docs    | endpoint inventory, API consumer/mutation policy, backlog   | yes             |

## Work Plan

### Implementation

- [x] Add the matter-checklists vertical slice and migration.
- [x] Add API consumers and checklist UI to matter detail.

### Tests and Documentation

- [x] Add or update tests with the behavior change.
- [x] Review all documentation surfaces required by `AGENTS.md`.
- [x] Update canonical documents affected by the code diff.

### Validation

- [x] Backend tests and 100% coverage gate.
- [x] OpenAPI sync and frontend check/build.
- [x] Pre-commit on all files.

## Progress Log

| Date       | State       | Completed                                                      | Pending / next safe action                      |
| ---------- | ----------- | -------------------------------------------------------------- | ----------------------------------------------- |
| 2026-07-14 | En progreso | Scope and plan prepared                                        | Implement backend vertical slice and migration. |
| 2026-07-14 | Hecho       | Full-stack checklist, tests, docs, OpenAPI and gates completed | None.                                           |

## Validation Results

| Date       | Command                                                                                                                       | Result | Notes                                                           |
| ---------- | ----------------------------------------------------------------------------------------------------------------------------- | ------ | --------------------------------------------------------------- |
| 2026-07-14 | `.\.venv\Scripts\python.exe -m pytest backend/tests --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=100 -q` | Passed | 364 passed; 100% coverage; cache warning only.                  |
| 2026-07-14 | `npm --prefix frontend run openapi:sync`                                                                                      | Passed | Backend OpenAPI artifact regenerated.                           |
| 2026-07-14 | `npm --prefix frontend run check`                                                                                             | Passed | 50 files and 220 tests passed; OpenAPI/dependency gates passed. |
| 2026-07-14 | `npm --prefix frontend run build`                                                                                             | Passed | Production build and all performance budgets passed.            |
| 2026-07-14 | `.\.venv\Scripts\pre-commit.exe run --all-files`                                                                              | Passed | All hooks passed after automatic formatting pass.               |

## Pause / Handoff Record

- Current state: complete and validated.
- Changed files and contracts: checklist persistence/API, matter detail UI, OpenAPI, endpoint/access/consumer/mutation docs.
- Pending work: none for CORE-006.
- Blockers or approvals: none.
- Residual risks: exact normalized matching means a novel free-text synonym starts with an empty checklist but still supports custom items.
- Next safe action: none; proceed to the next backlog item.

## Completion Documentation Review

- [x] Root and service READMEs reviewed.
- [x] Backend operation and architecture docs reviewed.
- [x] Frontend operation docs and inventories reviewed.
- [x] Foundation status files reviewed and changed only if a foundation contract moved.
- [x] AI governance docs, templates, and checklists reviewed.
- [x] Item plan and summary backlog synchronized.

Record documents intentionally unchanged and why:

- Root/backend/frontend READMEs: no setup or service workflow changed.
- Foundation status files: no foundation rule or validation gate changed.
- Route inventory and e2e smoke docs: no route, auth, or error journey changed.

## Completion Summary

- Delivered: deterministic templates for seven initial matter types, status updates, custom items, firm isolation, and matter-detail UI.
- Validation: backend 364 tests/100% coverage; frontend check 220 tests; OpenAPI sync; build/performance; pre-commit.
- Skipped validation: e2e smoke was not required because routes, auth, and global error journeys did not change.
- Human approvals: not applicable.
- Residual risk: unsupported synonyms intentionally produce an empty customizable checklist.
