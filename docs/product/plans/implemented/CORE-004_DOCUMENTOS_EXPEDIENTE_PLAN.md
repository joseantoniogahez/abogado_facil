# CORE-004 - API de documentos de expediente

## Estado del tracking

- ID: `CORE-004`
- Tipo: Backend
- Prioridad: P1
- Estado del plan: Completo
- Estado de implementación: Hecho
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

- [x] Los bytes se guardan mediante el puerto de `OPS-004`, nunca en PostgreSQL ni filesystem local.
- [x] PDF, DOCX y TXT válidos se cargan con tipo manual y quedan asociados al asunto propio.
- [x] Archivos incompatibles, demasiado grandes o sobre la cuota se rechazan sin residuos.
- [x] El listado es estable y la descarga transmite exactamente los bytes almacenados.
- [x] El borrado elimina metadata y objeto con comportamiento recuperable ante fallos parciales.
- [x] No se carga el archivo completo en memoria para validar, subir o descargar.
- [x] Aislamiento, claves privadas y errores opacos impiden acceso cruzado o enumeración.
- [x] API, OpenAPI, errores, docs y pruebas describen el mismo contrato.
- [x] Backend completo y cobertura 100% pasan y quedan registrados.

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

- [x] Cambiar CORE-004 a `En progreso` al iniciar.
- [x] Ejecutar preview del scaffold (el segundo intento confirmó que el slice ya creado no se sobrescribe).
- [x] Crear modelo, migración, schemas, repositorio, servicio, router y OpenAPI.
- [x] Validar streaming, tipos, tamaño y cuota sin confiar en datos del navegador.
- [x] Implementar compensación de upload/delete y errores seguros sin datos sensibles.
- [x] Registrar DI/router y cubrir UoW, aislamiento y puntos de fallo.

### Tests y documentación

- [x] Probar schemas, repositorio, servicio, router, migración, DI, OpenAPI y fake storage.
- [x] Probar el contrato S3 mediante cliente SDK simulado y el fake entregado por `OPS-004`; OPS-004 no aporta fixture MinIO vivo.
- [x] Actualizar `api_endpoints.md`, `authorization_matrix.md` y `error_mapping.md`.
- [x] Sincronizar OpenAPI frontend y actualizar tracking.

### Validación

- [x] Pruebas backend dirigidas.
- [x] `python -m pytest backend/tests`
- [x] `python -m pytest backend/tests --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=100`
- [x] `npm --prefix frontend run openapi:sync`
- [x] `pre-commit run --all-files`

## Riesgos y mitigaciones

| Riesgo                    | Mitigación                                                              |
| ------------------------- | ----------------------------------------------------------------------- |
| Inconsistencia SQL–objeto | Orden explícito, compensación y pruebas de cada punto de fallo          |
| Acceso cruzado            | Scope por despacho/asunto/documento y mismo 404 para ajeno/inexistente  |
| Archivo malicioso         | Allowlist, firma/MIME básica, nombre saneado y descarga como attachment |
| Memoria excesiva          | Lectura, upload y descarga en chunks con límite durante el stream       |
| Carrera en cuota          | Bloqueo/serialización definida y prueba de cargas concurrentes          |

## Registro de avance

| Fecha      | Estado        | Completado                                                               | Pendiente / siguiente acción segura                     |
| ---------- | ------------- | ------------------------------------------------------------------------ | ------------------------------------------------------- |
| 2026-07-13 | Plan dividido | Contrato backend separado de infraestructura y UI                        | Implementar `OPS-004`; después iniciar scaffold backend |
| 2026-07-13 | En progreso   | Dependencias CORE-002 y OPS-004 verificadas; lectura canónica completada | Crear slice, migración, pruebas y contratos             |
| 2026-07-13 | Hecho         | Slice, migración, contratos, OpenAPI y gates completos                   | CORE-010 puede consumir el contrato                     |

## Resultados de validación

| Fecha      | Comando                                                    | Resultado | Notas                                  |
| ---------- | ---------------------------------------------------------- | --------- | -------------------------------------- |
| 2026-07-13 | Revisión de partición y contratos                          | Pasó      | Planificación; runtime no implementado |
| 2026-07-13 | `python -m pytest backend/tests`                           | Pasó      | 353 pruebas tras formato final         |
| 2026-07-13 | Coverage backend                                           | Pasó      | 354 pruebas; 100.00%                   |
| 2026-07-13 | `npm --prefix frontend run openapi:sync` y `openapi:check` | Pasó      | Artefacto actualizado                  |
| 2026-07-13 | `pre-commit run --all-files`                               | Pasó      | Todos los hooks pasaron                |

## Pausa / handoff

- Estado actual: API backend completa y contrato OpenAPI sincronizado.
- Archivos y contratos cambiados: slice `matter_documents`, migración, DI/router, storage streaming, docs y OpenAPI.
- Pendiente: ninguno dentro de CORE-004; la UI corresponde a CORE-010.
- Bloqueos o aprobaciones: ninguno; aprobaciones humanas no aplican.
- Riesgo residual: no se levantó MinIO real; el adaptador se validó con cliente SDK simulado y Compose con pre-commit.
- Siguiente acción segura: iniciar CORE-010 o CORE-005 sobre el contrato publicado.

## Revisión documental de cierre

- [x] README backend revisado.
- [x] Operaciones y arquitectura backend revisadas.
- [x] Artefacto OpenAPI frontend revisado.
- [x] Foundation status revisados sin cambios: no cambiaron reglas ni gates fundacionales.
- [x] Plan y backlog sincronizados.

## Resumen de cierre

- Entregado: API aislada para cargar, listar, descargar y eliminar PDF/DOCX/TXT mediante object storage.
- Validación: backend y cobertura 100%, OpenAPI sync/check y pre-commit completos.
- Validación omitida: prueba contra MinIO vivo; no existe el fixture supuesto por el plan.
- Aprobaciones humanas: no aplicables.
- Riesgo residual: validación viva de MinIO queda cubierta operativamente por OPS-004, no por este slice.

No cambiar CORE-004 a `Hecho` mientras quede pendiente cualquier criterio, gate o documento.
