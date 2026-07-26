# AI-007 - Validación de salidas estructuradas

## Tracking Status

- ID: `AI-007`
- Type: Backend
- Priority: P0-IA
- Plan status: Complete
- Implementation status: Hecho
- Last updated: 2026-07-26
- Backlog source: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objective

Impedir que texto o JSON producido por IA se persista como resultado sin haber sido parseado y
validado contra un schema explícito y versionado.

## Starting Point

Los proveedores devuelven texto normalizado y `AIJob` conserva `schema_version`, pero
`AIJobsService.succeed` acepta actualmente cualquier diccionario. No existe un artefacto que
demuestre validación previa ni una comprobación de versión al persistir.

## Scope

### Included

- Validador compartido de JSON de IA basado en schemas Pydantic.
- Resultado validado que conserva datos y versión de schema.
- Rechazo seguro de JSON malformado, shape inválido y campos no permitidos por el schema.
- Gate en `AIJobsService.succeed` que sólo acepta resultados validados y con la misma versión.
- Pruebas de éxito, fallos, seguridad de mensajes, persistencia y logging.

### Excluded

- Schemas de funciones IA concretas.
- Reparación automática de JSON o segundo intento al proveedor.
- Endpoints, UI, copiar o exportar resultados.
- Persistir texto crudo o detalles de validación.

## Dependencies and Decisions

- Dependencies: `AI-009`, `AI-011`, `OBS-001` y `TEST-AI-001`.
- Decisions closed: Pydantic es la autoridad de schema existente; fallos de parse/validación usan
  `provider_invalid_response`; la versión debe coincidir con `AIJob.schema_version`.
- Open questions: ninguna.

## Acceptance Criteria

- [x] JSON válido produce datos normalizados y versionados.
- [x] JSON malformado o shape inválido se rechaza con un error seguro no reintentable.
- [x] `AIJobsService.succeed` no acepta resultados sin validar.
- [x] Una versión distinta a la registrada en `AIJob` se rechaza antes de persistir.
- [x] Texto crudo y detalles de validación no aparecen en excepciones ni logs.
- [x] Required documentation is synchronized with delivered behavior.
- [x] Required validation gates pass and are recorded below.
- [x] Mandatory human approvals are recorded, or explicitly not applicable.

## Affected Contracts and Files

| Surface | Expected files or contracts                 | Change required |
| ------- | ------------------------------------------- | --------------- |
| Runtime | structured output validator, AIJobs service | yes             |
| Tests   | validator, AIJobs service, docs contracts   | yes             |
| Docs    | lifecycle, errors, architecture, foundation | yes             |

## Work Plan

### Implementation

- [x] Implementar resultado validado y validador JSON/schema.
- [x] Exigir resultado validado y versión coincidente al completar `AIJob`.
- [x] Mantener errores y observabilidad libres de contenido externo.

### Tests and Documentation

- [x] Add or update tests with the behavior change.
- [x] Review all documentation surfaces required by `AGENTS.md`.
- [x] Update canonical documents affected by the code diff.

### Validation

- [x] Pruebas focalizadas del validador, AIJobs y documentación.
- [x] `python -m pytest backend/tests`
- [x] Cobertura backend 100%.
- [x] `pre-commit run --all-files`.

## Progress Log

| Date       | State       | Completed                                 | Pending / next safe action |
| ---------- | ----------- | ----------------------------------------- | -------------------------- |
| 2026-07-25 | En progreso | Alcance y gate de persistencia definidos  | Implementar el validador   |
| 2026-07-25 | Hecho       | Gate, pruebas y documentación completados | Sin trabajo pendiente      |

## Validation Results

| Date       | Command                                                                                                | Result | Notes                             |
| ---------- | ------------------------------------------------------------------------------------------------------ | ------ | --------------------------------- |
| 2026-07-25 | Pruebas focalizadas de outputs, AIJobs y docs                                                          | Passed | 26 pruebas; módulo nuevo al 100%  |
| 2026-07-25 | `python -m pytest backend/tests --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=100` | Passed | 521 pruebas; cobertura total 100% |
| 2026-07-25 | `pre-commit run --all-files`                                                                           | Passed | Todos los hooks pasan             |

## Pause / Handoff Record

- Current state: ningún `AIJob` puede completarse con un resultado arbitrario o con schema distinto.
- Changed files and contracts: validador de outputs, gate AIJobs, pruebas, docs de operación,
  arquitectura, foundation status y tracking.
- Pending work: ninguno dentro de `AI-007`.
- Blockers or approvals: ninguno.
- Residual risks: cada función futura debe declarar su schema concreto con restricciones adecuadas.
- Next safe action: continuar con `AI-008`, minimización del contexto enviado.

## Completion Documentation Review

- [x] Root and service READMEs reviewed.
- [x] Backend operation and architecture docs reviewed.
- [x] Frontend operation docs and inventories reviewed.
- [x] Foundation status files reviewed and changed only if a foundation contract moved.
- [x] AI governance docs, templates, and checklists reviewed.
- [x] Item plan and summary backlog synchronized.

Record documents intentionally unchanged and why:

- Root/backend README: backend docs index actualizado; root README sin cambio porque no hay
  dependencia, endpoint ni configuración nuevos.
- API/auth/RBAC/OpenAPI: sin cambio; es un gate interno previo a persistencia.
- Arquitectura y operaciones: ports/adapters, lifecycle y nuevo contrato de outputs actualizados.
- Frontend: sin cambio; no existe una superficie consumidora todavía.
- Foundation status: actualizado porque la validación pasa a ser una regla transversal.
- AI governance: proceso sin cambio; backlog, plan e índices sincronizados.

## Completion Summary

- Delivered: parseo y validación Pydantic segura, `ValidatedAIOutput`, copia defensiva, error
  normalizado y gate de schema/version en `AIJobsService`.
- Validation: 26 pruebas focalizadas; 521 pruebas backend con cobertura 100%; pre-commit completo.
- Skipped validation: endpoints/UI/proveedores reales; el ticket es un gate interno sin función IA
  pública.
- Human approvals: not applicable.
- Residual risk: los schemas de producto y sus versiones se entregarán con cada función IA.

Do not set the item to `Hecho` while any required criterion, validation, documentation update, or
approval remains incomplete.

## Reopened Gate Review - 2026-07-26

- Direct `ValidatedAIOutput` construction now fails without the module-private factory capability.
- Invalid factory capabilities are rejected explicitly.
- `data` returns a deep defensive copy, so callers cannot mutate validated state.
- Technical representations omit validated data to prevent accidental logging disclosure.
- AI job tests create every successful result through `validate_ai_output` and a real closed schema.
- Focused validation: 86 passed; affected modules at 100% coverage.
- Full validation: 547 passed; total backend coverage 100%.
- Documentation contracts: 37 passed after formatting.
- Pre-commit: all hooks passed on the second run after `mdformat` normalized Markdown.
- Residual risk: function-specific schemas still require review; no gate bypass remains open.
