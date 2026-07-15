# UX-001 - Jerarquía visual de botones y acciones

## Tracking Status

- ID: `UX-001`
- Type: `Frontend`
- Priority: `P1`
- Plan status: `Ready`
- Implementation status: `Listo`
- Last updated: `2026-07-14`
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

- [ ] Toda acción primaria o secundaria se distingue visualmente del texto circundante en reposo.
- [ ] Las acciones discretas conservan una señal persistente y no dependen exclusivamente de
  `hover`, color o cursor para comunicar interactividad.
- [ ] Los controles deshabilitados se reconocen como controles no disponibles y no como texto
  ordinario; conservan su etiqueta legible.
- [ ] El foco de teclado es claramente visible en botones y enlaces de acción.
- [ ] Las acciones destructivas se distinguen de las primarias y secundarias sin comunicar peligro
  solamente mediante color.
- [ ] Elementos con comportamiento de navegación siguen siendo enlaces y los que ejecutan acciones
  siguen siendo botones.
- [ ] La auditoría cubre las rutas públicas, autenticadas y administrativas existentes.
- [ ] No se agregan dependencias y el build permanece dentro del presupuesto vigente.
- [ ] Required documentation is synchronized with delivered behavior.
- [ ] Required validation gates pass and are recorded below.
- [ ] Mandatory human approvals are recorded, or explicitly not applicable.

## Affected Contracts and Files

| Surface | Expected files or contracts                                           | Change required |
| ------- | --------------------------------------------------------------------- | --------------- |
| Shared  | `frontend/src/shared/ui` y tokens/estilos globales                    | yes             |
| Runtime | componentes de rutas públicas, autenticadas y administrativas         | yes             |
| Tests   | pruebas de variantes, interacción y `accessibility.routes.test.tsx`   | yes             |
| Docs    | accesibilidad, foundation status sólo si cambia una regla, y tracking | review          |

## Work Plan

### Implementation

- [ ] Inventariar botones y enlaces de acción y clasificarlos por jerarquía y semántica.
- [ ] Crear variantes compartidas con estados consistentes y foco visible.
- [ ] Migrar primero navegación, dashboard y flujos de producto, y después administración.
- [ ] Revisar acciones deshabilitadas, pendientes y destructivas en cada pantalla afectada.
- [ ] Eliminar duplicación de estilos locales cuando la variante compartida la reemplace.

### Tests and Documentation

- [ ] Añadir pruebas enfocadas del contrato visual/semántico de las variantes compartidas.
- [ ] Mantener verdes y ampliar cuando corresponda las pruebas de accesibilidad de rutas.
- [ ] Review all documentation surfaces required by `AGENTS.md`.
- [ ] Update canonical documents affected by the code diff.

### Validation

- [ ] `npm --prefix frontend run test:a11y`
- [ ] `npm --prefix frontend run openapi:check`
- [ ] `npm --prefix frontend run check`
- [ ] `npm --prefix frontend run build`
- [ ] Pre-commit on changed files.

## Progress Log

| Date       | State         | Completed                                       | Pending / next safe action                        |
| ---------- | ------------- | ----------------------------------------------- | ------------------------------------------------- |
| 2026-07-14 | Plan prepared | Problema, alcance, decisiones y gates definidos | Inventariar controles y diseñar variantes shared. |

## Validation Results

| Date | Command | Result | Notes |
| ---- | ------- | ------ | ----- |
|      |         |        |       |

## Pause / Handoff Record

- Current state: el comportamiento y diseño runtime no cambian; el ítem está listo para iniciar.
- Changed files and contracts: backlog y plan de UX-001; ningún contrato runtime.
- Pending work: inventario, variantes compartidas, migración, pruebas y revisión documental.
- Blockers or approvals: none.
- Residual risks: una migración amplia puede producir inconsistencias temporales si se pausa a mitad;
  debe organizarse por grupos completos de pantallas y registrar el punto de reanudación.
- Next safe action: inventariar cada control interactivo y proponer las variantes compartidas antes
  de modificar pantallas.

Update this section before every pause or partial handoff.

## Completion Documentation Review

- [ ] Root and service READMEs reviewed.
- [ ] Backend operation and architecture docs reviewed.
- [ ] Frontend operation docs and inventories reviewed.
- [ ] Foundation status files reviewed and changed only if a foundation contract moved.
- [ ] AI governance docs, templates, and checklists reviewed.
- [ ] Item plan and summary backlog synchronized.

Record documents intentionally unchanged and why:

- Pending implementation review.

## Completion Summary

- Delivered: backlog item and implementation-ready UX plan only.
- Validation: documentation hooks pending.
- Skipped validation: frontend runtime gates are not applicable until implementation starts.
- Human approvals: not applicable to backlog capture.
- Residual risk: the visual inventory must confirm the final migration surface.

Do not set the item to `Hecho` while any required criterion, validation, documentation update, or
approval remains incomplete.
