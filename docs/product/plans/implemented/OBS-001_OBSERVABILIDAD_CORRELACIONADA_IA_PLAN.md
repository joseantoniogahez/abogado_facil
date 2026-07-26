# OBS-001 - Observabilidad correlacionada de IA

## Tracking Status

- ID: `OBS-001`
- Type: Ops
- Priority: P1
- Plan status: Complete
- Implementation status: Hecho
- Last updated: 2026-07-25
- Backlog source: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objective

Permitir seguir una ejecución de IA mediante el mismo `request_id` y `execution_id` desde su
creación en API, paso por `AIJob` y RQ, hasta el proveedor y su resultado, usando eventos
estructurados que nunca incluyan prompts, documentos, respuestas, credenciales ni mensajes externos.

## Starting Point

El middleware ya asigna `request_id`; `AIJob` persiste el par de correlación; RQ transporta sólo
`execution_id`; y streaming registra ambos IDs. Sin embargo, el servicio de jobs, el scheduler RQ y
los adaptadores OpenAI/Gemini/Mock no emiten todavía un recorrido común. Tampoco existe aún un
handler funcional de producto.

## Scope

### Included

- Contexto común de correlación y validación segura de identificadores.
- Eventos estructurados para lifecycle de `AIJob`, enqueue/deduplicación RQ y llamadas a proveedor.
- Duración, estado, intento y código normalizado donde sean aplicables.
- Redacción preventiva y pruebas negativas para datos sensibles.
- Política documentada para que futuros workers recuperen el `request_id` desde PostgreSQL.

### Excluded

- Primer endpoint o handler funcional de IA.
- Persistir `request_id` adicional en Redis.
- Exportador OTLP, tracing distribuido o dashboard de métricas.
- Registrar prompts, resultados, cuerpos externos o mensajes de excepción.
- Métricas agregadas de negocio/proveedor.

## Dependencies and Decisions

- Dependencies: `AI-005`, `AI-009`, `AI-010` y `AI-011`.
- Decisions closed: PostgreSQL/`AIJob` conserva la correlación completa; Redis transporta sólo
  `execution_id`; los logs usan pares key/value ordenados y campos permitidos; un ID entrante no
  seguro se reemplaza por uno opaco.
- Open questions: ninguna.

## Acceptance Criteria

- [x] El lifecycle de `AIJob` registra el mismo `request_id` y `execution_id` en cada transición.
- [x] RQ registra enqueue, duplicado y fallo sin añadir contexto sensible al payload Redis.
- [x] OpenAI, Gemini y Mock registran inicio, éxito o fallo con ambos IDs y duración.
- [x] Los fallos registran sólo código normalizado y clase segura, nunca mensaje/cuerpo externo.
- [x] IDs de correlación no seguros no pueden inyectar líneas o campos en logs.
- [x] Pruebas demuestran un recorrido correlacionable y ausencia de prompt, respuesta, clave y
  detalles externos.
- [x] Required documentation is synchronized with delivered behavior.
- [x] Required validation gates pass and are recorded below.
- [x] Mandatory human approvals are recorded, or explicitly not applicable.

## Affected Contracts and Files

| Surface | Expected files or contracts                             | Change required |
| ------- | ------------------------------------------------------- | --------------- |
| Runtime | observability, middleware, AI jobs, RQ, providers       | yes             |
| Tests   | observability, middleware, jobs, RQ, providers, docs    | yes             |
| Docs    | streaming/observability, queue, lifecycle, architecture | yes             |

## Work Plan

### Implementation

- [x] Definir y validar el contexto común de correlación.
- [x] Instrumentar lifecycle de jobs y scheduler RQ.
- [x] Instrumentar adaptadores OpenAI, Gemini y Mock.

### Tests and Documentation

- [x] Add or update tests with the behavior change.
- [x] Review all documentation surfaces required by `AGENTS.md`.
- [x] Update canonical documents affected by the code diff.

### Validation

- [x] Pruebas focalizadas de observabilidad, jobs, RQ y proveedores.
- [x] `python -m pytest backend/tests`
- [x] Cobertura backend 100%.
- [x] `pre-commit run --all-files`.

## Progress Log

| Date       | State       | Completed                                             | Pending / next safe action     |
| ---------- | ----------- | ----------------------------------------------------- | ------------------------------ |
| 2026-07-25 | En progreso | Inventario, límites de confianza y alcance definidos  | Implementar contexto y eventos |
| 2026-07-25 | Hecho       | Correlación, redacción, pruebas y documentos cerrados | Sin trabajo pendiente          |

## Validation Results

| Date       | Command                                                                                                | Result | Notes                                   |
| ---------- | ------------------------------------------------------------------------------------------------------ | ------ | --------------------------------------- |
| 2026-07-25 | Pruebas focalizadas de observabilidad, middleware, AIJob, RQ, proveedores y docs                       | Passed | 97 pruebas                              |
| 2026-07-25 | Pruebas focalizadas tras serializar campos string de log                                               | Passed | 62 pruebas                              |
| 2026-07-25 | `python -m pytest backend/tests --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=100` | Passed | 496 pruebas; cobertura total 100%       |
| 2026-07-25 | `pre-commit run --all-files`                                                                           | Passed | Todos los hooks pasan tras autoformateo |

## Pause / Handoff Record

- Current state: recorrido correlacionado y seguro disponible en todas las capas existentes.
- Changed files and contracts: observability helper, request middleware, AI jobs, RQ, proveedores,
  pruebas, operación, arquitectura, foundation status y tracking.
- Pending work: ninguno dentro de OBS-001.
- Blockers or approvals: ninguno.
- Residual risks: no existe handler funcional; el primero debe cumplir el contrato probado de
  recuperar el par desde `AIJob`.
- Next safe action: continuar con `TEST-AI-001` y reutilizar estos eventos en cada escenario de fallo.

## Completion Documentation Review

- [x] Root and service READMEs reviewed.
- [x] Backend operation and architecture docs reviewed.
- [x] Frontend operation docs and inventories reviewed.
- [x] Foundation status files reviewed and changed only if a foundation contract moved.
- [x] AI governance docs, templates, and checklists reviewed.
- [x] Item plan and summary backlog synchronized.

Record documents intentionally unchanged and why:

- Root/backend READMEs: sin cambio; no hay servicio, dependencia, endpoint ni configuración nueva.
- API/auth/RBAC/OpenAPI: error mapping se actualizó por validación de `X-Request-ID`; no cambian
  rutas, permisos ni schemas.
- Frontend: sin cambio; `X-Request-ID` sigue siendo el mismo header público.
- Backend operations/architecture: lifecycle, queue, streaming y ports/adapters actualizados.
- Foundation status: actualizado porque la correlación es un contrato transversal.
- AI governance: proceso sin cambio; backlog e índices sincronizados.

## Completion Summary

- Delivered: contexto validado, IDs seguros, eventos correlacionados en AIJob/RQ/proveedores/stream,
  duración y errores normalizados, payload Redis intacto y campos string serializados contra
  inyección.
- Validation: 496 pruebas backend con cobertura 100%, pruebas focalizadas y pre-commit completo.
- Skipped validation: handler y proveedor real; no existe función IA de producto y las pruebas usan
  RQ/transportes inyectados y Mock para no enviar datos externos.
- Human approvals: not applicable.
- Residual risk: el primer handler funcional debe cargar `AIJob` por alcance de tenant antes de
  construir `AiTextRequest`; el contrato y la prueba integrada ya fijan esa obligación.
