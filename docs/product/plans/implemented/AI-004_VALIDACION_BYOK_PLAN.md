# AI-004 - Validación obligatoria de BYOK en funciones IA

## Estado

- ID: `AI-004`
- Tipo: Backend
- Prioridad: `P0-IA`
- Estado de implementación: `Hecho`
- Competencia de portafolio: `BE-AI`

## Entrega

Se añadió `AiProviderFactory`, que obtiene la credencial con aislamiento por usuario y despacho
antes de construir un adaptador OpenAI o Gemini. Credenciales ausentes, corruptas, vacías y
proveedores no soportados producen un error seguro y no instancian ningún proveedor.

## Validación y riesgo residual

Las pruebas unitarias cubren credencial válida, ausencia, corrupción, valor vacío y proveedor no
soportado. La fábrica aún debe conectarse a `AI-101` a `AI-103`; esos consumidores deberán recibirla
por DI. La validación de salida y el ciclo de vida de jobs permanecen en `AI-007` y `AI-009`.

## Remediación de revisión 2026-07-24

- [x] Una credencial AES-GCM con autenticación inválida se traduce a `InvalidInputError`.
- [x] La prueba usa ciphertext alterado y confirma que no se construye el proveedor.

## Cierre de remediación

- Validación: 431 pruebas backend con cobertura 100% y todos los hooks del repositorio pasan.
- Documentación revisada: error mapping y arquitectura backend actualizados; API, auth, RBAC y
  OpenAPI no cambiaron.
- Trabajo pendiente: ninguno dentro de AI-004.
- Riesgo residual: la fábrica aún debe conectarse a las funciones IA futuras.
