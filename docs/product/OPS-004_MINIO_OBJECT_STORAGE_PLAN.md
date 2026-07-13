# OPS-004 - Base S3-compatible con MinIO

## Estado del tracking

- ID: `OPS-004`
- Tipo: Ops
- Prioridad: P1
- Estado del plan: Hecho
- Estado de implementación: Hecho
- Última actualización: 2026-07-13
- Backlog: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objetivo

Proveer object storage privado, persistente y S3-compatible para documentos mediante MinIO en
Docker Compose, junto con un puerto backend probado que desacople las features del proveedor.

## Alcance

### Incluido

- MinIO con healthcheck, volumen nombrado y bucket privado creado idempotentemente.
- Configuración local/test/prod para endpoint, región, bucket, credenciales y path-style.
- Puertos de API/consola publicados sólo en desarrollo.
- Puerto backend `put`, `stream/get` y `delete`, adaptador S3/MinIO y fake para pruebas.
- Timeouts, traducción de errores y redacción de secretos/logs.
- Prueba real de subir, leer, comparar, borrar y persistir tras recrear contenedor.
- README, `.env_examples`, Compose y anexo de puertos/adaptadores actualizados.

### Excluido

- Tabla, API y reglas de documentos (`CORE-004`).
- UI (`CORE-010`) y proveedor S3 productivo.
- Backups completos y política de retención de documentos.

## Dependencias y decisiones

- `DEC-010` está cerrada: MinIO local mediante API S3; blobs fuera de PostgreSQL.
- El SDK S3 se fijará y auditará en este ticket; ninguna feature importará el SDK directamente.
- Producción exigirá secretos explícitos y permitirá reemplazar MinIO por un endpoint S3 externo.
- Las pruebas unitarias usarán fake; la integración real será separable y reproducible con Compose.
- Variables: `S3_ENDPOINT_URL`, `S3_REGION`, `S3_BUCKET`, `S3_ACCESS_KEY`, `S3_SECRET_KEY` y
  `S3_PATH_STYLE`; puertos MinIO sólo si se publican localmente.

## Criterios de aceptación

- [x] Compose levanta MinIO saludable y crea el bucket privado de forma idempotente.
- [x] Los objetos sobreviven a recrear contenedores conservando el volumen.
- [x] Backend puede put/stream/delete mediante un puerto sin importar el SDK desde features.
- [x] Configuración inválida falla al arranque con mensajes que no exponen secretos.
- [x] Producción no contiene credenciales inseguras por defecto.
- [x] La prueba real compara bytes, elimina el objeto y verifica su ausencia.
- [x] Compose dev/test/prod, docs y pre-commit pasan.

## Archivos y contratos afectados

| Superficie  | Archivos esperados                                           | Cambio |
| ----------- | ------------------------------------------------------------ | ------ |
| Compose     | `compose.yaml`, overrides test/prod, volúmenes/healthchecks  | Sí     |
| Config      | `.env_examples`, settings y factory backend                  | Sí     |
| Integración | `backend/app/integrations` y pruebas                         | Sí     |
| Docs        | README raíz/backend y `clean_architecture_ports_adapters.md` | Sí     |

## Plan de trabajo

### Implementación

- [x] Cambiar OPS-004 a `En progreso` al iniciar.
- [x] Fijar imagen MinIO/cliente, revisar licencia y registrar versiones explícitas.
- [x] Agregar servicio, healthcheck, init de bucket, volumen y políticas por ambiente.
- [x] Añadir settings tipados y validación prod/local.
- [x] Implementar puerto, adaptador y fake con streaming, timeouts y errores seguros.
- [x] Crear prueba de integración reproducible y prueba de persistencia del volumen.

### Documentación y validación

- [x] Actualizar `.env_examples`, README raíz/backend y anexo de arquitectura.
- [x] `docker compose config`
- [x] `docker compose -f compose.yaml -f compose.test.yaml config`
- [x] `docker compose -f compose.yaml -f compose.prod.yaml config`
- [x] Pruebas backend dirigidas de configuración/adaptador.
- [x] `python -m pytest backend/tests`
- [x] Gate backend de cobertura 100%.
- [x] `pre-commit run --all-files`

## Riesgos y mitigaciones

| Riesgo                      | Mitigación                                     |
| --------------------------- | ---------------------------------------------- |
| Pérdida de objetos          | Volumen nombrado y prueba de recreación        |
| Secretos filtrados          | Variables backend, redacción y errores seguros |
| Acoplamiento a MinIO        | Puerto propio y contrato S3-compatible         |
| Suite dependiente de Docker | Fake unitario y prueba real separable          |

## Registro de avance

| Fecha      | Estado     | Completado                                                             | Pendiente / siguiente acción segura              |
| ---------- | ---------- | ---------------------------------------------------------------------- | ------------------------------------------------ |
| 2026-07-13 | Plan listo | Infraestructura separada de API y UI                                   | Cambiar a `En progreso` y validar Compose actual |
| 2026-07-13 | Hecho      | MinIO privado persistente, puerto/adaptador/fake, configuración y docs | Ninguna; OPS-004 cerrado                         |

## Resultados de validación

| Fecha      | Comando                          | Resultado | Notas                                                         |
| ---------- | -------------------------------- | --------- | ------------------------------------------------------------- |
| 2026-07-13 | Revisión de partición            | Pasó      | Planificación; MinIO no implementado                          |
| 2026-07-13 | Compose base/test/prod           | Pasó      | Producción validada con variables explícitas                  |
| 2026-07-13 | Pruebas dirigidas                | Pasó      | 35 pruebas de settings, adaptador y arranque                  |
| 2026-07-13 | Integración y persistencia MinIO | Pasó      | Bytes, borrado, ausencia y recreación con volumen verificados |
| 2026-07-13 | Suite y cobertura backend        | Pasó      | 347 pasaron, 1 omitida por defecto; cobertura 100.00%         |
| 2026-07-13 | `pre-commit run --all-files`     | Pasó      | Todos los hooks pasaron                                       |

## Pausa / handoff

- Estado actual: implementación completa.
- Pendiente: ninguno dentro de OPS-004.
- Bloqueos: ninguno.
- Riesgo residual: backups y retención permanecen fuera de alcance.
- Siguiente acción segura: iniciar `CORE-004` consumiendo `FileStoragePort`.

## Revisión documental de cierre

- [x] README raíz/backend revisados.
- [x] Arquitectura backend revisada.
- [x] Foundation status revisados; sin cambio porque no se alteraron reglas ni gates fundacionales.
- [x] Plan y backlog sincronizados.

## Resumen de cierre

- Entregado: MinIO local/test/prod, bucket privado persistente, configuración segura y puerto S3 probado.
- Validación: Compose, suite backend, cobertura 100%, integración real, persistencia y pre-commit.
- Validación omitida: ninguna obligatoria.
- Aprobaciones humanas: no aplicables.
- Riesgo residual: backups/retención y elección del endpoint S3 productivo siguen en tickets posteriores.
