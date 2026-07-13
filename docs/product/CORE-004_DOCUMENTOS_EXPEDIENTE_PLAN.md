# CORE-004 - API de documentos de expediente

## Estado del tracking

- ID: `CORE-004`
- Tipo: Backend
- Prioridad: P1
- Estado del plan: Listo
- Estado de implementación: Identificado
- Última actualización: 2026-07-13
- Fuente: `docs/product/REQUERIMIENTOS_ABOGADO_FACIL_IA.md`, sección 6.8
- Backlog: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objetivo

Crear el slice backend que permita subir, listar, descargar y eliminar documentos PDF, DOCX y TXT
de un asunto propio. PostgreSQL conservará metadata y el contenido se persistirá mediante el puerto
S3-compatible entregado por `OPS-004`.

## Punto de partida

CORE-002 aporta asuntos aislados por `firm_id`. `OPS-004` debe aportar configuración validada,
puerto de object storage, adaptador MinIO/S3 y fake de pruebas. No existe aún tabla ni API de
documentos. La interfaz se implementará por separado en `CORE-010` después de estabilizar OpenAPI.

## Alcance

### Incluido

- Tabla `matter_documents` con metadata, clave opaca y aislamiento por despacho/asunto.
- Carga multipart de un archivo y selección de tipo documental manual.
- PDF, DOCX y TXT validados por extensión, MIME y firma/contenido básico.
- Límites configurables de tamaño y cantidad por asunto.
- Listado determinista de metadata, descarga autenticada por streaming y eliminación.
- Coordinación compensable entre Unit of Work y object storage.
- Errores normalizados, OpenAPI, pruebas backend y documentación operativa.

### Excluido

- Compose, bucket, SDK y adaptador S3/MinIO, propiedad de `OPS-004`.
- UI y consumidor frontend, propiedad de `CORE-010`.
- Extracción de texto (`CORE-005`), OCR, imágenes, antivirus externo y presigned URLs.
- Versionado, reemplazo, búsqueda, carpetas, papelera y borrado de asuntos (`SEC-003`).

## Dependencias y decisiones

- Dependencias: `CORE-002` y `OPS-004` en estado `Hecho` antes de cerrar este ticket.
- La API será la autoridad de límites. Defaults propuestos: 10 MiB y 50 documentos por asunto.
- La clave será generada por servidor, por ejemplo
  `firms/{firm_id}/matters/{matter_id}/{document_uuid}`; nunca usará el nombre original.
- Tipos: `identification`, `record`, `contract`, `receipt`, `proof`, `filing`, `notification`,
  `evidence` y `other`.
- Asuntos/documentos ajenos e inexistentes devolverán el mismo `404`.
- Si falla el almacenamiento no se confirmará metadata. Si falla SQL tras el upload, se intentará
  eliminar el objeto y se registrará un evento seguro de reconciliación.
- Las descargas pasarán por la API, serán streaming y usarán `Content-Disposition: attachment`.
- No se expondrán `firm_id`, storage key, bucket, endpoint ni credenciales.

## Contrato propuesto

### Persistencia

| Campo               | Regla                                          |
| ------------------- | ---------------------------------------------- |
| `id`                | UUID público generado por servidor             |
| `firm_id`           | FK obligatoria e indexada                      |
| `matter_id`         | FK obligatoria e indexada con despacho y orden |
| `original_filename` | Nombre saneado sólo para presentación          |
| `document_type`     | Enum manual permitido                          |
| `media_type`        | Tipo validado por servidor                     |
| `size_bytes`        | Tamaño validado                                |
| `storage_key`       | Clave opaca única, privada                     |
| `created_at`        | Timestamp UTC                                  |

### API

| Método   | Ruta                                                       | Resultado                      |
| -------- | ---------------------------------------------------------- | ------------------------------ |
| `POST`   | `/v1/matters/{matter_id}/documents`                        | Multipart; `201` con metadata  |
| `GET`    | `/v1/matters/{matter_id}/documents`                        | `items` y `total`              |
| `GET`    | `/v1/matters/{matter_id}/documents/{document_id}/download` | Stream autenticado             |
| `DELETE` | `/v1/matters/{matter_id}/documents/{document_id}`          | Elimina metadata/objeto; `204` |

## Criterios de aceptación

- [ ] Los bytes se guardan mediante el puerto de `OPS-004`, nunca en PostgreSQL ni filesystem local.
- [ ] PDF, DOCX y TXT válidos se cargan con tipo manual y quedan asociados al asunto propio.
- [ ] Archivos incompatibles, demasiado grandes o sobre la cuota se rechazan sin residuos.
- [ ] El listado es estable y la descarga transmite exactamente los bytes almacenados.
- [ ] El borrado elimina metadata y objeto con comportamiento recuperable ante fallos parciales.
- [ ] No se carga el archivo completo en memoria para validar, subir o descargar.
- [ ] Aislamiento, claves privadas y errores opacos impiden acceso cruzado o enumeración.
- [ ] API, OpenAPI, errores, docs y pruebas describen el mismo contrato.
- [ ] Backend completo y cobertura 100% pasan y quedan registrados.

