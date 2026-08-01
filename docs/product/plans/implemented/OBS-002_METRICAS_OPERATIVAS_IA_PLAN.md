# OBS-002 - Métricas operativas de IA

## Tracking Status

- ID: `OBS-002`
- Type: `Ops`
- Priority: `P1`
- Plan status: `Complete`
- Implementation status: `Hecho`
- Last updated: `2026-08-01`
- Backlog source: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objective

Entregar un dashboard reproducible y aislado por despacho con éxito, errores, latencia, tokens,
costo, reintentos y jobs atascados.

## Starting Point

Existen métricas de proveedor locales al proceso y `AIJob` persistente, pero no hay consulta
histórica ni UI. `AIJob` no conserva duración ni estimaciones de uso/costo.

## Scope

### Included

- Persistir telemetría operativa content-free por job.
- Agregar métricas por despacho y exponerlas mediante API autenticada.
- Mostrar métricas, cobertura de costo y jobs atascados en una pantalla reproducible.

### Excluded

- Prompts, contenido legal o secretos en telemetría.
- Facturación del proveedor o precios externos inferidos.

## Dependencies and Decisions

- Dependencies: `AI-006`, `AI-009`, `OBS-001`.
- Decisions closed: tokens estimados de forma determinista; costo nullable y cobertura explícita.
- Open questions: none.

## Acceptance Criteria

- [x] Dashboard aislado por `firm_id` informa éxito, errores, latencia, tokens, cobertura de costo, reintentos y jobs atascados.
- [x] No se persiste contenido sensible.
- [x] Required documentation is synchronized with delivered behavior.
- [x] Required validation gates pass and are recorded below.
- [x] Mandatory human approvals are not applicable.

## Work Plan

- [ ] Extender telemetría persistente de `AIJob` y migración.
- [ ] Crear agregación/API firm-scoped y UI.
- [ ] Añadir pruebas backend/frontend y sincronizar contratos/documentación.
- [ ] Ejecutar gates full-stack.

## Progress Log

| Date       | State       | Completed                         | Pending / next safe action |
| ---------- | ----------- | --------------------------------- | -------------------------- |
| 2026-08-01 | En progreso | Alcance y decisiones formalizados | Implementar persistencia   |

## Validation Results

| Date       | Command               | Result | Notes                             |
| ---------- | --------------------- | ------ | --------------------------------- |
| 2026-08-01 | Backend coverage gate | Pass   | 609 passed, 100%                  |
| 2026-08-01 | Frontend check/build  | Pass   | Contratos, UI y budgets validados |

## Pause / Handoff Record

- Current state: plan activo.
- Changed files and contracts: plan y backlog.
- Pending work: implementación completa.
- Next safe action: extender `AIJob` y agregar el slice `ai_insights`.
