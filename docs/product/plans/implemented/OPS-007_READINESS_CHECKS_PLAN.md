# OPS-007 - Health y readiness checks

## Tracking Status

- ID: `OPS-007`
- Type: `Backend`
- Priority: `P1`
- Plan status: `Complete`
- Implementation status: `Hecho`
- Last updated: `2026-07-20`
- Backlog source: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objective

Separar la señal de proceso vivo de la capacidad real de aceptar tráfico dependiente de base de datos y object storage.

## Delivered

- `/v1/health` conserva un liveness barato y público.
- `/v1/readiness` comprueba DB y object storage en paralelo con timeout configurable de 2 segundos.
- Responde `200` con `ready`, o `503` con `not_ready` y estados seguros `ok/unavailable`, sin detalles del proveedor.
- Se añadió `check` al puerto de storage y al adaptador S3.
- Se actualizaron OpenAPI, inventario de endpoints, matriz de autorización y Compose (el healthcheck existente sigue usando liveness).

## Acceptance Criteria

- [x] Liveness y readiness tienen contratos separados.
- [x] Fallos de DB/storage se reflejan de forma determinista y segura.
- [x] Docker/deployment docs y tests quedan sincronizados.

## Validation Results

- `python -m pytest backend/tests`: 385 passed.
- `python -m pytest backend/tests --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=100`: 385 passed, 100% coverage.
- `npm --prefix frontend run openapi:check`: passed.
- `npm --prefix frontend run check` / `build`: no completaron por restricciones/timeout del bundler en este entorno.
- `pre-commit run --all-files`: checks pasaron hasta `hadolint`; Docker Desktop no estaba disponible para ese hook.

## Completion Summary

- Delivered: readiness separado con checks críticos, timeout y respuesta segura.
- Residual risk: ejecutar validación frontend completa y hooks Docker cuando el entorno tenga acceso normal al bundler y Docker Desktop activo.
