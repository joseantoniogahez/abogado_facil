# Minimizacion de contexto para IA

## Contrato obligatorio

Toda llamada a OpenAI, Gemini o Mock debe construir primero un `MinimizedAIContext` mediante
`build_minimized_ai_context`. `AiTextRequest` rechaza texto libre y cualquier valor que no cumpla
ese contrato.

La capa de producto que conoce al usuario, despacho y funcion declara:

- `authorized_fields`: campos que el principal puede usar en esa ejecucion;
- `necessary_fields`: subconjunto minimo requerido por la funcion;
- `source_context`: datos ya recuperados con aislamiento de despacho y usuario;
- `instruction`: instruccion estable de la funcion, sin secretos.

El constructor rechaza campos necesarios no autorizados o ausentes. Los campos disponibles pero no
necesarios no se copian ni se renderizan. La salida ordena los nombres de forma determinista y los
delimita dentro de `<authorized_context>`; esta delimitacion no sustituye el hardening contra prompt
injection de `SEC-004`.

## Limites

- hasta 20 campos por llamada;
- nombres `snake_case` de hasta 50 caracteres;
- instruccion de hasta 4,000 caracteres;
- cada valor de hasta 20,000 caracteres;
- payload renderizado total de hasta 60,000 caracteres;
- no se aceptan instrucciones, campos o valores vacios.

Los casos de uso futuros pueden imponer limites mas estrictos, pero no ampliar estos topes sin
actualizar contrato, pruebas y revision de riesgo.

## Seguridad y observabilidad

El contexto vive solamente en memoria durante la llamada. No se incluye en `AIJob`, RQ/Redis,
eventos de observabilidad, errores publicos ni logs. Los adaptadores registran unicamente
correlacion, proveedor, modelo, duracion y codigo de error normalizado.

La allowlist no concede autorizacion. La capa llamadora debe recuperar `source_context` usando el
`firm_id` y `user_id` del `AIJob`; luego debe declarar como autorizados solo los campos permitidos
para ese principal y esa funcion.
