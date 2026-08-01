# Documentos y almacenamiento

## Propósito

Conservar documentos del expediente fuera de PostgreSQL y hacer disponible su metadata y texto
extraído cuando sea viable.

## Flujo principal

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

## Permisos

- Cargar, listar, descargar y eliminar requieren sesión autenticada y acceso al despacho del asunto.
- Los documentos ajenos se comportan como no encontrados.

## Estados de error

- Tipo, tamaño o contenido inválido rechaza la carga antes de presentarla como disponible.
- Un fallo de parser conserva el archivo y registra la extracción como fallida.
- Un fallo de almacenamiento no crea metadata que afirme que el archivo está disponible.

## Referencias técnicas

- [CORE-004](../plans/implemented/CORE-004_DOCUMENTOS_EXPEDIENTE_PLAN.md)
- [CORE-005](../plans/implemented/CORE-005_EXTRACCION_TEXTO_PDF_PLAN.md)
- [CORE-010](../plans/implemented/CORE-010_INTERFAZ_DOCUMENTOS_EXPEDIENTE_PLAN.md)
- [OPS-004](../plans/implemented/OPS-004_MINIO_OBJECT_STORAGE_PLAN.md)
