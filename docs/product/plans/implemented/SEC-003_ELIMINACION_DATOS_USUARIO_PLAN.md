# SEC-003 - Eliminación de datos del usuario

## Tracking Status

- ID: `SEC-003`
- Type: `Backend`
- Priority: `P1`
- Plan status: `Complete`
- Implementation status: `Hecho`
- Last updated: `2026-08-01`
- Backlog source: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objective

Permitir que un usuario elimine definitivamente documentos individuales y asuntos completos de su
despacho, con aislamiento tenant y limpieza de los datos dependientes.

## Scope

### Included

- Conservar la eliminación individual de documentos existente.
- Añadir eliminación definitiva de asuntos propios.
- Eliminar objetos almacenados y registros dependientes del asunto.
- Mantener `404` opaco para asuntos inexistentes o ajenos.
- Documentar la política y cubrirla con pruebas.

### Excluded

- Borrado de cuenta, despacho o cliente.
- Papelera, recuperación, retención legal o borrado diferido.
- Purga retroactiva de copias de seguridad; se documentará en `OPS-002`.

## Acceptance Criteria

- [x] `DELETE /v1/matters/{matter_id}` elimina un asunto propio y devuelve `204`.
- [x] Los objetos documentales del asunto se eliminan antes de borrar sus metadatos.
- [x] Notas, tareas, pagos, cálculos, checklist, documentos y resultados IA se eliminan en cascada.
- [x] Un asunto inexistente o ajeno devuelve el mismo `404` opaco.
- [x] Pruebas, migración y documentación pasan los gates backend.

## Work Plan

- [x] Definir cascadas de base de datos y migración reversible.
- [x] Implementar servicio, DI, endpoint y contrato OpenAPI.
- [x] Añadir pruebas de servicio, router, persistencia y aislamiento.
- [x] Actualizar documentación y ejecutar validaciones.

## Progress Log

| Date       | State       | Completed                                                    | Pending / next safe action                |
| ---------- | ----------- | ------------------------------------------------------------ | ----------------------------------------- |
| 2026-08-01 | En progreso | Política y alcance de eliminación establecidos.              | Implementar cascadas, endpoint y pruebas. |
| 2026-08-01 | Hecho       | Endpoint, cascadas, limpieza, pruebas y contratos completos. | Ninguna.                                  |

## Validation Results

| Date       | Command                                                                                                | Result | Notes                         |
| ---------- | ------------------------------------------------------------------------------------------------------ | ------ | ----------------------------- |
| 2026-08-01 | `python -m pytest backend/tests`                                                                       | Pass   | 602 pruebas.                  |
| 2026-08-01 | `python -m pytest backend/tests --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=100` | Pass   | 602 pruebas; cobertura 100 %. |
| 2026-08-01 | `npm --prefix frontend run openapi:check`                                                              | Pass   | Artefacto sincronizado.       |
| 2026-08-01 | Migración SQLite `upgrade head` y downgrade a revisión anterior                                        | Pass   | Migración reversible.         |

## Pause / Handoff Record

- Current state: completo.
- Pending work: ninguno.
- Blockers or approvals: ninguno.
- Residual risks: una política de retención legal futura puede requerir borrado diferido.
- Next safe action: continuar con `OPS-001`.

## Completion Summary

- Delivered: eliminación definitiva tenant-scoped de asuntos, objetos y datos dependientes.
- Validation: backend 602 pruebas y cobertura 100 %, OpenAPI sincronizado y migración reversible.
- Skipped validation: frontend check/build/e2e; no cambió comportamiento de UI o rutas frontend.
- Residual risk: no existe papelera; backups pueden conservar datos hasta expirar según `OPS-002`.
