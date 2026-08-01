# Avisos legales y experiencia de uso

## Propósito

Mantener advertencias, revisión humana y jerarquía visual coherentes en las funciones sensibles.

## Flujo principal

- La aplicación comunica que la información generada por IA requiere revisión humana.
- La landing y los flujos actuales muestran el aviso legal correspondiente.
- Las acciones principales, destructivas y deshabilitadas tienen jerarquía visual explícita.
- Los estados no dependen únicamente de `hover` y conservan una relación accesible entre texto,
  control y resultado.

## Límites y advertencias

- El patrón de revisión humana y su consistencia en funciones IA están implementados.
- El consentimiento, aviso de privacidad, términos y aprobación jurídica de release permanecen
  pendientes en `SEC-002`.
- Los cálculos y cualquier contenido generado deben presentarse como estimaciones o borradores,
  nunca como asesoría jurídica definitiva.

## Permisos

- Los avisos públicos se muestran sin sesión; la revisión de resultados requiere acceso autenticado
  al recurso correspondiente.

## Estados de error

- Ningún fallo puede omitir el aviso legal ni presentar contenido IA como aceptado automáticamente.
- Una acción no autorizada permanece bloqueada y no se sustituye por una advertencia meramente visual.

## Referencias técnicas

- [LEGAL-001](../plans/implemented/LEGAL-001_AVISOS_LEGALES_PLAN.md)
- [UX-001](../plans/implemented/UX-001_JERARQUIA_VISUAL_ACCIONES_PLAN.md)
- [LEGAL-002A](../plans/implemented/LEGAL-002A_PATRON_REVISION_HUMANA_PLAN.md)
- [LEGAL-002B implementado](../plans/implemented/LEGAL-002B_VALIDACION_AVISOS_IA_PLAN.md)
