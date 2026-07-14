# CORE-005 - Extracción de texto de PDF

## Tracking Status

- ID: `CORE-005`
- Type: `Backend`
- Priority: `P1`
- Plan status: `Complete`
- Implementation status: `Hecho`
- Last updated: `2026-07-14`
- Backlog source: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objective

Extraer y persistir el texto de documentos PDF con capa de texto para que futuros flujos de IA
puedan consumirlo sin volver a descargar ni procesar el archivo.

## Starting Point

CORE-004 almacena PDF, DOCX y TXT en object storage y conserva metadata aislada por despacho y
asunto. No existe extracción ni metadata que distinga un PDF utilizable de uno escaneado o ilegible.

## Scope

### Included

- Extracción local de texto durante la carga de PDF válido.
- Persistencia del texto extraído y de un estado explícito.
- Estados para texto disponible, PDF sin capa de texto, fallo recuperable y archivo no PDF.
- Consulta interna aislada por despacho/asunto/documento para futuros servicios de IA.
- Migración, pruebas y documentación del comportamiento.

### Excluded

- OCR, imágenes, extracción de DOCX/TXT, búsqueda full-text y endpoints de análisis.
- Resumen, cronología o llamadas a proveedores de IA.
- Exposición del texto completo en las respuestas públicas de documentos.
- Procesamiento asíncrono o reprocesamiento de documentos existentes.

## Dependencies and Decisions

- Dependencies: `CORE-004` y `OPS-004`, ambos `Hecho`.
- Decisions closed: la extracción es síncrona, local y tolerante a fallos; un fallo no impide guardar
  el documento. El texto se normaliza por página y se persiste en PostgreSQL.
- Open questions: ninguna que bloquee la entrega.

## Acceptance Criteria

- [x] Un PDF con capa de texto persiste contenido normalizado con estado `available`.
- [x] Un PDF sin texto o ilegible se almacena sin OCR y registra `empty` o `failed` sin fallar la carga.
- [x] Archivos no PDF registran `not_applicable` y no invocan el extractor.
- [x] El repositorio permite recuperar texto sólo dentro del scope despacho/asunto/documento.
- [x] El API público no expone texto extraído ni rompe el contrato existente.
- [x] Required documentation is synchronized with delivered behavior.
- [x] Required validation gates pass and are recorded below.
- [x] Mandatory human approvals are recorded, or explicitly not applicable.

## Affected Contracts and Files

| Surface      | Expected files or contracts                            | Change required |
| ------------ | ------------------------------------------------------ | --------------- |
| Runtime      | `matter_documents` model/service/repository            | yes             |
| Data         | Alembic migration for extraction fields                | yes             |
| Dependencies | backend runtime PDF parser                             | yes             |
| Tests        | matter document service/repository/migration contracts | yes             |
| Docs         | backend README and document operation notes            | yes             |

## Work Plan

### Implementation

- [x] Add extraction fields and migration.
- [x] Add a PDF text extraction port/adapter and inject it into the document service.
- [x] Persist normalized results without making extraction failure fatal to uploads.
- [x] Add a firm-scoped internal repository read for future IA consumers.

### Tests and Documentation

- [x] Add or update tests with the behavior change.
- [x] Review all documentation surfaces required by `AGENTS.md`.
- [x] Update canonical documents affected by the code diff.

### Validation

- [x] Targeted matter-document tests.
- [x] `python -m pytest backend/tests`.
- [x] Backend 100% coverage gate.
- [x] Pre-commit on all files.

## Progress Log

| Date       | State       | Completed                                                            | Pending / next safe action                               |
| ---------- | ----------- | -------------------------------------------------------------------- | -------------------------------------------------------- |
| 2026-07-14 | En progreso | Alcance, dependencias y decisiones documentados                      | Implementar migración, extractor, persistencia y pruebas |
| 2026-07-14 | Hecho       | Extracción, persistencia, migración, pruebas, docs y gates completos | Ninguna acción pendiente en CORE-005                     |

## Validation Results

| Date       | Command                                     | Result | Notes                                                 |
| ---------- | ------------------------------------------- | ------ | ----------------------------------------------------- |
| 2026-07-14 | Pruebas dirigidas de documentos y extractor | Pasó   | 12 pruebas                                            |
| 2026-07-14 | `python -m pytest backend/tests -x`         | Pasó   | 359 pruebas; warning no bloqueante de caché pytest    |
| 2026-07-14 | Coverage backend con mínimo 100%            | Pasó   | 359 pruebas; 100.00%                                  |
| 2026-07-14 | `python -m pre_commit run --all-files`      | Pasó   | Segundo intento tras autofix; todos los hooks pasaron |

## Pause / Handoff Record

- Current state: extracción PDF local y tolerante a fallos completa.
- Changed files and contracts: modelo/migración de documentos, servicio, repositorio, DI, adaptador
  PDF, dependencia runtime, pruebas y documentación backend.
- Pending work: ninguno dentro de CORE-005.
- Blockers or approvals: ninguno.
- Residual risks: PDFs complejos pueden no ser extraíbles sin OCR, fuera de alcance.
- Next safe action: futuros flujos IA pueden consumir la lectura interna con scope; OCR permanece fuera de alcance.

## Completion Documentation Review

- [x] Root and service READMEs reviewed.
- [x] Backend operation and architecture docs reviewed.
- [x] Frontend operation docs and inventories reviewed.
- [x] Foundation status files reviewed and changed only if a foundation contract moved.
- [x] AI governance docs, templates, and checklists reviewed.
- [x] Item plan and summary backlog synchronized.

Record documents intentionally unchanged and why:

- Root `README.md`: sin cambio; no cambió el arranque ni el contrato general del producto.
- `backend/docs/operations/authorization_matrix.md` y `error_mapping.md`: sin cambio; no hay endpoint,
  permiso ni error público nuevo.
- Docs frontend y OpenAPI: sin cambio; las respuestas públicas permanecen idénticas.
- Foundation status: sin cambio; no cambió una regla o gate fundacional.
- AI governance: sin cambio; el flujo de backlog existente fue seguido sin modificarlo.

## Completion Summary

- Delivered: extracción local de texto PDF persistida con estados explícitos y acceso interno aislado.
- Validation: 12 pruebas dirigidas, 359 pruebas backend, cobertura 100% y pre-commit completo.
- Skipped validation: prueba OCR y proveedor IA, explícitamente fuera de alcance.
- Human approvals: not applicable.
- Residual risk: PDFs escaneados o con codificaciones no soportadas pueden quedar `empty`/`failed` y
  requieren OCR futuro.
