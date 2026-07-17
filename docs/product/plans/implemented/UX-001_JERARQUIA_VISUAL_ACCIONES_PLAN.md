# UX-001 - Jerarquía visual de botones y acciones

## Tracking Status

- ID: `UX-001`
- Type: `Frontend`
- Priority: `P1`
- Plan status: `Hecho`
- Implementation status: `Hecho`
- Last updated: `2026-07-15`
- Backlog source: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objective

Conservar el diseño minimalista de Abogado Fácil y mejorar la identificación inmediata de botones,
enlaces de acción y controles deshabilitados, sin exigir `hover` para distinguirlos del texto.

## Starting Point

La interfaz usa estilos de acción definidos de forma local en varias pantallas. Algunas acciones
tienen fondo o borde, mientras otras se presentan como texto sin una señal persistente. Los estados
deshabilitados suelen comunicarse principalmente mediante opacidad, por lo que pueden parecer texto
estático. Ya existen variantes compartidas para administración en `src/shared/rbac/ui.tsx`, pero no un
sistema visual reutilizable para toda la aplicación.

## Scope

### Included

- Definir una jerarquía visual compartida y compacta para acciones primarias, secundarias, discretas
  y destructivas.
- Definir estados perceptibles en reposo, `hover`, foco visible, presionado, carga y deshabilitado.
- Diferenciar los controles deshabilitados mediante más de una señal visual cuando corresponda, sin
  ocultarlos ni hacerlos parecer texto ordinario.
- Aplicar las variantes compartidas a botones y enlaces con apariencia de acción en las pantallas
  actuales, incluidas navegación, autenticación, dashboard, clientes, asuntos y administración.
- Conservar semántica HTML, navegación por teclado, contraste suficiente y objetivos táctiles
  razonables.
- Mantener la paleta, formas redondeadas y densidad visual actuales.

### Excluded

- Rediseño general de marca, tipografía, layout, navegación o contenido.
- Incorporar una librería externa de componentes o iconos.
- Cambiar permisos, disponibilidad funcional o comportamiento de las acciones.
- Convertir todos los enlaces de navegación contextual en botones.
- Crear infraestructura nueva de regresión visual si no puede resolverse con los gates existentes.

## Dependencies and Decisions

- Dependencies: none.
- Decisions closed: se conserva el lenguaje minimalista; la mejora se concentra en contraste,
  borde/fondo, peso tipográfico, espaciado y estados persistentes.
- Decisions closed: `hover` complementa la identificación, pero no puede ser la única señal de que
  un elemento es interactivo.
- Decisions closed: las variantes reutilizables pertenecen a `src/shared/ui`; los estilos de RBAC
  deben migrar o delegar en ellas sin invertir la dependencia `app -> features -> shared`.
- Open questions: none.

## Acceptance Criteria

- [x] Toda acción primaria o secundaria se distingue visualmente del texto circundante en reposo.
- [x] Las acciones discretas conservan una señal persistente y no dependen exclusivamente de
  `hover`, color o cursor para comunicar interactividad.
- [x] Los controles deshabilitados se reconocen como controles no disponibles y no como texto
  ordinario; conservan su etiqueta legible.
- [x] El foco de teclado es claramente visible en botones y enlaces de acción.
- [x] Las acciones destructivas se distinguen de las primarias y secundarias sin comunicar peligro
  solamente mediante color.
- [x] Elementos con comportamiento de navegación siguen siendo enlaces y los que ejecutan acciones
  siguen siendo botones.
- [x] La auditoría cubre las rutas públicas, autenticadas y administrativas existentes.
- [x] No se agregan dependencias y el build permanece dentro del presupuesto vigente.
- [x] Required documentation is synchronized with delivered behavior.
- [x] Required validation gates pass and are recorded below.
- [x] Mandatory human approvals are recorded, or explicitly not applicable.

## Affected Contracts and Files

| Surface | Expected files or contracts                                           | Change required |
| ------- | --------------------------------------------------------------------- | --------------- |
| Shared  | `frontend/src/shared/ui` y tokens/estilos globales                    | yes             |
| Runtime | componentes de rutas públicas, autenticadas y administrativas         | yes             |
| Tests   | pruebas de variantes, interacción y `accessibility.routes.test.tsx`   | yes             |
| Docs    | accesibilidad, foundation status sólo si cambia una regla, y tracking | review          |

## Work Plan

### Implementation

