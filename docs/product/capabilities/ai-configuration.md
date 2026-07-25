# Configuración de IA BYOK

## Capacidades disponibles

- Configurar una API key propia para OpenAI o Google Gemini desde `/settings/ai`.
- Consultar qué proveedores tienen una credencial configurada sin recuperar ni mostrar el secreto.
- Reemplazar una credencial existente y eliminarla cuando deje de utilizarse.
- Mantener cada credencial asociada al usuario y despacho de la sesión.

## Reglas funcionales

- Las API keys se envían únicamente al backend y se almacenan cifradas.
- La respuesta de la API contiene estado y fechas, nunca la clave original ni el valor cifrado.
- Guardar una clave confirma persistencia, pero no realiza una prueba de conexión contra el
  proveedor.
- Antes de construir un proveedor para una función de IA, el backend exige una credencial
  configurada y descifrable para el usuario y despacho actuales.
- Todavía no existen funciones de producto que envíen asuntos, notas o documentos a proveedores
  externos.

## Referencias técnicas

- [AI-001](../plans/implemented/AI-001_CREDENCIALES_BYOK_PLAN.md)
- [AI-002](../plans/implemented/AI-002_PANTALLA_CONFIGURACION_IA_PLAN.md)
- [AI-003](../plans/implemented/AI-003_MULTI_PROVIDER_PLAN.md)
- [AI-004](../plans/implemented/AI-004_VALIDACION_BYOK_PLAN.md)
- [AI-005](../plans/implemented/AI-005_POLITICA_LOGS_DATOS_SENSIBLES_PLAN.md)
