# Configuración de IA BYOK

## Propósito

Permitir que cada usuario configure credenciales propias para funciones IA sin exponer sus secretos.

## Flujo principal

- Configurar una API key propia para OpenAI o Google Gemini desde `/settings/ai`.
- Elegir un proveedor mediante un onboarding guiado con instrucciones específicas, advertencia de
  costo y tratamiento seguro de la clave.
- Consultar qué proveedores tienen una credencial configurada sin recuperar ni mostrar el secreto.
- Comprobar la conexión después del guardado consultando los modelos disponibles para esa
  credencial; un fallo ofrece reintento o reemplazo sin exponer el secreto.
- Reemplazar una credencial existente y eliminarla cuando deje de utilizarse.
- Recorrer una demostración local identificada como mock, sin clave, persistencia, llamadas a
  OpenAI/Gemini ni consumo de saldo.
- Mantener cada credencial asociada al usuario y despacho de la sesión.

## Reglas funcionales

- Las API keys se envían únicamente al backend y se almacenan cifradas.
- La respuesta de la API contiene estado y fechas, nunca la clave original ni el valor cifrado.
- Guardar una clave confirma persistencia. La pantalla realiza después una comprobación separada
  mediante el catálogo dinámico; descubrir modelos confirma acceso de listado, no garantiza cuota
  ni disponibilidad de una generación posterior.
- Antes de construir un proveedor para una función de IA, el backend exige una credencial
  configurada y descifrable para el usuario y despacho actuales.
- Las funciones de asistencia y borradores pueden enviar al proveedor únicamente el contexto
  autorizado que el usuario confirma en la vista previa; su release sigue bloqueado por los gates
  P0-IA pendientes.

## Límites y advertencias

- La comprobación de modelos puede fallar por conectividad, permisos, cuota o cambios del proveedor
  y se reintenta únicamente por acción explícita.
- La aplicación nunca vuelve a mostrar la clave original ni el valor cifrado.
- El recorrido mock es educativo y no representa una respuesta real ni asesoría jurídica.

## Permisos

- Consultar, guardar, reemplazar o eliminar credenciales requiere sesión autenticada.
- Cada credencial queda limitada al usuario y despacho actuales.

## Estados de error

- Un proveedor no admitido o una clave inválida no se persiste como configuración utilizable.
- Una credencial ausente o indescifrable bloquea la ejecución IA sin exponer detalles sensibles.

## Referencias técnicas

- [AI-001](../plans/implemented/AI-001_CREDENCIALES_BYOK_PLAN.md)
- [AI-002](../plans/implemented/AI-002_PANTALLA_CONFIGURACION_IA_PLAN.md)
- [AI-003](../plans/implemented/AI-003_MULTI_PROVIDER_PLAN.md)
- [AI-004](../plans/implemented/AI-004_VALIDACION_BYOK_PLAN.md)
- [AI-005](../plans/implemented/AI-005_POLITICA_LOGS_DATOS_SENSIBLES_PLAN.md)
- [AI-013](../plans/implemented/AI-013_DESCUBRIMIENTO_MODELOS_BYOK_PLAN.md)
- [UX-AI-002](../plans/implemented/UX-AI-002_ONBOARDING_BYOK_GUIADO_PLAN.md)
