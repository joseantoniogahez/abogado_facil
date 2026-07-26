# DOCS-AI-002 - Flujo de datos y threat model de IA

## Tracking Status

- ID: `DOCS-AI-002`
- Type: `Docs`
- Priority: `P1`
- Plan status: `Complete`
- Implementation status: `Hecho`
- Last updated: `2026-07-26`
- Backlog source: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objective

Documentar el flujo de datos de IA, sus limites de confianza, controles existentes y riesgos
residuales antes de habilitar funciones reales.

## Starting Point

Existen contratos operativos separados para BYOK, RQ, contexto, outputs y observabilidad, pero falta
una vista integral que conecte las fronteras y el threat model.

## Scope

### Included

- Flujo API/aplicacion, PostgreSQL, Redis/RQ, proveedor y resultado validado.
- Limites de confianza para credenciales, documentos, logs y resultados.
- Amenazas, controles actuales, riesgos residuales y gates posteriores.

### Excluded

- Implementar `SEC-004` o funciones IA de producto.
- Diagramas dependientes de un proveedor concreto.

## Dependencies and Decisions

- Dependencies: `AI-001` a `AI-011`, `OBS-001`, `TEST-AI-001`.
- Decisions closed: documento canonico bajo arquitectura backend y referencias a contratos
  operativos existentes.
- Open questions: none.

## Acceptance Criteria

- [x] El flujo de datos y cada limite de confianza son explicitos.
- [x] Credenciales, contexto, Redis, proveedores, outputs y logs tienen amenazas y controles.
- [x] Riesgos residuales enlazan tickets concretos sin declarar garantias inexistentes.
- [x] Required documentation is synchronized with delivered behavior.
- [x] Required validation gates pass and are recorded below.
- [x] Mandatory human approvals are recorded, or explicitly not applicable.

## Affected Contracts and Files

| Surface | Expected files or contracts           | Change required |
| ------- | ------------------------------------- | --------------- |
| Runtime | none                                  | no              |
| Tests   | documentation contracts               | yes             |
| Docs    | architecture, indexes, plans, backlog | yes             |

## Work Plan

### Implementation

- [x] Crear el flujo de datos y threat model integral.
- [x] Enlazar contratos operativos y riesgos residuales.

### Tests and Documentation

- [x] Add or update tests with the behavior change.
- [x] Review all documentation surfaces required by `AGENTS.md`.
- [x] Update canonical documents affected by the code diff.

### Validation

- [x] Documentation contract tests.
- [x] Full backend gates.
- [x] Pre-commit on all files.

## Progress Log

| Date       | State       | Completed                                 | Pending / next safe action      |
| ---------- | ----------- | ----------------------------------------- | ------------------------------- |
| 2026-07-26 | En progreso | Alcance y ubicacion definidos             | Escribir y validar el documento |
| 2026-07-26 | Hecho       | Threat model, contratos y gates completos | Continuar con SEC-004           |

## Validation Results

| Date       | Command                            | Result | Notes               |
| ---------- | ---------------------------------- | ------ | ------------------- |
| 2026-07-26 | pruebas focalizadas y documentales | Passed | 86 y 37 pruebas     |
| 2026-07-26 | suite backend con coverage         | Passed | 547; cobertura 100% |
| 2026-07-26 | `pre-commit run --all-files`       | Passed | todos los hooks     |

## Pause / Handoff Record

- Current state: documento canonico implementado y validado.
- Changed files and contracts: arquitectura IA, indice backend, prueba contractual y tracking.
- Pending work: none.
- Blockers or approvals: none.
- Residual risks: `SEC-004` sigue siendo gate previo a funciones IA reales.
- Next safe action: continuar con `SEC-004`.

## Completion Documentation Review

- [x] Root and service READMEs reviewed.
- [x] Backend operation and architecture docs reviewed.
- [x] Frontend operation docs and inventories reviewed.
- [x] Foundation status files reviewed and changed only if a foundation contract moved.
- [x] AI governance docs, templates, and checklists reviewed.
- [x] Item plan and summary backlog synchronized.

Record documents intentionally unchanged and why:

- Root/backend README: backend docs index updated; setup unchanged.
- Frontend docs: no frontend or API consumer changed.
- Foundation status: updated because the two mandatory gates were strengthened.

## Completion Summary

- Delivered: flujo de datos, limites de confianza, amenazas, controles y release gates.
- Validation: 547 backend tests, 100% coverage, 37 documentation tests and all pre-commit hooks.
- Skipped validation: none.
- Human approvals: not applicable.
- Residual risk: `SEC-004` and `LEGAL-002A` remain explicit gates before real AI workflows.
