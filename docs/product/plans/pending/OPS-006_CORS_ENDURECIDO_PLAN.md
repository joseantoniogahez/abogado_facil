# OPS-006 - CORS endurecido

## Tracking Status

- ID: `OPS-006`
- Type: `Backend`
- Priority: `P1`
- Plan status: `Ready`
- Implementation status: `Identificado`
- Last updated: `2026-07-19`
- Backlog source: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objective

Reducir la superficie de CORS mediante una política explícita y segura por entorno.

## Starting Point

`configure_cors` permite todos los métodos y headers cuando existen orígenes configurados, además
de credenciales.

## Scope

### Included

- Configurar métodos y headers permitidos explícitamente.
- Validar compatibilidad con frontend, preflight y credenciales.
- Documentar variables y política.

### Excluded

- Cambiar autenticación JWT.
- Resolver políticas del reverse proxy fuera del backend.

## Dependencies and Decisions

- Dependencies: `AUDIT-001`, frontend runtime config.
- Decisions closed: no usar comodines innecesarios en producción.
- Open questions: lista final de orígenes productivos.

## Acceptance Criteria

- [ ] CORS productivo rechaza orígenes no permitidos.
- [ ] Preflight y requests autorizados funcionan.
- [ ] Tests cubren configuración segura y documentación actualizada.

## Affected Contracts and Files

| Surface | Expected files or contracts                | Change required |
| ------- | ------------------------------------------ | --------------- |
| Runtime | `backend/app/core/setup/cors.py`, settings | yes             |
| Tests   | CORS/factory tests                         | yes             |
| Docs    | runtime/browser security docs              | yes             |

## Work Plan

- [ ] Inventariar consumidores y orígenes.
- [ ] Implementar política explícita.
- [ ] Añadir pruebas y actualizar contratos.

## Validation

- [ ] `python -m pytest backend/tests`
- [ ] `npm --prefix frontend run check` si cambia el contrato de runtime
- [ ] pre-commit sobre archivos modificados

## Progress Log

| Date       | State         | Completed      | Pending / next safe action                |
| ---------- | ------------- | -------------- | ----------------------------------------- |
| 2026-07-19 | Plan prepared | Scope recorded | Wait for `AUDIT-001` and origin inventory |

## Validation Results

No ejecutadas: ticket no iniciado.

## Pause / Handoff Record

- Current state: plan listo.
- Pending work: política, tests y docs.
- Blockers or approvals: orígenes productivos.
- Residual risks: CORS demasiado permisivo.
- Next safe action: iniciar después de `AUDIT-001`.

## Completion Summary

- Delivered: pendiente.
- Validation: pendiente.
- Residual risk: pendiente.
