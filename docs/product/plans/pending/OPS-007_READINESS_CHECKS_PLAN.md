# OPS-007 - Health y readiness checks

## Tracking Status

- ID: `OPS-007`
- Type: `Backend`
- Priority: `P1`
- Plan status: `Ready`
- Implementation status: `Identificado`
- Last updated: `2026-07-19`
- Backlog source: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objective

Separar la señal de proceso vivo de la capacidad real de aceptar tráfico dependiente de base de
datos y object storage.

## Starting Point

Existe `/v1/health` como endpoint público, pero no se ha definido una comprobación de readiness
operativa de dependencias.

## Scope

### Included

- Mantener liveness barato y sin secretos.
- Añadir readiness con timeouts y respuesta segura.
- Documentar uso en Compose/despliegue y probar fallos.

### Excluded

- Crear un sistema de monitoreo externo.
- Ejecutar operaciones destructivas durante checks.

## Dependencies and Decisions

- Dependencies: `AUDIT-001`, DB and storage ports.
- Decisions closed: readiness no debe bloquear indefinidamente ni filtrar detalles internos.
- Open questions: status code exacto para dependencia no disponible.

## Acceptance Criteria

- [ ] Liveness y readiness tienen contratos separados.
- [ ] Fallos de DB/storage se reflejan de forma determinista y segura.
- [ ] Docker/deployment docs y tests quedan sincronizados.

## Affected Contracts and Files

| Surface | Expected files or contracts                           | Change required |
| ------- | ----------------------------------------------------- | --------------- |
| Runtime | health feature, DB/storage ports, router registration | yes             |
| Tests   | health/router/integration tests                       | yes             |
| Docs    | API endpoints and deployment docs                     | yes             |

## Work Plan

- [ ] Definir contrato y timeout.
- [ ] Implementar checks mediante puertos existentes.
- [ ] Añadir tests de éxito y fallo.

## Validation

- [ ] `python -m pytest backend/tests`
- [ ] coverage gate backend
- [ ] pre-commit sobre archivos modificados

## Progress Log

| Date       | State         | Completed      | Pending / next safe action            |
| ---------- | ------------- | -------------- | ------------------------------------- |
| 2026-07-19 | Plan prepared | Scope recorded | Define readiness contract after audit |

## Validation Results

No ejecutadas: ticket no iniciado.

## Pause / Handoff Record

- Current state: plan listo.
- Pending work: contrato, implementación y pruebas.
- Blockers or approvals: status code y dependencia productiva.
- Residual risks: despliegue puede enviar tráfico antes de estar listo.
- Next safe action: iniciar después de `AUDIT-001`.

## Completion Summary

- Delivered: pendiente.
- Validation: pendiente.
- Residual risk: pendiente.
