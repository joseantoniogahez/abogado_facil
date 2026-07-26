# AI-006 - Metricas de uso, errores y latencia de IA

## Tracking Status

- ID: `AI-006`
- Type: `Backend`
- Priority: `P1`
- Plan status: `Complete`
- Implementation status: `Hecho`
- Last updated: `2026-07-25`
- Backlog source: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objective

Registrar metricas iniciales agregadas por proveedor y funcion IA, distinguiendo resultado y codigo
de error, con conteo y latencia, sin incluir contexto, credenciales ni identificadores personales.

## Starting Point

Los adaptadores emiten eventos correlacionados con duracion, pero `AiTextRequest` no identifica la
funcion y no existe un registro agregado consultable o exportable.

## Scope

### Included

- Registro thread-safe, en memoria y de cardinalidad acotada.
- Etiquetas proveedor, funcion, resultado y error normalizado.
- Conteo, latencia total, maxima y promedio derivable.
- Instrumentacion comun de OpenAI, Gemini y Mock.
- Pruebas de exito, fallos normalizados, fallos inesperados y redaccion.

### Excluded

- Endpoint o dashboard de metricas.
- Persistencia historica y exportador Prometheus/OpenTelemetry (`OBS-002`).
- Costos monetarios o tokens cuando el proveedor no los entrega de forma uniforme.

## Dependencies and Decisions

- Dependencies: `AI-003`, `AI-005`, `AI-011`, `OBS-001`.
- Decisions closed: usar un puerto/registro interno sin dependencia nueva; las etiquetas se validan
  para evitar cardinalidad no acotada y datos controlados por proveedor.
- Open questions: none.

## Acceptance Criteria

- [x] Cada llamada registra una sola observacion por proveedor, funcion y resultado.
- [x] Los fallos normalizados incluyen codigo seguro; los inesperados usan codigo interno estable.
- [x] El snapshot expone conteo y latencias agregadas sin contenido sensible.
- [x] Required documentation is synchronized with delivered behavior.
- [x] Required validation gates pass and are recorded below.
- [x] Mandatory human approvals are recorded, or explicitly not applicable.

## Affected Contracts and Files

| Surface | Expected files or contracts                   | Change required |
| ------- | --------------------------------------------- | --------------- |
| Runtime | observabilidad y proveedores IA               | yes             |
| Tests   | observabilidad, providers y contratos         | yes             |
| Docs    | contrato operativo, arquitectura y foundation | yes             |

## Work Plan

### Implementation

- [x] Crear registro y snapshot de metricas IA.
- [x] Añadir funcion al request y validarla.
- [x] Instrumentar resultado y duracion en el wrapper comun.

### Tests and Documentation

- [x] Add or update tests with the behavior change.
- [x] Review all documentation surfaces required by `AGENTS.md`.
- [x] Update canonical documents affected by the code diff.

### Validation

- [x] Targeted metrics/provider/documentation tests.
- [x] Full backend suite with 100% coverage.
- [x] Pre-commit on all files.

## Progress Log

| Date       | State       | Completed                                           | Pending / next safe action    |
| ---------- | ----------- | --------------------------------------------------- | ----------------------------- |
| 2026-07-25 | En progreso | Alcance y diseño cerrados                           | Implementar runtime y pruebas |
| 2026-07-25 | Hecho       | Registro, instrumentacion, pruebas y docs completos | Iniciar gates de Fase 3       |

## Validation Results

| Date       | Command                                                   | Result | Notes                                |
| ---------- | --------------------------------------------------------- | ------ | ------------------------------------ |
| 2026-07-25 | `pytest` enfocado con coverage                            | Passed | 89 passed; modulos afectados al 100% |
| 2026-07-25 | `pytest backend/tests --cov=app ... --cov-fail-under=100` | Passed | 544 passed; 100%                     |
| 2026-07-25 | `pre-commit run --all-files`                              | Passed | Todos los hooks                      |

## Pause / Handoff Record

- Current state: metricas iniciales implementadas y validadas.
- Changed files and contracts: registro comun, contrato de request, providers, pruebas y docs.
- Pending work: none for AI-006.
- Blockers or approvals: none.
- Residual risks: el registro es local por proceso hasta implementar `OBS-002`.
- Next safe action: iniciar `SEC-004` o `LEGAL-002A` antes del hero flow de Fase 3.

## Completion Documentation Review

- [x] Root and service READMEs reviewed.
- [x] Backend operation and architecture docs reviewed.
- [x] Frontend operation docs and inventories reviewed.
- [x] Foundation status files reviewed and changed only if a foundation contract moved.
- [x] AI governance docs, templates, and checklists reviewed.
- [x] Item plan and summary backlog synchronized.

Record documents intentionally unchanged and why:

- Root/backend README: no setup changed; backend docs index updated.
- Frontend docs: no frontend or API surface changed.
- Foundation status: updated because provider calls gained a mandatory metrics contract.
- AI governance templates: lifecycle unchanged.

## Completion Summary

- Delivered: metricas agregadas por provider, funcion, resultado, error y latencia.
- Validation: 544 backend tests at 100% coverage; 89 focused tests; all pre-commit hooks.
- Skipped validation: none.
- Human approvals: not applicable.
- Residual risk: registry data is process-local until `OBS-002` adds multiprocess export/aggregation.
