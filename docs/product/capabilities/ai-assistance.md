# Asistencia de IA sobre expedientes

## Propósito

Ayudar a estructurar información del expediente mediante IA BYOK sin convertir el resultado en una
decisión jurídica ni ejecutar acciones automáticas.

## Flujo principal

1. El usuario elige una función: analizar relato, generar preguntas o mensaje, resumir, crear una
   cronología o sugerir elementos de checklist.
1. Revisa proveedor, modelo y fuentes incluidas en una vista previa.
1. Confirma la ejecución; el backend valida de nuevo el contexto y la credencial BYOK.
1. Revisa y edita el resultado, y puede aceptarlo, rechazarlo, regenerarlo o reportar un problema.
1. Un resultado aceptado puede convertirse explícitamente en nota, tarea, pregunta, checklist,
   documento faltante o mensaje.

## Límites y advertencias

- El contenido es un borrador sujeto a revisión humana y no constituye asesoría jurídica.
- Consultar resultados guardados no vuelve a invocar al proveedor.
- Cambiar función, fuentes, proveedor o modelo invalida la vista previa anterior.
- Las funciones están implementadas para validación, pero no están autorizadas para release
  mientras `SEC-001C` y `SEC-002` continúen pendientes.

## Permisos

- Requiere sesión autenticada, credencial BYOK válida y acceso al despacho del asunto.
- Los recursos ajenos al despacho se comportan como no encontrados.

## Estados de error

- Contexto, entrada o confirmación inválidos requieren corregir o repetir la vista previa.
- Una credencial ausente o inválida bloquea la ejecución.
- Rate limits, timeouts y fallos del proveedor muestran mensajes seguros y no exponen secretos.

## Referencias técnicas

- [AI-101](../plans/implemented/AI-101_ANALIZADOR_RELATO_PLAN.md)
- [AI-102](../plans/implemented/AI-102_PREGUNTAS_CLIENTE_PLAN.md)
- [AI-103](../plans/implemented/AI-103_MENSAJES_CLIENTE_PLAN.md)
- [AI-104](../plans/implemented/AI-104_REVISION_ACEPTACION_PLAN.md)
- [AI-105](../plans/implemented/AI-105_CONVERSION_ACCIONES_PLAN.md)
- [AI-106](../plans/implemented/AI-106_PROCEDENCIA_ACTUALIZACION_PLAN.md)
- [AI-201](../plans/implemented/AI-201_RESUMEN_EXPEDIENTE_PLAN.md)
- [AI-202](../plans/implemented/AI-202_CRONOLOGIA_HECHOS_PLAN.md)
- [AI-203](../plans/implemented/AI-203_CHECKLIST_PERSONALIZADO_IA_PLAN.md)
- [LEGAL-002A](../plans/implemented/LEGAL-002A_PATRON_REVISION_HUMANA_PLAN.md)
- [UX-AI-001](../plans/implemented/UX-AI-001_PREVIEW_CONTEXTO_PLAN.md)
