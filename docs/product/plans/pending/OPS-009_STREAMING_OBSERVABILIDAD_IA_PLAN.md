# OPS-009 - Streaming y observabilidad para IA

## Tracking Status

- ID: `OPS-009`
- Type: `Backend`
- Priority: `P1`
- Plan status: `Ready`
- Implementation status: `Identificado`
- Last updated: `2026-07-19`
- Backlog source: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objective

Dejar un patrón seguro y probado para respuestas progresivas de IA y correlación operativa sin
exponer información legal sensible.

## Starting Point

El backend usa `StreamingResponse` para descargas, tiene `request_id` y logging HTTP, pero aún no
define streaming de resultados IA, cancelación, eventos ni métricas de proveedor.

## Scope

### Included

- Elegir SSE o streaming JSON Lines según consumidores.
- Definir cancelación, errores, heartbeat y correlación.
- Registrar latencia, errores y estados sin prompts, documentos ni credenciales.

### Excluded

- Implementar un proveedor LLM.
- Crear funciones de IA de Fase 2.

## Dependencies and Decisions

- Dependencies: `AUDIT-001`, observabilidad existente y contratos futuros AI.
- Decisions closed: no datos sensibles en logs ni eventos.
- Open questions: consumidor frontend y formato final de eventos.

## Acceptance Criteria

- [ ] Patrón de streaming cancelable documentado y probado.
- [ ] Errores y finalización tienen contrato estable.
- [ ] Métricas/logs correlacionan request y ejecución sin contenido sensible.
- [ ] OpenAPI/frontend quedan sincronizados si se publica una ruta.

## Affected Contracts and Files

| Surface | Expected files or contracts                  | Change required |
| ------- | -------------------------------------------- | --------------- |
| Runtime | response/integration/observability modules   | yes             |
| Tests   | streaming, cancellation, observability tests | yes             |
| Docs    | API, observability, runtime error docs       | yes             |

## Work Plan

- [ ] Definir formato de evento y lifecycle.
- [ ] Implementar ejemplo/patrón reusable.
- [ ] Añadir pruebas de cancelación, fallo y redacción de datos.

## Validation

- [ ] `python -m pytest backend/tests`
- [ ] `npm --prefix frontend run openapi:sync` si cambia la API
- [ ] pre-commit sobre archivos modificados

## Progress Log

| Date       | State         | Completed                                    | Pending / next safe action        |
| ---------- | ------------- | -------------------------------------------- | --------------------------------- |
| 2026-07-19 | Plan prepared | Scope separated from provider implementation | Define event contract after audit |

## Validation Results

No ejecutadas: ticket no iniciado.

## Pause / Handoff Record

- Current state: plan listo.
- Pending work: contrato, patrón, pruebas y docs.
- Blockers or approvals: consumidor y formato de eventos.
- Residual risks: futuras respuestas IA podrían ser bloqueantes o difíciles de diagnosticar.
- Next safe action: iniciar después de `AUDIT-001`.

## Completion Summary

- Delivered: pendiente.
- Validation: pendiente.
- Residual risk: pendiente.
