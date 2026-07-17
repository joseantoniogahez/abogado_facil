# CORE-008 - Control básico de pagos

## Tracking Status

- ID: `CORE-008`
- Type: `Full-stack`
- Priority: `P1`
- Plan status: `Complete`
- Implementation status: `Hecho`
- Last updated: `2026-07-16`
- Backlog source: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objective

Permitir que un despacho controle los honorarios pactados de cada asunto, registre anticipos y
pagos parciales, consulte el total pagado y el saldo pendiente, y conserve notas financieras.

## Starting Point

Los asuntos ya tienen detalle aislado por despacho y componentes embebidos para notas, tareas,
checklist y documentos. No existe persistencia, API ni interfaz para información financiera.

## Scope

### Included

- Configurar honorarios pactados y notas financieras por asunto.
- Registrar abonos positivos clasificados como `advance` o `partial`.
- Mostrar total pagado y saldo calculados por el backend.
- Listar los abonos cronológicamente en el detalle del asunto.
- Mantener aislamiento estricto por despacho y contrato monetario decimal de dos posiciones.

### Excluded

- Pagos en línea, facturación, impuestos, comisiones, reembolsos y eliminación de abonos.
- Monedas múltiples, tipos de cambio, planes de pago, vencimientos y notificaciones.
- Reportes financieros globales o exportación contable.

## Dependencies and Decisions

- Dependencies: `CORE-002`.
- Decisions closed: moneda MVP fija `MXN`; honorarios iniciales en cero; saldo igual a honorarios
  menos abonos y puede ser negativo para visibilizar pagos excedentes; abonos son inmutables.
- Open questions: none.

## Acceptance Criteria

- [x] Un usuario configura honorarios y notas para un asunto propio.
- [x] Registra anticipos y pagos parciales con monto, fecha y nota opcional.
- [x] La API calcula total pagado y saldo con precisión decimal.
- [x] El detalle del asunto muestra el resumen y el historial de abonos.
- [x] Recursos ajenos o inexistentes producen el mismo `404`.
- [x] Required documentation is synchronized with delivered behavior.
- [x] Required validation gates pass and are recorded below.
- [x] Mandatory human approvals are recorded, or explicitly not applicable.

## Affected Contracts and Files

| Surface | Expected files or contracts                            | Change required |
| ------- | ------------------------------------------------------ | --------------- |
| Runtime | backend slice/migration/DI/router; matter detail UI    | yes             |
| Tests   | backend feature tests; frontend component/contracts    | yes             |
| Docs    | endpoints, API consumers, mutation policy and tracking | yes             |

## Work Plan

### Implementation

- [x] Add the matter-payments vertical slice, migration, DI and router registration.
- [x] Add frontend consumer and accessible payment summary/history UI.
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

| Date       | State       | Completed                                        | Pending / next safe action             |
| ---------- | ----------- | ------------------------------------------------ | -------------------------------------- |
| 2026-07-16 | En progreso | Scope, decisions and scaffold preview completed  | Implement backend slice and migration. |
| 2026-07-16 | Hecho       | Runtime, tests, contracts, docs and gates passed | None.                                  |

## Validation Results

| Date       | Command                                                                                                                       | Result | Notes                                                      |
| ---------- | ----------------------------------------------------------------------------------------------------------------------------- | ------ | ---------------------------------------------------------- |
| 2026-07-16 | `.\.venv\Scripts\python.exe -m pytest backend/tests --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=100 -q` | Passed | 373 passed; 100% coverage.                                 |
| 2026-07-16 | `npm --prefix frontend run openapi:sync`                                                                                      | Passed | OpenAPI artifact regenerated.                              |
| 2026-07-16 | `npm --prefix frontend run check`                                                                                             | Passed | 53 files, 230 tests, coverage and contract gates passed.   |
| 2026-07-16 | `npm --prefix frontend run build`                                                                                             | Passed | Production build and all performance budgets passed.       |
| 2026-07-16 | `.\.venv\Scripts\pre-commit.exe run --all-files`                                                                              | Passed | All hooks passed after automatic formatting was reapplied. |

## Pause / Handoff Record

- Current state: complete and validated.
- Changed files and contracts: payment persistence/API, matter detail UI, OpenAPI, endpoint/access
  policy, API consumer and mutation policy documentation.
- Pending work: none for CORE-008.
- Blockers or approvals: none.
- Residual risks: immutable abonos require a future correction workflow if business rules later
  demand reversals.
- Next safe action: proceed to the next backlog item.

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
- Route inventory and e2e smoke docs: no route, auth or global error journey changed.
- Error mapping: existing normalized `400`, `401`, `404` and `500` contracts are reused.

## Completion Summary

- Delivered: firm-scoped MXN honorarios, financial notes, immutable advance/partial payment history,
  backend-calculated totals and balance, and accessible matter-detail controls.
- Validation: backend 373 tests/100% coverage; frontend check 230 tests; OpenAPI sync; production
  build and performance budgets; all pre-commit hooks.
- Skipped validation: e2e smoke was not required because routes, auth and global error journeys did
  not change.
- Human approvals: not applicable.
- Residual risk: payment reversals and corrections are intentionally outside this MVP slice.
