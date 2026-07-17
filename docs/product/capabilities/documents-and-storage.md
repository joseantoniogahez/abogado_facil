# Documentos y almacenamiento

## Capacidades disponibles

- Subir documentos PDF, DOCX y TXT desde el detalle del asunto.
- Listar, descargar y eliminar documentos del asunto.
- Conservar metadata del documento en la base de datos y el archivo en almacenamiento S3-compatible.
- Extraer localmente texto de PDFs que tengan una capa de texto.

## Límites y advertencias

- Los PDFs escaneados no pasan por OCR y quedan con extracción vacía.
- Un error de parser no impide conservar el documento; queda registrado como extracción fallida.
- DOCX y TXT no requieren extracción PDF.
- El texto extraído queda disponible para futuros flujos de IA, pero la carga no ejecuta análisis de IA.
- Los archivos no se almacenan dentro de PostgreSQL.

## Referencias técnicas

- [CORE-004](../plans/implemented/CORE-004_DOCUMENTOS_EXPEDIENTE_PLAN.md)
- [CORE-005](../plans/implemented/CORE-005_EXTRACCION_TEXTO_PDF_PLAN.md)
- [CORE-010](../plans/implemented/CORE-010_INTERFAZ_DOCUMENTOS_EXPEDIENTE_PLAN.md)
- [OPS-004](../plans/implemented/OPS-004_MINIO_OBJECT_STORAGE_PLAN.md)
