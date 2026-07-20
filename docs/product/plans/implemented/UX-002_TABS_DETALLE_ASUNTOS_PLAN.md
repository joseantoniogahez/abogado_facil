# UX-002 - Tabs para el detalle de asuntos

## Tracking Status

- ID: `UX-002`
- Type: `Frontend`
- Priority: `P1`
- Plan status: `Complete`
- Implementation status: `Hecho`
- Last updated: `2026-07-18`
- Backlog source: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objective

Reducir el scroll y el tiempo para encontrar una funcionalidad dentro del detalle de un asunto,
manteniendo visibles los datos operativos más importantes.

## Starting Point

El detalle actual renderiza en una sola columna las notas, tareas, pagos, cálculos, checklist y
documentos. La funcionalidad existe, pero la navegación se vuelve costosa cuando el asunto contiene
más información.

## Scope

### Included

- Mantener una cabecera/resumen visible con cliente, tipo, estado, próxima acción y acciones principales.
- Agrupar el contenido en tabs: `Resumen`, `Seguimiento`, `Finanzas` y `Documentos y notas`.
- Mantener navegación accesible por teclado y estados activos claramente identificables.
- Persistir la tab activa en la URL mediante un parámetro como `tab`.
- Adaptar la navegación para pantallas pequeñas.

### Excluded

- Cambios en la API, modelo de datos o permisos.
- Cambios en el comportamiento interno de notas, tareas, pagos, cálculos, checklist o documentos.
- Crear un tab separado para cada módulo.

## Dependencies and Decisions

- Dependencies: módulos existentes del detalle de asuntos y contratos frontend de routing/accesibilidad.
- Decisions closed: usar cuatro grupos funcionales y conservar un resumen operativo visible.
- Open questions: ninguna que impida iniciar la implementación.

## Acceptance Criteria

- [ ] El detalle ya no muestra todos los módulos uno debajo de otro por defecto.
- [ ] El resumen inicial muestra la información operativa principal y las acciones de asunto.
- [ ] Seguimiento contiene tareas y checklist.
- [ ] Finanzas contiene pagos y cálculos.
- [ ] Documentos y notas contiene ambos módulos.
- [ ] La tab activa se conserva al recargar mediante la URL y se valida un valor inválido con un fallback seguro.
- [ ] La navegación es usable con teclado y funciona en viewport móvil.
- [ ] Required documentation is synchronized with delivered behavior.
- [ ] Required validation gates pass and are recorded below.
- [ ] Mandatory human approvals are recorded, or explicitly not applicable.

## Affected Contracts and Files

| Surface | Expected files or contracts                                                              | Change required |
| ------- | ---------------------------------------------------------------------------------------- | --------------- |
| Runtime | `frontend/src/features/matters/MattersPage.tsx`, routing/query-param behavior            | yes             |
| Tests   | Matter detail tests and accessibility baseline                                           | yes             |
| Docs    | `frontend/docs/operations/route_inventory.md` only if route behavior is documented there | review          |

## Work Plan

### Implementation

- [x] Crear el componente o patrón de tabs dentro del feature de asuntos.
- [x] Separar los módulos actuales en los cuatro grupos definidos.
- [x] Persistir y validar la tab activa con `useSearchParams`.
- [x] Ajustar estilos responsive y estados de foco/selección.

### Tests and Documentation

- [x] Add or update tests with the behavior change.
- [x] Review all documentation surfaces required by `AGENTS.md`.
- [x] Update canonical documents affected by the code diff.

### Validation

- [x] `npm --prefix frontend run check`
- [x] `npm --prefix frontend run build`
- [x] `pre-commit run --files <changed-files>`

## Progress Log

| Date       | State       | Completed                                                                                               | Pending / next safe action |
| ---------- | ----------- | ------------------------------------------------------------------------------------------------------- | -------------------------- |
| 2026-07-18 | Implemented | Tabs, URL state, responsive overflow, accessibility semantics, focused tests, and route docs delivered. | Complete.                  |

## Validation Results

| Date       | Command                     | Result | Notes                                                                                                        |
| ---------- | --------------------------- | ------ | ------------------------------------------------------------------------------------------------------------ |
| 2026-07-18 | Focused matter tests        | Pass   | 10 tests passed.                                                                                             |
| 2026-07-18 | Lint and typecheck          | Pass   | Both completed successfully.                                                                                 |
| 2026-07-18 | Build                       | Pass   | TypeScript/Vite compilation and approved performance budgets pass.                                           |
| 2026-07-18 | Full check                  | Pass   | Full frontend check passes after the approved CSS budget increase.                                           |
| 2026-07-18 | Pre-commit on changed files | Pass   | Hooks pass after Markdown normalization.                                                                     |
| 2026-07-18 | CSS budget approval         | Pass   | `max_total_css_bytes` increased from 21,200 to 21,400 with explicit owner approval; build uses 21,333 bytes. |

## Pause / Handoff Record

- Current state: UX-002 implementation and required validation are complete.
- Changed files and contracts: Backlog summary, capability catalog, frontend route inventory, and this implemented plan.
- Pending work: None.
- Blockers or approvals: None.
- Residual risks: Exact visual treatment may need adjustment after testing at mobile widths.
- Next safe action: None.

## Completion Documentation Review

- [x] Root and service READMEs reviewed.
- [x] Backend operation and architecture docs reviewed.
- [x] Frontend operation docs and inventories reviewed.
- [x] Foundation status files reviewed and changed only if a foundation contract moved.
- [x] AI governance docs, templates, and checklists reviewed.
- [x] Item plan and summary backlog synchronized.

Record documents intentionally unchanged and why:

- Frontend route inventory: updated because the matter detail now documents the supported `tab` query parameter values.
- Backend docs: no API or backend behavior is in scope.

## Completion Summary

- Delivered: Matter detail tabs with visible summary, grouped modules, URL persistence/fallback, accessible semantics, and responsive navigation.
- Validation: Focused tests, lint, typecheck, full check, build, performance budget, and pre-commit pass.
- Skipped validation: E2E was not required because auth/routing/error journeys did not change.
- Human approvals: Not applicable.
- Residual risk: The approved CSS budget retains 67 bytes of raw headroom.

Do not set the item to `Hecho` while any required criterion, validation, documentation update, or
approval remains incomplete.
