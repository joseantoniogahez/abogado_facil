# AUDIT-001 — Auditoría inicial del backend FastAPI

Fecha: 2026-07-19
Alcance: `backend/app`, `backend/tests`, contratos operativos y anexos de arquitectura.

## Resultado ejecutivo

La línea base funcional está estable: la suite existente ejecuta 378 pruebas y todas pasan. No se
identificó un hallazgo P0 en autenticación, autorización, aislamiento por despacho, manejo
normalizado de errores, UoW o almacenamiento de documentos. Sí existen cuatro riesgos P1 ya
separados en los tickets `OPS-005` a `OPS-009`; deben resolverse antes de producción y antes de
iniciar funciones IA.

## Hallazgos

### P1-001 — La documentación OpenAPI queda pública en cualquier entorno

- Evidencia: `backend/app/core/setup/factory.py:135-143` crea FastAPI sin `docs_url`, `redoc_url`
  ni `openapi_url` condicionados por `APP_ENV`.
- Impacto: `/docs`, `/redoc` y `/openapi.json` quedan expuestos en producción, revelando el
  inventario completo de rutas, esquemas y ejemplos operativos.
- Recomendación: implementar una política explícita por entorno y probar local/test/prod.
- Destino: `OPS-005`.

### P1-002 — CORS permite métodos y headers comodín junto con credenciales

- Evidencia: `backend/app/core/setup/cors.py:12-17` usa `allow_credentials=True`,
  `allow_methods=["*"]` y `allow_headers=["*"]` para cualquier origen configurado.
- Impacto: amplía innecesariamente la superficie de requests cross-origin y deja la política
  dependiente de una lista de origenes sin restricciones equivalentes de métodos y headers.
- Recomendación: declarar métodos y headers mínimos por entorno; validar que los comodines no se
  acepten en producción y probar preflight y requests autenticados.
- Destino: `OPS-006`.

### P1-003 — No existe readiness check de dependencias críticas

- Evidencia: el único endpoint operativo es `backend/app/features/health/router.py:9-11`, que
  siempre devuelve `{"status": "ok"}` y no verifica base de datos ni object storage.
- Impacto: un orquestador puede enviar tráfico a una instancia viva pero incapaz de atender
  operaciones que requieren sus dependencias.
- Recomendación: conservar liveness barato y añadir readiness separado, con timeout, status code
  determinista y respuesta sin detalles internos.
- Destino: `OPS-007`.

### P1-004 — Login, registro y uploads no tienen rate limiting

- Evidencia: no hay middleware, dependencia ni integración de contador/límite en
  `backend/app`; las superficies de login/registro están en `backend/app/features/auth/router.py`
  y el upload en `backend/app/features/matter_documents/router.py:27-36`.
- Impacto: quedan expuestos a fuerza bruta, abuso de registro y consumo descontrolado de recursos;
  el riesgo sería especialmente material al añadir llamadas IA.
- Recomendación: definir límites configurables y un backend compartido entre workers, con respuesta
  normalizada, headers útiles y pruebas de exceso/recuperación.
- Destino: `OPS-008`.

### P2-001 — El patrón de streaming existente sólo cubre descargas

- Evidencia: `backend/app/features/matter_documents/router.py:47-53` usa `StreamingResponse` para
  descargar documentos; no existe contrato de SSE/JSON Lines, cancelación, heartbeat ni métricas
  específicas para ejecuciones IA.
- Impacto: una futura función IA podría introducir respuestas progresivas inconsistentes o
  difíciles de diagnosticar si cada feature inventa su propio ciclo de eventos.
- Recomendación: resolver formato, cancelación, errores, heartbeat, correlación y redacción de
  datos antes de publicar endpoints IA.
- Destino: `OPS-009`.

## Controles revisados sin hallazgo abierto

- Auth/JWT: issuer, audience, expiración, algoritmo y secreto de producción se validan en
  `backend/app/core/config/settings.py`; el token se decodifica con issuer/audience y algoritmo
  explícitos.
- RBAC: el catálogo y la cobertura de políticas están contractualmente probados; las rutas
  protegidas usan dependencias tipadas.
- Aislamiento: las features legales derivan `firm_id` del principal y las pruebas cubren accesos
  extranjeros/ multiusuario.
- Errores: handlers centrales normalizan validación, HTTP y errores no controlados, incluyendo
  `request_id`, y no devuelven detalles del proveedor de storage.
- UoW/DI/routers: la suite cubre límites arquitectónicos, transacciones, registro centralizado y
  providers de dependencias.
- Documentos: el tamaño, cuota, tipo/contenido, claves por despacho y streaming están cubiertos
  por pruebas; queda pendiente añadir límite de abuso (P1-004).

## Validación

Ejecutado:

```text
.\\.venv\\Scripts\\python.exe -m pytest backend/tests
378 passed, 1 warning en pytest cache (WinError 183 al crear .pytest_cache)
```

No ejecutado: coverage gate de 100% y pre-commit. No se modificó runtime ni configuración; la
auditoría sólo produce documentación y esos gates quedan para los tickets de implementación.

## Decisión de secuencia

`AUDIT-001` queda listo para cierre documental. El siguiente trabajo seguro es `OPS-005`, seguido
por `OPS-006`, `OPS-007`, `OPS-008` y `OPS-009`; `AUDIT-002` permanece bloqueado por dependencia
hasta que los cinco tickets estén en `Hecho`.
