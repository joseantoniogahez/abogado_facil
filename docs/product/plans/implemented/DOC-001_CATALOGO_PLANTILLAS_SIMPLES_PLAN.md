# DOC-001 - Catálogo de plantillas simples

## Tracking Status

- ID: `DOC-001`
- Type: `Full-stack`
- Priority: `P1`
- Plan status: `Complete`
- Implementation status: `Hecho`
- Last updated: `2026-07-31`
- Backlog source: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objective

Ofrecer un catálogo autenticado y reutilizable de plantillas documentales simples para que
`DOC-002` pueda construir formularios sobre un contrato estable.

## Scope

### Included

- Catálogo inmutable con requerimiento de pago, convenio de pago, solicitud de documentos y
  resumen interno.
- Metadatos de finalidad y campos requeridos u opcionales.
- Endpoint autenticado `GET /v1/document-templates`.
- Pantalla protegida `/document-templates`, navegación y estados accesibles.
- Pruebas, OpenAPI y documentación de contratos.

### Excluded

- Generación, persistencia o edición de borradores (`DOC-002`).
- Copia, descarga o exportación (`DOC-003`).
- Uso de IA, envío o presentación automática.

## Dependencies and Decisions

- Dependencies: fundación de autenticación, API y frontend existente.
- Decision: catálogo versionado en código, no datos por despacho.
- Decision: ruta global protegida, separada de los archivos adjuntos por asunto.
- Open questions: ninguna bloqueante.

## Acceptance Criteria

- [x] La API devuelve exactamente los cuatro tipos iniciales y sus campos.
- [x] La pantalla presenta las cuatro plantillas con propósito y requisitos.
- [x] Carga, error recuperable, navegación y accesibilidad quedan cubiertos.
- [x] OpenAPI, inventarios y documentación quedan sincronizados.
- [x] Gates backend, frontend y pre-commit pasan.

## Work Plan

### Implementation

- [x] Crear slice backend estático, esquema, metadata OpenAPI y router.
- [x] Crear consumidor, parser, pantalla protegida y navegación frontend.

### Tests and Documentation

- [x] Add or update tests with the behavior change.
- [x] Review all documentation surfaces required by `AGENTS.md`.
- [x] Update canonical documents affected by the code diff.

### Validation

- [x] Backend tests and 100% coverage.
- [x] OpenAPI sync, frontend check and build.
- [x] Pre-commit on all files.

## Progress Log

| Date       | State       | Completed                                                | Pending / next safe action               |
| ---------- | ----------- | -------------------------------------------------------- | ---------------------------------------- |
| 2026-07-31 | En progreso | Alcance, contrato y frontera de fase definidos.          | Implementar catálogo backend y frontend. |
| 2026-07-31 | Hecho       | API, UI, pruebas, contratos y documentación completados. | Continuar con `DOC-002`.                 |

## Validation Results

| Date       | Command                                                         | Result | Notes                                        |
| ---------- | --------------------------------------------------------------- | ------ | -------------------------------------------- |
| 2026-07-31 | `python -m pytest backend/tests --cov=app --cov-fail-under=100` | Pass   | 590 pruebas; cobertura total de 100 %.       |
| 2026-07-31 | `npm --prefix frontend run openapi:sync`                        | Pass   | Artefacto sincronizado con el endpoint.      |
| 2026-07-31 | `npm --prefix frontend run check`                               | Pass   | Lint, tipos, pruebas, cobertura y contratos. |
| 2026-07-31 | `npm --prefix frontend run build`                               | Pass   | Build y presupuestos de rendimiento pasan.   |
| 2026-07-31 | `pre-commit run --all-files`                                    | Pass   | Hooks pasan tras formateo automático.        |

## Pause / Handoff Record

- Current state: implementación completa y validada.
- Changed files and contracts: catálogo API, ruta protegida, OpenAPI e inventarios.
- Pending work: ninguno para `DOC-001`; `DOC-002` implementará los borradores.
- Blockers or approvals: ninguno.
- Residual risks: mantener el catálogo alineado con el formulario futuro.
- Next safe action: preparar el plan de `DOC-002` sobre este contrato.

## Completion Documentation Review

- [x] Root and service READMEs reviewed.
- [x] Backend operation and architecture docs reviewed.
- [x] Frontend operation docs and inventories reviewed.
- [x] Foundation status files reviewed and intentionally unchanged; no foundation contract moved.
- [x] AI governance docs, templates, and checklists reviewed.
- [x] Item plan and summary backlog synchronized.

## Completion Summary

- Delivered: catálogo autenticado de cuatro plantillas, campos, pantalla protegida y navegación.
- Validation: backend 100 %, OpenAPI, frontend check/build y pre-commit.
- Skipped validation: E2E no aplica; no cambiaron autenticación ni manejo global de errores.
- Human approvals: no aplicable.
- Residual risk: `DOC-002` podría ajustar campos y deberá mantener el contrato sincronizado.
