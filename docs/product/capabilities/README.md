# Capacidades del producto

Esta carpeta es la fuente funcional estable de Abogado Fácil. Describe lo que el producto permite
hacer hoy, sus límites, reglas visibles y comportamiento esperado.

Está pensada para dos usos:

- La IA la consulta para entender capacidades existentes antes de proponer cambios.
- El equipo puede derivarla en un manual de usuario después del release oficial.

Los detalles técnicos, decisiones de implementación y evidencias de validación permanecen en
[`../plans/implemented/`](../plans/implemented/).

## Catálogo

- [`auth-dashboard.md`](auth-dashboard.md): registro, acceso, perfil y dashboard.
- [`clients.md`](clients.md): clientes y aislamiento por despacho.
- [`matters.md`](matters.md): asuntos y todas las capacidades integradas en su detalle.
- [`documents-and-storage.md`](documents-and-storage.md): documentos, almacenamiento y extracción de texto.
- [`ai-configuration.md`](ai-configuration.md): configuración segura de credenciales BYOK.
- [`ai-assistance.md`](ai-assistance.md): funciones IA sobre el expediente, revisión y conversión
  en acciones.
- [`document-templates.md`](document-templates.md): catálogo, generación, copia y exportación de
  borradores.
- [`legal-and-ux.md`](legal-and-ux.md): avisos legales, accesibilidad y jerarquía de acciones.

## Convenciones

Cada capacidad debe usar las secciones `Propósito`, `Flujo principal`, `Límites y advertencias`,
`Permisos`, `Estados de error` y `Referencias técnicas`. No debe incluir comandos,
detalles de migración ni historial de decisiones salvo que sean necesarios para entender un
contrato funcional.

Cuando una capacidad cambie, se actualiza primero aquí y después el plan/backlog correspondiente.
