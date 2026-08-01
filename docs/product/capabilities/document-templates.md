# Plantillas y borradores de documentos

## Propósito

Crear borradores editables a partir de plantillas controladas y permitir copiarlos o exportarlos sin
guardarlos, enviarlos o presentarlos automáticamente.

## Flujo principal

1. El usuario abre el catálogo y selecciona una plantilla disponible.
1. Completa los campos requeridos y revisa proveedor, modelo y valores en una vista previa.
1. Confirma la generación con una credencial BYOK válida.
1. Edita el borrador resultante y puede copiar su contenido o exportarlo como archivo de texto.

## Límites y advertencias

- El catálogo inicial contiene requerimiento de pago, convenio, solicitud de documentos y resumen
  interno.
- El resultado siempre es un borrador sujeto a revisión humana.
- La aplicación no guarda, envía, firma ni presenta el documento automáticamente.
- La generación con proveedor está implementada para validación, pero no autorizada para release
  mientras `SEC-001C` y `SEC-002` sigan pendientes.

## Permisos

- El catálogo, la vista previa y la generación requieren sesión autenticada.
- La generación requiere una credencial BYOK válida del usuario y despacho actuales.

## Estados de error

- Campos o tokens de vista previa inválidos requieren corregir el formulario o repetir la vista
  previa.
- Credenciales ausentes, rate limits, timeouts y fallos del proveedor bloquean la generación sin
  perder el formulario editable.
- Un fallo de copia o descarga se informa sin marcar el borrador como enviado o guardado.

## Referencias técnicas

- [DOC-001](../plans/implemented/DOC-001_CATALOGO_PLANTILLAS_SIMPLES_PLAN.md)
- [DOC-002](../plans/implemented/DOC-002_GENERADOR_BORRADORES_PLAN.md)
- [DOC-003](../plans/implemented/DOC-003_COPIAR_EXPORTAR_BORRADOR_PLAN.md)
