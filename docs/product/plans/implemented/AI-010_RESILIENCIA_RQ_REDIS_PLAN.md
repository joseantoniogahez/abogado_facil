# AI-010 - Resiliencia de proveedores con RQ y Redis

## Tracking Status

- ID: `AI-010`
- Type: Backend
- Priority: P1
- Plan status: Complete
- Implementation status: Hecho
- Last updated: 2026-07-25
- Backlog source: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objective

Disponer de una cola RQ sobre el Redis existente para ejecutar funciones IA fuera del proceso web,
con timeout, retries recuperables, backoff, límite de concurrencia e idempotencia, conservando
PostgreSQL/`AIJob` como fuente de verdad.

## Starting Point

`AI-009` ya entrega el ciclo persistente de `AIJob`; existe Redis para rate limiting y un
`JobSchedulerPort`, pero no hay adaptador RQ, worker, configuración de cola ni dependencia RQ.

## Scope

### Included

- RQ 2.10 sobre Redis con serializer JSON.
- Adaptador del `JobSchedulerPort` con catálogo explícito de handlers.
- Payload de Redis limitado al `execution_id`.
- `job_id` determinista, `unique=True`, timeout, TTL y retries con backoff.
- Concurrencia inicial limitada a un worker; escala explícita y cuota distribuida diferida hasta
  existir un handler de proveedor.
- Configuración validada, DI y servicio worker en Compose con scheduler.
- Pruebas sin Redis externo y documentación operativa/de seguridad.

### Excluded

- Primer handler funcional de producto (`AI-101`).
- Persistencia de prompts o contexto en Redis.
- Taxonomía completa de errores (`AI-011`).
- Correlación y métricas agregadas (`OBS-001`, `AI-006`, `OBS-002`).
- Dashboard de RQ o dependencia adicional de monitoreo.

## Dependencies and Decisions

- Dependencies: `AI-009`, Redis y el puerto `JobSchedulerPort`.
- Decisions closed: RQ 2.10; JSON en lugar de pickle; PostgreSQL es fuente de verdad; Redis sólo
  transporta identificadores; worker usa scheduler para backoff diferido.
- Open questions: ninguna.

## Acceptance Criteria

- [x] El scheduler encola únicamente handlers permitidos y un `execution_id` válido.
- [x] Un mismo `execution_id` no genera trabajos duplicados.
- [x] Timeout, retries, backoff y TTL son configurables y validados; Compose limita inicialmente la
  concurrencia a un worker.
- [x] Productor y worker usan el mismo serializer JSON.
- [x] Redis no recibe prompts, credenciales, texto documental ni resultados.
- [x] Compose incluye un worker saludable respecto a Redis y separado del proceso web.
- [x] Pruebas cubren política de enqueue, duplicados, configuración inválida y errores seguros.
- [x] Required documentation is synchronized with delivered behavior.
- [x] Required validation gates pass and are recorded below.
- [x] Mandatory human approvals are recorded, or explicitly not applicable.

## Affected Contracts and Files

| Surface | Expected files or contracts                            | Change required |
| ------- | ------------------------------------------------------ | --------------- |
| Runtime | settings, integrations/jobs, DI, requirements, Compose | yes             |
| Tests   | config, adapter, DI, documentation contracts           | yes             |
| Docs    | README, architecture, operations, backlog plan         | yes             |

## Work Plan

### Implementation

- [x] Extender el comando y puerto de jobs con contrato seguro.
- [x] Implementar el adaptador RQ y su configuración validada.
- [x] Cablear DI y worker RQ en Compose.

### Tests and Documentation

- [x] Add or update tests with the behavior change.
- [x] Review all documentation surfaces required by `AGENTS.md`.
- [x] Update canonical documents affected by the code diff.

### Validation

- [x] Pruebas focalizadas de configuración, integración y DI.
- [x] `docker compose config` y variantes test/prod.
- [x] `python -m pytest backend/tests`
- [x] Cobertura backend 100%.
- [x] `pre-commit run --all-files`.

