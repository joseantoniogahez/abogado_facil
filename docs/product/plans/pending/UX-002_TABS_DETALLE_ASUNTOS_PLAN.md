# UX-002 - Tabs para el detalle de asuntos

## Tracking Status

- ID: `UX-002`
- Type: `Frontend`
- Priority: `P1`
- Plan status: `Ready`
- Implementation status: `Listo`
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

- [ ] Crear el componente o patrón de tabs dentro del feature de asuntos.
- [ ] Separar los módulos actuales en los cuatro grupos definidos.
- [ ] Persistir y validar la tab activa con `useSearchParams`.
- [ ] Ajustar estilos responsive y estados de foco/selección.

### Tests and Documentation

- [ ] Add or update tests with the behavior change.
- [ ] Review all documentation surfaces required by `AGENTS.md`.
- [ ] Update canonical documents affected by the code diff.

### Validation

- [ ] `npm --prefix frontend run check`
- [ ] `npm --prefix frontend run build`
- [ ] `pre-commit run --files <changed-files>`

## Progress Log

| Date       | State         | Completed                                     | Pending / next safe action                                          |
| ---------- | ------------- | --------------------------------------------- | ------------------------------------------------------------------- |
| 2026-07-18 | Plan prepared | Backlog item and executable scope registered. | Implement tabs, tests, responsive behavior, and run frontend gates. |

## Validation Results

| Date | Command | Result | Notes                                                                         |
| ---- | ------- | ------ | ----------------------------------------------------------------------------- |
|      |         |        | No implementation validation run; this turn only registered the backlog item. |

## Pause / Handoff Record

- Current state: Scope and plan are ready; no code implementation has started.
- Changed files and contracts: Backlog summary and this pending plan.
- Pending work: Implement UX-002 and validate the frontend behavior.
- Blockers or approvals: None.
- Residual risks: Exact visual treatment may need adjustment after testing at mobile widths.
- Next safe action: Read the affected matter tests and implement the tabs in the existing matter detail feature.

## Completion Documentation Review

- [ ] Root and service READMEs reviewed.
- [ ] Backend operation and architecture docs reviewed.
- [ ] Frontend operation docs and inventories reviewed.
- [ ] Foundation status files reviewed and changed only if a foundation contract moved.
- [x] AI governance docs, templates, and checklists reviewed.
- [x] Item plan and summary backlog synchronized.

Record documents intentionally unchanged and why:

- Frontend route inventory: no route path changes are made by this backlog item; review again during implementation if query-parameter behavior must be documented.
- Backend docs: no API or backend behavior is in scope.

## Completion Summary

- Delivered: Backlog registration and pending implementation plan for the matter-detail tabs redesign.
- Validation: Not applicable; no code changed.
- Skipped validation: Frontend tests/build/pre-commit, because implementation has not started.
- Human approvals: Not applicable at planning stage.
- Residual risk: The final grouping and responsive presentation should be confirmed during implementation.

Do not set the item to `Hecho` while any required criterion, validation, documentation update, or
approval remains incomplete.
