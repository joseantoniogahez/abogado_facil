# AI-202 - Cronología de hechos

## Tracking Status

- ID: `AI-202`
- Type: `Full-stack`
- Priority: `P1`
- Plan status: `Complete`
- Implementation status: `Hecho`
- Last updated: `2026-07-29`
- Backlog source: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objective

Generar y guardar una cronología revisable del expediente con eventos ordenados, fecha opcional y
fuente explícita cuando esté disponible.

## Starting Point

`AI-201` extendió el flujo persistente de asistencia IA. El mismo flujo ya ofrece preview firmado,
validación estructurada, revisión humana, regeneración, procedencia y lectura sin recomputación.

## Scope

### Included

- Función `matter_timeline` con eventos estructurados.
- Evento con `date` opcional, descripción y fuente opcional.
- Presentación ordenada y edición por líneas antes de aceptar.
- Persistencia, copia, conversión, regeneración y pruebas contractuales.

### Excluded

- Inferencia silenciosa de fechas inexistentes.
- Sincronización automática con cambios posteriores del expediente.
- Checklist sugerido de `AI-203`.

## Dependencies and Decisions

- Dependencies: `AI-201` y Fase 3 completos.
- Decisions closed: fechas desconocidas permanecen nulas; la fuente sólo se muestra si existe.
- Open questions: ninguna.

## Acceptance Criteria

- [x] El usuario puede generar una cronología desde el detalle del asunto.
- [x] Los eventos aparecen ordenados por fecha conocida y conservan eventos sin fecha.
- [x] Cada evento puede editarse y guarda su fuente opcional.
- [x] Required documentation is synchronized with delivered behavior.
- [x] Required validation gates pass and are recorded below.
- [x] Mandatory human approvals are recorded, or explicitly not applicable.

## Affected Contracts and Files

| Surface | Expected files or contracts              | Change required |
| ------- | ---------------------------------------- | --------------- |
| Runtime | `ai_assistance` y `matter-ai`            | yes             |
| Tests   | suites backend/frontend de asistencia IA | yes             |
| Docs    | endpoints, capacidad, OpenAPI y backlog  | yes             |

## Work Plan

### Implementation

- [x] Añadir esquema e instrucciones de `matter_timeline`.
- [x] Añadir edición, orden y presentación de eventos en frontend.
- [x] Mantener revisión y persistencia mediante el flujo existente.

### Tests and Documentation

- [x] Add or update tests with the behavior change.
- [x] Review all documentation surfaces required by `AGENTS.md`.
- [x] Update canonical documents affected by the code diff.

### Validation

- [x] Pruebas dirigidas de asistencia IA.
- [x] Backend completo con cobertura 100%.
- [x] OpenAPI sync, frontend check y build.
- [x] Pre-commit.

## Progress Log

| Date       | State       | Completed                                                        | Pending / next safe action      |
| ---------- | ----------- | ---------------------------------------------------------------- | ------------------------------- |
| 2026-07-29 | En progreso | Alcance y contrato de evento definidos.                          | Implementar backend y frontend. |
| 2026-07-29 | Hecho       | Cronología, edición, fuentes, pruebas, OpenAPI y docs completos. | Ninguna.                        |

## Validation Results

| Date       | Command                                          | Result | Notes                                          |
| ---------- | ------------------------------------------------ | ------ | ---------------------------------------------- |
| 2026-07-29 | `pytest backend/tests/features/ai_assistance -q` | Pass   | 24 pruebas.                                    |
| 2026-07-29 | `pytest backend/tests --cov=app ...`             | Pass   | 588 pruebas y cobertura 100%.                  |
| 2026-07-29 | `npm --prefix frontend run check`                | Pass   | 262 pruebas, cobertura, contratos y auditoría. |
| 2026-07-29 | `npm --prefix frontend run build`                | Pass   | Build y presupuestos aprobados.                |
| 2026-07-29 | `pre-commit run --all-files`                     | Pass   | Todos los hooks.                               |

## Pause / Handoff Record

- Current state: cronología persistente, editable y revisable disponible.
- Changed files and contracts: asistencia IA backend/frontend, OpenAPI, pruebas y docs.
- Pending work: ninguna dentro de `AI-202`.
- Blockers or approvals: ninguno.
- Residual risks: fechas y fuentes dependen de los datos aportados.
- Next safe action: iniciar `AI-203`.

## Completion Documentation Review

- [x] Root and service READMEs reviewed.
- [x] Backend operation and architecture docs reviewed.
- [x] Frontend operation docs and inventories reviewed.
- [x] Foundation status files reviewed and changed only if a foundation contract moved.
- [x] AI governance docs, templates, and checklists reviewed.
- [x] Item plan and summary backlog synchronized.

## Completion Summary

- Delivered: cronología editable con fechas válidas, eventos sin fecha y fuente opcional.
- Validation: backend 588/588 con 100%; frontend 262/262, build y pre-commit.
- Skipped validation: e2e no requerido; no cambió auth, routing ni errores.
- Human approvals: no aplicable.
- Residual risk: fechas y fuentes dependen de los datos aportados; revisión humana obligatoria.