## Archivos y contratos afectados

| Superficie   | Archivos o contratos esperados                       | Cambio    |
| ------------ | ---------------------------------------------------- | --------- |
| Feature      | `backend/app/features/matter_documents`              | Sí        |
| Persistencia | modelo, metadata y migración Alembic                 | Sí        |
| Integración  | consumo del puerto creado por `OPS-004`              | Sí        |
| Registro     | DI, router y metadata OpenAPI                        | Sí        |
| Docs         | endpoints, autorización, errores y anexos aplicables | Sí        |
| Frontend     | artefacto OpenAPI, sin consumidor/UI                 | Sólo sync |

## Plan de trabajo

### Implementación

- [ ] Cambiar CORE-004 a `En progreso` al iniciar.
- [ ] Ejecutar `python scripts/scaffold_feature.py backend matter-documents --with-model --dry-run`.
- [ ] Crear modelo, migración, schemas, repositorio, servicio, router y OpenAPI.
- [ ] Validar streaming, tipos, tamaño y cuota sin confiar en datos del navegador.
- [ ] Implementar compensación de upload/delete y observabilidad sin datos sensibles.
- [ ] Registrar DI/router y cubrir UoW, aislamiento y puntos de fallo.

### Tests y documentación

- [ ] Probar schemas, repositorio, servicio, router, migración, DI, OpenAPI y fake storage.
- [ ] Añadir una prueba dirigida contra MinIO usando el fixture entregado por `OPS-004`.
- [ ] Actualizar `api_endpoints.md`, `authorization_matrix.md` y `error_mapping.md`.
- [ ] Sincronizar OpenAPI frontend y actualizar tracking.

### Validación

- [ ] Pruebas backend dirigidas.
- [ ] `python -m pytest backend/tests`
- [ ] `python -m pytest backend/tests --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=100`
- [ ] `npm --prefix frontend run openapi:sync`
- [ ] `pre-commit run --all-files`

## Riesgos y mitigaciones

| Riesgo                    | Mitigación                                                              |
| ------------------------- | ----------------------------------------------------------------------- |
| Inconsistencia SQL–objeto | Orden explícito, compensación y pruebas de cada punto de fallo          |
| Acceso cruzado            | Scope por despacho/asunto/documento y mismo 404 para ajeno/inexistente  |
| Archivo malicioso         | Allowlist, firma/MIME básica, nombre saneado y descarga como attachment |
| Memoria excesiva          | Lectura, upload y descarga en chunks con límite durante el stream       |
| Carrera en cuota          | Bloqueo/serialización definida y prueba de cargas concurrentes          |

## Registro de avance

| Fecha      | Estado        | Completado                                        | Pendiente / siguiente acción segura                     |
| ---------- | ------------- | ------------------------------------------------- | ------------------------------------------------------- |
| 2026-07-13 | Plan dividido | Contrato backend separado de infraestructura y UI | Implementar `OPS-004`; después iniciar scaffold backend |

## Resultados de validación

| Fecha      | Comando                           | Resultado | Notas                                  |
| ---------- | --------------------------------- | --------- | -------------------------------------- |
| 2026-07-13 | Revisión de partición y contratos | Pasó      | Planificación; runtime no implementado |

## Pausa / handoff

- Estado actual: plan listo; implementación identificada hasta completar `OPS-004`.
- Archivos y contratos cambiados: plan y backlog.
- Pendiente: toda la implementación backend.
- Bloqueos o aprobaciones: ninguno; la secuencia requiere completar primero `OPS-004`.
- Riesgo residual: compensación SQL–MinIO aún no verificada.
- Siguiente acción segura: implementar y cerrar `OPS-004`.

## Revisión documental de cierre

- [ ] README backend revisado.
- [ ] Operaciones y arquitectura backend revisadas.
- [ ] Artefacto OpenAPI frontend revisado.
- [ ] Foundation status revisados sin cambios salvo movimiento fundacional.
- [ ] Plan y backlog sincronizados.

## Resumen de cierre

- Entregado: pendiente.
- Validación: revisión documental del plan.
- Validación omitida: gates de runtime hasta implementación.
- Aprobaciones humanas: no aplicables al plan.
- Riesgo residual: integración real pendiente.

No cambiar CORE-004 a `Hecho` mientras quede pendiente cualquier criterio, gate o documento.
