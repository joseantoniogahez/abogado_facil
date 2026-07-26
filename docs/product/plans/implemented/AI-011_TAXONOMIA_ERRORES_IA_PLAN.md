# AI-011 - Taxonomía normalizada de errores de IA

## Tracking Status

- ID: `AI-011`
- Type: Backend
- Priority: P1
- Plan status: Complete
- Implementation status: Hecho
- Last updated: 2026-07-25
- Backlog source: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objective

Normalizar los fallos de OpenAI, Gemini y Mock a códigos cerrados, seguros y accionables, para que
los workers persistan un `error_code` estable y futuros consumidores frontend puedan mostrar un
mensaje común sin recibir detalles, cuerpos ni credenciales del proveedor.

## Starting Point

`AiProviderError` sólo conserva un mensaje y el indicador `retryable`. Los adaptadores distinguen
entre errores HTTP recuperables y no recuperables, pero no entre autenticación, rate limit,
timeout, indisponibilidad, solicitud rechazada o respuesta inválida. `AIJob` ya puede persistir un
`error_code` seguro.

## Scope

### Included

- Catálogo cerrado de códigos y mensajes públicos independientes del proveedor.
- Mapeo común de estados HTTP y fallos de transporte para OpenAI y Gemini.
- Fallos deterministas configurables en Mock bajo el mismo contrato.
- Propiedades explícitas para retry y persistencia en `AIJob`.
- Pruebas de contrato, seguridad y paridad multi-provider.
- Documentación de arquitectura, operación y catálogo.

### Excluded

- Endpoint o pantalla de ejecución de IA.
- Parsing de cuerpos de error externos.
- Handler RQ de una función de producto.
- Observabilidad correlacionada y métricas agregadas.
- Validación de JSON/schema de resultados.

## Dependencies and Decisions

- Dependencies: `AI-003`, `AI-009` y `AI-010`.
- Decisions closed: el estado HTTP decide el código sin inspeccionar cuerpos externos; los mensajes
  públicos son constantes; sólo rate limit, timeout e indisponibilidad son recuperables.
- Open questions: ninguna.

## Acceptance Criteria

- [x] OpenAI, Gemini y Mock emiten el mismo tipo y catálogo de error.
- [x] Autenticación, rate limit, timeout, indisponibilidad, rechazo e invalid response tienen códigos
  estables.
- [x] Cada error declara explícitamente si es recuperable.
- [x] El código es válido para persistirse directamente en `AIJob.error_code`.
- [x] Mensajes, representaciones y contratos públicos no contienen claves, URLs, cuerpos o detalles
  externos.
- [x] Required documentation is synchronized with delivered behavior.
- [x] Required validation gates pass and are recorded below.
- [x] Mandatory human approvals are recorded, or explicitly not applicable.

## Affected Contracts and Files

| Surface | Expected files or contracts                                 | Change required |
| ------- | ----------------------------------------------------------- | --------------- |
| Runtime | `app/integrations/ai_providers.py`, AI job error code       | yes             |
| Tests   | provider contracts, AI job compatibility, docs contracts    | yes             |
| Docs    | error mapping, AI job lifecycle, ports/adapters, AI catalog | yes             |

## Work Plan

### Implementation

- [x] Definir catálogo, metadatos seguros y mapeo HTTP/transporte.
- [x] Aplicar el contrato a OpenAI, Gemini y Mock.
- [x] Verificar compatibilidad con `AIJob.error_code`.

### Tests and Documentation

- [x] Add or update tests with the behavior change.
- [x] Review all documentation surfaces required by `AGENTS.md`.
- [x] Update canonical documents affected by the code diff.

### Validation

- [x] Pruebas focalizadas de proveedores y ciclo de jobs.
- [x] `python -m pytest backend/tests`
- [x] Cobertura backend 100%.
- [x] `pre-commit run --all-files`.

## Progress Log

| Date       | State       | Completed                                                | Pending / next safe action             |
| ---------- | ----------- | -------------------------------------------------------- | -------------------------------------- |
| 2026-07-25 | En progreso | Alcance, catálogo y fuentes oficiales revisados          | Implementar contrato y pruebas focales |
| 2026-07-25 | Hecho       | Taxonomía, adaptadores, pruebas y documentación cerrados | Sin trabajo pendiente                  |

## Validation Results

| Date       | Command                                                                                                | Result | Notes                                                  |
| ---------- | ------------------------------------------------------------------------------------------------------ | ------ | ------------------------------------------------------ |
| 2026-07-25 | Documentación oficial de errores OpenAI y Gemini                                                       | Passed | Estados de auth, rate limit y transitorios verificados |
| 2026-07-25 | Pruebas focalizadas de proveedores, AIJob y docs con coverage                                          | Passed | 55 pruebas; módulo de proveedores al 100%              |
| 2026-07-25 | `python -m pytest backend/tests --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=100` | Passed | 490 pruebas; cobertura total 100%                      |
| 2026-07-25 | `pre-commit run --all-files`                                                                           | Passed | Todos los hooks pasan tras autoformateo                |

## Pause / Handoff Record

- Current state: taxonomía cerrada y contrato público seguro implementados y validados.
- Changed files and contracts: adaptadores IA, pruebas, catálogo operativo, arquitectura,
  lifecycle, error mapping, foundation status y tracking.
- Pending work: ninguno dentro de AI-011.
- Blockers or approvals: ninguno.
- Residual risks: algunos estados 4xx pueden tener varias causas; se clasifican sin leer cuerpos
  externos para mantener el límite de confianza.
- Next safe action: continuar con `OBS-001`; los handlers funcionales futuros deben persistir
  `AiProviderError.error_code`.

## Completion Documentation Review

- [x] Root and service READMEs reviewed.
- [x] Backend operation and architecture docs reviewed.
- [x] Frontend operation docs and inventories reviewed.
- [x] Foundation status files reviewed and changed only if a foundation contract moved.
- [x] AI governance docs, templates, and checklists reviewed.
- [x] Item plan and summary backlog synchronized.

Record documents intentionally unchanged and why:

- Root/backend READMEs: el índice backend se actualizó; los READMEs de operación no cambian porque
  no hay servicio, configuración ni endpoint nuevo.
- API/auth/RBAC/OpenAPI: sin cambio; no se añadió superficie HTTP ni permiso.
- Frontend: sin cambio; todavía no existe un consumidor de ejecución IA.
- Foundation status: actualizado porque el catálogo es un contrato compartido de integración.
- AI governance: sin cambio de proceso; backlog e índices de planes sincronizados.

## Completion Summary

- Delivered: catálogo cerrado, mensajes públicos constantes, retry explícito, traducción común para
  OpenAI/Gemini y fallos deterministas en Mock, compatible con `AIJob.error_code`.
- Validation: 490 pruebas backend con cobertura 100% y pre-commit completo.
- Skipped validation: llamadas reales a proveedores; los adaptadores se validan mediante transporte
  inyectable y no deben usar credenciales externas en tests.
- Human approvals: not applicable.
- Residual risk: el mapeo por estado sacrifica detalle diagnóstico deliberadamente; observabilidad
  interna segura y correlacionada corresponde a `OBS-001`.