- [x] Inventariar botones y enlaces de acción y clasificarlos por jerarquía y semántica.
- [x] Crear variantes compartidas con estados consistentes y foco visible.
- [x] Migrar primero navegación, dashboard y flujos de producto, y después administración.
- [x] Revisar acciones deshabilitadas, pendientes y destructivas en cada pantalla afectada.
- [x] Eliminar duplicación de estilos locales cuando la variante compartida la reemplace.

### Tests and Documentation

- [x] Añadir pruebas enfocadas del contrato visual/semántico de las variantes compartidas.
- [x] Mantener verdes y ampliar cuando corresponda las pruebas de accesibilidad de rutas.
- [x] Review all documentation surfaces required by `AGENTS.md`.
- [x] Update canonical documents affected by the code diff.

### Validation

- [x] `npm --prefix frontend run test:a11y`
- [x] `npm --prefix frontend run openapi:check`
- [x] `npm --prefix frontend run check`
- [x] `npm --prefix frontend run build`
- [x] Pre-commit on changed files.

## Progress Log

| Date       | State         | Completed                                                                   | Pending / next safe action                         |
| ---------- | ------------- | --------------------------------------------------------------------------- | -------------------------------------------------- |
| 2026-07-14 | Plan prepared | Problema, alcance, decisiones y gates definidos                             | Inventariar controles y diseñar variantes shared.  |
| 2026-07-15 | En progreso   | Inventario completado; variantes compartidas iniciadas                      | Migrar pantallas, probar y validar.                |
| 2026-07-15 | Hecho         | Variantes y migración completas; pruebas, a11y, OpenAPI y build verdes      | Ejecutar pre-commit y cerrar tracking.             |
| 2026-07-15 | Refinado      | Enlaces contextuales inline separados de acciones discretas con base visual | Documentación sincronizada; sin trabajo pendiente. |

## Validation Results

| Date       | Command                                          | Result | Notes                                                                    |
| ---------- | ------------------------------------------------ | ------ | ------------------------------------------------------------------------ |
| 2026-07-15 | `npm --prefix frontend run test:a11y`            | Pass   | 7/7 pruebas.                                                             |
| 2026-07-15 | `npm --prefix frontend run check`                | Pass   | 51 archivos, 225 pruebas; branches 85.21%; incluye OpenAPI y deps audit. |
| 2026-07-15 | `npm --prefix frontend run build`                | Pass   | JS/CSS raw y gzip dentro del presupuesto; CSS 21,117 B de 21,200 B.      |
| 2026-07-15 | `.\.venv\Scripts\pre-commit.exe run --all-files` | Pass   | Todos los hooks pasaron en la segunda ejecución.                         |

## Pause / Handoff Record

- Current state: implementación, documentación, tracking y gates completos.
- Changed files and contracts: variantes shared —incluida la distinción entre enlace inline y
  acción discreta con base visual—, estilos globales, navegación, auth, dashboard, perfil, clientes,
  asuntos, notas, checklist, documentos, RBAC, pruebas y gate de accesibilidad.
- Pending work: none.
- Blockers or approvals: none; human approval not applicable.
- Residual risks: el presupuesto CSS conserva 83 B de margen raw; futuras variantes deben reutilizar
  el sistema compartido.
- Next safe action: none; UX-001 está cerrado.

Update this section before every pause or partial handoff.

## Completion Documentation Review

- [x] Root and service READMEs reviewed.
- [x] Backend operation and architecture docs reviewed.
- [x] Frontend operation docs and inventories reviewed.
- [x] Foundation status files reviewed and changed only if a foundation contract moved.
- [x] AI governance docs, templates, and checklists reviewed.
- [x] Item plan and summary backlog synchronized.

Record documents intentionally unchanged and why:

- Root/service READMEs, backend docs, route/API/runtime/security/observability/e2e inventories,
  foundation status and AI governance docs remain unchanged because UX-001 changes no routes, API,
  auth/RBAC policy, runtime configuration, foundation rule, or delivery workflow.
- `frontend/docs/operations/accessibility_gate.md` changed because the shared action hierarchy is an
  accessibility contract.

## Completion Summary

- Delivered: shared action hierarchy and migration across public, authenticated, product and admin
  surfaces, preserving native semantics and persistent interaction cues.
- Validation: a11y, check/coverage/OpenAPI/dependency audit and production build/budget pass.
- Skipped validation: e2e smoke is not required because routes, auth and error journeys did not change.
- Human approvals: not applicable.
- Residual risk: CSS raw budget has 83 B remaining; reuse variants rather than adding parallel styles.

Do not set the item to `Hecho` while any required criterion, validation, documentation update, or
approval remains incomplete.
