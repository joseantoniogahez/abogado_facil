# OPS-001 - Límites configurables de archivos y análisis

## Tracking Status

- ID: `OPS-001`
- Type: `Ops`
- Priority: `P1`
- Plan status: `Complete`
- Implementation status: `Hecho`
- Last updated: `2026-08-01`

## Objective

Centralizar en configuración validada los límites operativos de archivos, entrada IA y salida IA.

## Scope

- Conservar `MATTER_DOCUMENT_MAX_SIZE_BYTES` y `MATTER_DOCUMENT_MAX_PER_MATTER`.
- Añadir límites configurables para narrativa IA, campos de borradores y tokens máximos de salida.
- Aplicar los límites en preview y ejecución, documentarlos y exponerlos en Compose.
- No añadir cuotas comerciales, rate limiting ni límites por plan.

## Acceptance Criteria

- [x] Tamaño y número de documentos se controlan mediante configuración validada.
- [x] Entrada y salida IA se controlan mediante configuración validada.
- [x] Preview y ejecución comparten los mismos límites efectivos.
- [x] Configuración, servicios y errores límite tienen pruebas.
- [x] Documentación y gates backend/OpenAPI pasan.

## Progress Log

| Date       | State       | Completed                                                  | Pending / next safe action             |
| ---------- | ----------- | ---------------------------------------------------------- | -------------------------------------- |
| 2026-08-01 | En progreso | Inventario de límites actuales cerrado.                    | Implementar configuración e inyección. |
| 2026-08-01 | Hecho       | Configuración, Compose, pruebas y documentación completos. | Ninguna.                               |

## Validation Results

| Date       | Command                                                                                                | Result | Notes                         |
| ---------- | ------------------------------------------------------------------------------------------------------ | ------ | ----------------------------- |
| 2026-08-01 | Pruebas dirigidas de configuración y servicios                                                         | Pass   | 26 pruebas.                   |
| 2026-08-01 | `python -m pytest backend/tests --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=100` | Pass   | 605 pruebas; cobertura 100 %. |
| 2026-08-01 | `npm --prefix frontend run openapi:check`                                                              | Pass   | Sin drift.                    |
| 2026-08-01 | `docker compose config -q`                                                                             | Pass   | Configuración válida.         |

## Pause / Handoff Record

- Current state: completo.
- Pending work: ninguno.
- Blockers or approvals: ninguno.
- Next safe action: continuar con `OPS-002`.

## Completion Summary

- Delivered: límites de archivos, entradas IA, campos documentales y tokens controlados por entorno.
- Validation: 605 pruebas backend, cobertura 100 %, OpenAPI y Compose válidos.
- Residual risk: las cuotas son globales por despliegue, no por plan comercial.
