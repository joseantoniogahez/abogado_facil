# AI-008 - Minimizacion del contexto enviado a IA

## Tracking Status

- ID: `AI-008`
- Type: `Backend`
- Priority: `P0-IA`
- Plan status: `Complete`
- Implementation status: `Hecho`
- Last updated: `2026-07-25`
- Backlog source: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objective

Impedir que los adaptadores de IA reciban prompts o contexto arbitrario: cada llamada debe usar un
contexto construido con una instruccion explicita y solamente los campos autorizados y necesarios
para la funcion.

## Starting Point

Los proveedores comparten `AiTextRequest`, pero este acepta un `prompt: str` libre. Redis,
PostgreSQL y los logs ya excluyen prompts y documentos; falta un gate verificable antes del envio.

## Scope

### Included

- Contrato inmutable de contexto minimizado y constructor con allowlist.
- Validacion de autorizacion, necesidad y limites de tamano.
- Gate nominal en `AiTextRequest` y uso comun por OpenAI, Gemini y Mock.
- Pruebas negativas de filtrado, limites y ausencia de contenido en logs/errores.
- Documentacion operativa y de arquitectura.

### Excluded

- Funciones IA de producto y seleccion concreta de campos por caso de uso.
- Defensa completa contra prompt injection documental (`SEC-004`).
- Persistencia de prompts o contexto.

## Dependencies and Decisions

- Dependencies: `AI-003`, `AI-005`, `AI-007`, `AI-009`, `AI-010`, `OBS-001`.
- Decisions closed: la capa llamadora declara campos autorizados y necesarios; el constructor
  rechaza solicitudes fuera de autorizacion y nunca serializa campos sobrantes.
- Open questions: none.

## Acceptance Criteria

- [x] Los adaptadores solo aceptan contexto producido por el constructor compartido.
- [x] Solo se envian campos simultaneamente autorizados y necesarios.
- [x] Nombres, valores, instruccion y tamano total tienen limites explicitos.
- [x] Logs y errores no incluyen el contexto.
- [x] Required documentation is synchronized with delivered behavior.
- [x] Required validation gates pass and are recorded below.
- [x] Mandatory human approvals are recorded, or explicitly not applicable.

## Affected Contracts and Files

| Surface | Expected files or contracts                         | Change required |
| ------- | --------------------------------------------------- | --------------- |
| Runtime | `app/integrations/ai_context.py`, `ai_providers.py` | yes             |
| Tests   | provider, context and integrated lifecycle suites   | yes             |
| Docs    | operations index, architecture, foundation          | yes             |

## Work Plan

### Implementation

- [x] Crear el constructor y contrato de contexto minimizado.
- [x] Sustituir el prompt libre en el contrato de proveedor.
- [x] Aplicar el mismo payload minimizado a todos los adaptadores.

### Tests and Documentation

- [x] Add or update tests with the behavior change.
- [x] Review all documentation surfaces required by `AGENTS.md`.
- [x] Update canonical documents affected by the code diff.

### Validation

- [x] Targeted AI integration and documentation tests.
- [x] Full backend suite with 100% coverage.
- [x] Pre-commit on all files.

## Progress Log

| Date       | State       | Completed                                | Pending / next safe action     |
| ---------- | ----------- | ---------------------------------------- | ------------------------------ |
| 2026-07-25 | En progreso | Alcance y gate definidos                 | Implementar contrato y pruebas |
| 2026-07-25 | Hecho       | Runtime, pruebas, docs y gates completos | Continuar con AI-006           |

## Validation Results

| Date       | Command                                                   | Result | Notes            |
| ---------- | --------------------------------------------------------- | ------ | ---------------- |
| 2026-07-25 | `pytest` enfocado                                         | Passed | 86 passed        |
| 2026-07-25 | `pytest backend/tests --cov=app ... --cov-fail-under=100` | Passed | 532 passed; 100% |
| 2026-07-25 | `pre-commit run --all-files`                              | Passed | Todos los hooks  |
| 2026-07-25 | `git diff --check`                                        | Passed | Sin errores      |

## Pause / Handoff Record

- Current state: gate de contexto minimizado implementado y validado.
- Changed files and contracts: integracion de contexto/proveedores, pruebas, docs y tracking.
- Pending work: none for AI-008.
- Blockers or approvals: none.
- Residual risks: las funciones futuras deben declarar correctamente su allowlist; `SEC-004`
  endurecera el tratamiento de contenido documental no confiable.
- Next safe action: continuar con `AI-006`, metricas de uso, errores y latencia.

## Completion Documentation Review

- [x] Root and service READMEs reviewed.
- [x] Backend operation and architecture docs reviewed.
- [x] Frontend operation docs and inventories reviewed.
- [x] Foundation status files reviewed and changed only if a foundation contract moved.
- [x] AI governance docs, templates, and checklists reviewed.
- [x] Item plan and summary backlog synchronized.

Record documents intentionally unchanged and why:

- Root/backend README: no product setup changed; backend docs index updated.
- Frontend docs: no frontend or API contract changed.
- Foundation status: updated because provider input gained a mandatory gate.
- AI governance templates: lifecycle unchanged.

## Completion Summary

- Delivered: constructor allowlistado, limites y gate comun para todos los proveedores.
- Validation: 532 backend tests at 100% coverage; 86 focused tests; all pre-commit hooks.
- Skipped validation: none.
- Human approvals: not applicable.
- Residual risk: correct product allowlists remain the responsibility of future AI use cases;
  prompt-injection hardening remains in `SEC-004`.
