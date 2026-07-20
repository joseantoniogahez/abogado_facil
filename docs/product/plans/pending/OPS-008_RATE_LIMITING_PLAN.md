# OPS-008 - Rate limiting para superficies sensibles

## Tracking Status

- ID: `OPS-008`
- Type: `Backend`
- Priority: `P1`
- Plan status: `Ready`
- Implementation status: `Identificado`
- Last updated: `2026-07-19`
- Backlog source: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objective

Proteger autenticación, registro, uploads y futuras llamadas IA contra abuso, fuerza bruta y costos
no controlados.

## Starting Point

No se encontró una política de rate limiting explícita en el backend actual.

## Scope

### Included

- Límites configurables por entorno y superficie sensible.
- Respuesta normalizada, headers útiles y estrategia compatible con múltiples workers.
- Tests de límite, recuperación y comportamiento local.

### Excluded

- Elegir proveedor gestionado de producción sin decisión separada.
- Limitar indiscriminadamente endpoints internos o health checks.

## Dependencies and Decisions

- Dependencies: `AUDIT-001`, decisión de almacenamiento de contadores.
- Decisions closed: no depender de memoria de proceso para producción multi-worker.
- Open questions: Redis u otro backend compartido.

## Acceptance Criteria

- [ ] Login, registro y uploads tienen límites definidos.
- [ ] La respuesta excedida usa el contrato de errores y no filtra secretos.
- [ ] Tests cubren límites y bypasses obvios.
- [ ] Dependencia nueva, si existe, está aprobada y auditada.

## Affected Contracts and Files

| Surface | Expected files or contracts                     | Change required |
| ------- | ----------------------------------------------- | --------------- |
| Runtime | middleware/dependencies, settings, integrations | yes             |
| Tests   | security/router/config tests                    | yes             |
| Docs    | API/error/runtime/dependency docs               | yes             |

## Work Plan

- [ ] Medir superficies y elegir estrategia.
- [ ] Implementar límites y configuración.
- [ ] Probar abuso, autenticación y workers.

## Validation

- [ ] `python -m pytest backend/tests`
- [ ] coverage gate backend
- [ ] dependency audit y pre-commit si se añade dependencia

## Progress Log

| Date       | State         | Completed                                 | Pending / next safe action           |
| ---------- | ------------- | ----------------------------------------- | ------------------------------------ |
| 2026-07-19 | Plan prepared | Scope and provider decision gate recorded | Wait for audit and provider decision |

## Validation Results

No ejecutadas: ticket no iniciado.

## Pause / Handoff Record

- Current state: plan listo.
- Pending work: estrategia compartida, implementación y tests.
- Blockers or approvals: provider/infraestructura para producción.
- Residual risks: abuso y fuerza bruta sin límite.
- Next safe action: iniciar después de `AUDIT-001`.

## Completion Summary

- Delivered: pendiente.
- Validation: pendiente.
- Residual risk: pendiente.
