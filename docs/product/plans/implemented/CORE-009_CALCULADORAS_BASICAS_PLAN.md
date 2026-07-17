# CORE-009 - Calculadoras básicas sin IA

## Tracking Status

- ID: `CORE-009`
- Type: `Full-stack`
- Priority: `P1`
- Plan status: `Complete`
- Implementation status: `Hecho`
- Last updated: `2026-07-16`
- Backlog source: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objective

Permitir cálculos jurídicos-administrativos determinísticos sin configurar IA, copiar un resumen
legible y guardar resultados asociados a un asunto con una advertencia de estimación.

## Starting Point

Los asuntos ya están aislados por despacho y su detalle integra notas, checklist, tareas, pagos y
documentos. No existe motor de cálculo, persistencia de resultados ni interfaz de calculadoras.

## Scope

### Included

- Calcular adeudo restante a partir de principal y abonos acumulados.
- Calcular rentas vencidas a partir de renta mensual, meses vencidos y pagos acumulados.
- Calcular interés simple a partir de principal, tasa anual y plazo en días.
- Mostrar importes MXN con dos decimales, resumen copiable y advertencia de estimación.
- Guardar y listar instantáneas inmutables de resultados en un asunto del despacho actual.

### Excluded

- Liquidación/finiquito laboral sin una especificación normativa y jurídica aprobada.
- Sustituir el control de honorarios y pagos parciales entregado en CORE-008.
- IA, actualización monetaria, interés compuesto, impuestos, calendarios o fuentes normativas.
- Editar o eliminar resultados guardados, exportar archivos o compartirlos externamente.

## Dependencies and Decisions

- Dependencies: `CORE-002`; CORE-008 evita duplicar el control de honorarios.
- Decisions closed: cálculo backend con `Decimal`; moneda fija `MXN`; día comercial de 365 días;
  resultados guardados como instantáneas con entradas, salida, resumen y advertencia.
- Open questions: none.

## Acceptance Criteria

- [x] El usuario ejecuta las tres calculadoras sin credenciales ni configuración de IA.
- [x] Cada resultado muestra entradas, importe MXN, resumen y advertencia de estimación.
- [x] El resumen se puede copiar desde una acción accesible.
- [x] El resultado puede guardarse y listarse en un asunto propio.
- [x] Recursos ajenos o inexistentes producen el mismo `404`.
- [x] Required documentation is synchronized with delivered behavior.
- [x] Required validation gates pass and are recorded below.
- [x] Mandatory human approvals are recorded, or explicitly not applicable.

## Affected Contracts and Files

| Surface | Expected files or contracts                                    | Change required |
| ------- | -------------------------------------------------------------- | --------------- |
| Runtime | backend slice/migration/DI/router; embedded matter-detail UI   | yes             |
| Tests   | backend feature tests; frontend component/contracts            | yes             |
| Docs    | endpoints, API consumers, mutation policy and tracking/OpenAPI | yes             |

## Work Plan

### Implementation

- [x] Add calculation and saved-result contracts, vertical slice, migration, DI and router.
- [x] Add the accessible calculator, copy action and saved-history UI to matter detail.
- [x] Synchronize OpenAPI and canonical contract inventories.

### Tests and Documentation

- [x] Add or update tests with the behavior change.
- [x] Review all documentation surfaces required by `AGENTS.md`.
- [x] Update canonical documents affected by the code diff.

### Validation

- [x] Backend tests and 100% coverage gate.
- [x] OpenAPI sync and frontend check/build.
- [x] Pre-commit on all files.

## Progress Log

| Date       | State       | Completed                                                  | Pending / next safe action |
| ---------- | ----------- | ---------------------------------------------------------- | -------------------------- |
| 2026-07-16 | En progreso | Scope, exclusions, decisions and scaffold preview recorded | Implement backend slice.   |
| 2026-07-16 | Hecho       | Runtime, tests, contracts, docs and gates passed           | None.                      |

## Validation Results

| Date       | Command                           | Result | Notes                                            |
| ---------- | --------------------------------- | ------ | ------------------------------------------------ |
| 2026-07-16 | Backend coverage gate             | Passed | 375 passed; 100% coverage.                       |
| 2026-07-16 | `npm --prefix frontend run check` | Passed | 232 tests; OpenAPI and dependency audit passed.  |
| 2026-07-16 | `npm --prefix frontend run build` | Passed | Production build and performance budgets passed. |
| 2026-07-16 | `pre-commit run --all-files`      | Passed | All hooks passed.                                |

## Pause / Handoff Record

- Current state: complete and validated.
- Changed files and contracts: calculation persistence/API, OpenAPI, read-access catalog, matter-detail UI and canonical inventories.
- Pending work: none for CORE-009.
- Blockers or approvals: none.
- Residual risks: formulas must remain clearly labeled as estimates and avoid implying legal advice.
- Next safe action: proceed to the next backlog item.

## Completion Documentation Review

- [x] Root and service READMEs reviewed.
- [x] Backend operation and architecture docs reviewed.
- [x] Frontend operation docs and inventories reviewed.
- [x] Foundation status files reviewed and changed only if a foundation contract moved.
- [x] AI governance docs, templates, and checklists reviewed.
- [x] Item plan and summary backlog synchronized.

Record documents intentionally unchanged and why:

- Root/service READMEs, route inventory, error mapping and foundation status: no setup, route, normalized error or foundation rule changed.

## Completion Summary

- Delivered: deterministic debt, overdue-rent and simple-interest estimates with copy and immutable matter history.
- Validation: backend 375 tests/100%; frontend check 232 tests; OpenAPI; build budgets; all pre-commit hooks.
- Skipped validation: e2e smoke was not required because routes, auth and global error journeys did not change.
- Human approvals: not applicable.
- Residual risk: labor settlement remains excluded until a legally reviewed formula is specified.