## Progress Log

| Date       | State       | Completed                                                                   | Pending / next safe action            |
| ---------- | ----------- | --------------------------------------------------------------------------- | ------------------------------------- |
| 2026-07-25 | En progreso | RQ/Redis, JSON, idempotencia y fronteras de datos definidos                 | Implementar configuración y adaptador |
| 2026-07-25 | Hecho       | Adaptador, configuración, worker Compose, pruebas y contratos sincronizados | Sin trabajo pendiente en AI-010       |

## Validation Results

| Date       | Command                                                                                                | Result | Notes                                                                                                                |
| ---------- | ------------------------------------------------------------------------------------------------------ | ------ | -------------------------------------------------------------------------------------------------------------------- |
| 2026-07-25 | Consulta de documentación oficial RQ/PyPI                                                              | Passed | RQ 2.10.0, `unique`, `Retry`, scheduler y serializer JSON confirmados; `RateLimit` no existe en el paquete publicado |
| 2026-07-25 | Pruebas focalizadas de configuración, integración, DI y CLI config                                     | Passed | 22 pruebas                                                                                                           |
| 2026-07-25 | Compose base, test y prod `config -q`                                                                  | Passed | Las tres variantes son válidas                                                                                       |
| 2026-07-25 | `pre-commit run --all-files`                                                                           | Passed | Todos los hooks pasan                                                                                                |
| 2026-07-25 | `python -m pytest backend/tests --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=100` | Passed | 465 pruebas, cobertura 100%                                                                                          |
| 2026-07-25 | `docker compose build ai-worker`                                                                       | Passed | Imagen Python 3.14 con RQ 2.10.0 construida                                                                          |
| 2026-07-25 | `docker compose up -d redis database ai-worker` + estado/logs                                          | Passed | Worker saludable, cola `ai`, scheduler activo y migraciones al día                                                   |

## Pause / Handoff Record

- Current state: transporte RQ/Redis implementado y validado en contenedor real.
- Changed files and contracts: settings, comando/puerto, adaptador RQ, CLI config, DI, requirements,
  Compose/env, READMEs, arquitectura, operación, foundation status y pruebas.
- Pending work: ninguno dentro de AI-010.
- Blockers or approvals: ninguno.
- Residual risks: el catálogo productivo está vacío hasta el primer handler; la cuota distribuida
  por proveedor debe implementarse junto al handler porque RQ 2.10.0 no publica `RateLimit`.
- Next safe action: continuar con AI-011 y registrar handlers sólo desde tickets funcionales.

## Completion Documentation Review

- [x] Root and service READMEs reviewed.
- [x] Backend operation and architecture docs reviewed.
- [x] Frontend operation docs and inventories reviewed.
- [x] Foundation status files reviewed and changed only if a foundation contract moved.
- [x] AI governance docs, templates, and checklists reviewed.
- [x] Item plan and summary backlog synchronized.

Record documents intentionally unchanged and why:

- Root/backend READMEs: actualizados con servicio y configuración.
- API/auth/RBAC/OpenAPI: sin cambio; no se añadió endpoint ni permiso.
- Frontend: sin cambio; no existe consumidor.
- Foundation status: actualizado porque se añadió un contrato de infraestructura compartida.

## Completion Summary

- Delivered: adaptador RQ/Redis seguro e idempotente, configuración validada, retries con backoff,
  timeout/TTL y worker Compose separado con scheduler y serializer JSON.
- Validation: 465 pruebas con cobertura 100%, pre-commit, tres variantes Compose y arranque real del
  worker saludable.
- Skipped validation: ejecución de un handler real; no existe todavía por alcance.
- Human approvals: not applicable.
- Residual risk: catálogo sin handlers y cuota distribuida por proveedor diferida hasta la primera
  función IA.
