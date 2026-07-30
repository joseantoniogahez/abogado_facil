# AI-201 - Resumen del expediente

## Tracking Status

- ID: `AI-201`
- Type: `Full-stack`
- Priority: `P1`
- Plan status: `Complete`
- Implementation status: `Hecho`
- Last updated: `2026-07-29`
- Backlog source: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objective

Permitir que el usuario genere, revise, guarde y reutilice un resumen estructurado de un expediente
sin ejecutar nuevamente al proveedor al consultar resultados existentes.

## Starting Point

La Fase 3 ya persiste resultados IA aislados por despacho y asunto, con preview firmado, BYOK,
validación estructurada, revisión humana, procedencia, regeneración y lectura sin recomputación.
`AI-201` puede extender ese flujo con una función y esquema propios.

## Scope

### Included

- Función `matter_summary` con resumen ejecutivo, estado del asunto, hechos clave, pendientes y
  próximos pasos.
- Selección, preview, ejecución, revisión, copia, conversión y regeneración en la interfaz existente.
- Persistencia y consulta mediante el contrato de resultados IA existente.
- Pruebas backend/frontend, OpenAPI y documentación contractual sincronizada.

### Excluded

- Cronología editable (`AI-202`) y checklist sugerido (`AI-203`).
- Recomposición automática al abrir o modificar el asunto.
- Nuevas fuentes documentales o herramientas del proveedor.

## Dependencies and Decisions

- Dependencies: Fase 3 y gates `P0-IA` ya cerrados.
- Decisions closed: reutilizar el slice `ai_assistance`; la consulta sólo lee resultados persistidos.
- Open questions: ninguna.

## Acceptance Criteria

- [x] El usuario puede ejecutar `matter_summary` desde el detalle del asunto.
- [x] La salida estructurada se valida antes de persistir y puede revisarse.
- [x] El resultado guardado aparece en consultas posteriores sin llamar al proveedor.
- [x] Required documentation is synchronized with delivered behavior.
- [x] Required validation gates pass and are recorded below.
- [x] Mandatory human approvals are recorded, or explicitly not applicable.

## Affected Contracts and Files

| Surface | Expected files or contracts                    | Change required |
| ------- | ---------------------------------------------- | --------------- |
| Runtime | `ai_assistance` backend y `matter-ai` frontend | yes             |
| Tests   | suites dirigidas backend/frontend              | yes             |
| Docs    | endpoints, consumidores, capacidad y OpenAPI   | yes             |

## Work Plan

### Implementation

- [x] Añadir esquema e instrucciones de `matter_summary`.
- [x] Añadir selección y presentación estructurada en frontend.
- [x] Confirmar persistencia y lectura sin recomputación mediante pruebas.

### Tests and Documentation

- [x] Add or update tests with the behavior change.
- [x] Review all documentation surfaces required by `AGENTS.md`.
- [x] Update canonical documents affected by the code diff.

### Validation

- [x] Pruebas dirigidas de `ai_assistance`.
- [x] Backend tests y cobertura 100%.
- [x] OpenAPI sync, frontend check y build.
- [x] Pre-commit on changed files.

## Progress Log

| Date       | State       | Completed                                                       | Pending / next safe action         |
| ---------- | ----------- | --------------------------------------------------------------- | ---------------------------------- |
| 2026-07-29 | En progreso | Alcance y reutilización del flujo de Fase 3 definidos.          | Implementar esquema, UI y pruebas. |
| 2026-07-29 | Hecho       | Función, UI, OpenAPI, pruebas, documentación y gates completos. | Ninguna.                           |

## Validation Results

| Date       | Command                                                   | Result | Notes                                            |
| ---------- | --------------------------------------------------------- | ------ | ------------------------------------------------ |
| 2026-07-29 | `pytest backend/tests/features/ai_assistance -q`          | Pass   | 22 pruebas.                                      |
| 2026-07-29 | `pytest backend/tests --cov=app ... --cov-fail-under=100` | Pass   | 586 pruebas; cobertura 100%.                     |
| 2026-07-29 | `npm --prefix frontend run check`                         | Pass   | 261 pruebas, lint, tipos, contratos y cobertura. |
| 2026-07-29 | `npm --prefix frontend run build`                         | Pass   | Build y presupuestos de rendimiento.             |
| 2026-07-29 | `pre-commit run --all-files`                              | Pass   | Todos los hooks.                                 |

## Pause / Handoff Record

- Current state: `matter_summary` está disponible dentro del flujo IA controlado.
- Changed files and contracts: esquema backend, UI/contrato frontend, OpenAPI y docs.
- Pending work: ninguna dentro de `AI-201`.
- Blockers or approvals: ninguno.
- Residual risks: exactitud y costo dependen del proveedor BYOK.
- Next safe action: iniciar `AI-202`.

## Completion Documentation Review

- [x] Root and service READMEs reviewed.
- [x] Backend operation and architecture docs reviewed.
- [x] Frontend operation docs and inventories reviewed.
- [x] Foundation status files reviewed and changed only if a foundation contract moved.
- [x] AI governance docs, templates, and checklists reviewed.
- [x] Item plan and summary backlog synchronized.

## Completion Summary

- Delivered: resumen estructurado persistente y revisable del expediente.
- Validation: backend 586/586 con 100%; frontend 261/261, build y pre-commit.
- Skipped validation: e2e no requerido; no cambió auth, routing ni el pipeline de errores.
- Human approvals: no aplicable.
- Residual risk: exactitud y costo dependen del proveedor BYOK; revisión humana obligatoria.
