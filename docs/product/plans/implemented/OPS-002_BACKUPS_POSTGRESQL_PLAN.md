# OPS-002 - Backups básicos de PostgreSQL

## Tracking Status

- ID: `OPS-002`
- Type: `Ops`
- Priority: `P1`
- Plan status: `Complete`
- Implementation status: `Hecho`
- Last updated: `2026-08-01`

## Objective

Definir un procedimiento reproducible y verificable de backup y restauración de PostgreSQL antes
del despliegue productivo.

## Acceptance Criteria

- [x] El procedimiento usa `pg_dump` custom, permisos restrictivos y credenciales internas del contenedor.
- [x] Incluye copia fuera del host, cifrado, retención y limpieza temporal.
- [x] Incluye verificación de archivo y simulacro de restauración en una base aislada.
- [x] Define evidencia mínima, frecuencia, responsables y relación con eliminación de datos.
- [x] Documentación e índices pasan sus gates.

## Progress Log

| Date       | State       | Completed                                          | Pending / next safe action     |
| ---------- | ----------- | -------------------------------------------------- | ------------------------------ |
| 2026-08-01 | En progreso | Alcance operativo definido.                        | Redactar y validar el runbook. |
| 2026-08-01 | Hecho       | Runbook, índices y enlace de despliegue completos. | Ninguna.                       |

## Validation Results

| Date       | Validation                 | Result | Notes                                           |
| ---------- | -------------------------- | ------ | ----------------------------------------------- |
| 2026-08-01 | `docker compose config -q` | Pass   | Perfil base resolvió correctamente.             |
| 2026-08-01 | Revisión del runbook       | Pass   | Backup, checksum, restore y limpieza cubiertos. |

## Pause / Handoff Record

- Current state: completo.
- Pending work: ninguno dentro del ticket documental.
- Blockers or approvals: ninguno.
- Next safe action: ejecutar el primer backup y restore drill al preparar un ambiente productivo.

## Completion Summary

- Delivered: runbook reproducible de backup, cifrado, retención, evidencia y restore aislado.
- Validation: configuración Compose válida y contrato documental revisado.
- Skipped validation: no se ejecutó un dump productivo porque no se proporcionó un ambiente productivo.
- Residual risk: el operador debe coordinar por separado backups de objetos S3/MinIO.
