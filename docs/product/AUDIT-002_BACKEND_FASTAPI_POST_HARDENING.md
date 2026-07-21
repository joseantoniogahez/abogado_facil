# AUDIT-002 — Auditoría posterior del backend FastAPI

Fecha: 2026-07-20
Alcance: cierre de `OPS-005` a `OPS-009`, backend runtime, contratos operativos, frontend OpenAPI
sync y pruebas.

## Resultado ejecutivo

La revisión de salida no encontró hallazgos P0/P1 abiertos ni regresiones en los contratos revisados.
Los cinco hardenings están implementados y cubiertos por la suite backend. El patrón de streaming
de `OPS-009` queda preparado para futuros consumidores IA, pero no se publica todavía ningún
endpoint ni proveedor LLM.

## Estado de findings iniciales

| Finding inicial                      | Ticket  | Estado  | Evidencia de cierre                                                                                                                                |
| ------------------------------------ | ------- | ------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| P1-001 OpenAPI público en producción | OPS-005 | Cerrado | `ApiSettings.openapi_enabled` deshabilita `/docs`, `/redoc` y `/openapi.json` en `prod`, `production` y `staging`; pruebas de configuración pasan. |
| P1-002 CORS demasiado permisivo      | OPS-006 | Cerrado | Orígenes HTTP(S) explícitos, métodos y headers mínimos, sin wildcard; pruebas de preflight/configuración pasan.                                    |
| P1-003 Sin readiness de dependencias | OPS-007 | Cerrado | `/v1/health` mantiene liveness; `/v1/readiness` verifica DB y object storage en paralelo, con timeout y respuesta `503` segura.                    |
| P1-004 Sin rate limiting             | OPS-008 | Cerrado | Login, registro y upload usan límites configurables; exceso devuelve `429 rate_limited`; Redis es obligatorio en producción cuando se habilita.    |
| P2-001 Streaming IA no definido      | OPS-009 | Cerrado | `stream_ai_events` implementa SSE con lifecycle, heartbeat, cancelación, correlación y redacción; pruebas específicas pasan.                       |

## Controles integrados revisados

- Auth/JWT, autorización/RBAC, aislamiento por despacho y errores normalizados siguen cubiertos por
  las pruebas existentes; no se modificaron sus contratos.
- La documentación de endpoints refleja readiness, rate limiting y la política OpenAPI/CORS.
- El artefacto frontend OpenAPI está sincronizado (`npm --prefix frontend run openapi:check`).
- Los logs de request y streaming mantienen `request_id` y no registran contenido legal, prompts,
  credenciales ni mensajes de proveedor.
- No se añadió dependencia nueva ni endpoint IA.

## Validación

- `.venv\Scripts\python.exe -m pytest backend/tests`: **397 passed**.
- `.venv\Scripts\python.exe -m pytest backend/tests --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=100`: **100% coverage**.
- `npm --prefix frontend run openapi:check`: **passed**.
- `git diff --check`: **passed**.
- `pre-commit`: intentado; no pudo inicializar hooks porque el entorno no tiene acceso a GitHub.

## Decisión de salida

`AUDIT-002` queda cerrado. La entrada a Fase 2 es técnicamente viable respecto a los hardenings
auditados, pero cada función IA deberá cumplir sus propios gates de aislamiento, consentimiento,
minimización de contexto, cifrado de credenciales, logs redaccionados y validación de salidas.
