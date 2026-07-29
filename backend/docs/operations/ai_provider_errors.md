# Catálogo seguro de errores de proveedores de IA

## Contrato común

OpenAI, Gemini y Mock traducen sus fallos a `AiProviderError`. El error expone únicamente:

- `error_code`: código estable que puede persistirse en `AIJob.error_code`;
- un mensaje público constante en español;
- `retryable`: decisión explícita para la política de ejecución.

`to_public_failure()` produce el contrato seguro `code`, `message` y `retryable` que podrán consumir
futuros endpoints y el frontend. No contiene nombre del proveedor, URL, API key, cuerpo de respuesta,
mensaje externo, prompt ni contexto legal.

## Taxonomía

| Código                           | Recuperable | Significado seguro                                       |
| -------------------------------- | ----------- | -------------------------------------------------------- |
| `provider_authentication_failed` | no          | Credencial ausente de acceso o sin permisos suficientes  |
| `provider_rate_limited`          | sí          | Cuota o límite temporal alcanzado                        |
| `provider_timeout`               | sí          | Tiempo de espera agotado                                 |
| `provider_unavailable`           | sí          | Red o servicio externo temporalmente no disponible       |
| `provider_request_rejected`      | no          | Solicitud rechazada por un error no recuperable          |
| `provider_invalid_response`      | no          | Respuesta exitosa ausente, malformada o no interpretable |
| `provider_configuration_error`   | no          | Endpoint/configuración interna inválida                  |

Los códigos son provider-neutral. La interfaz no debe convertirlos de nuevo en mensajes específicos
de OpenAI o Gemini.

## Mapeo de transporte

| Entrada externa                          | Código normalizado               |
| ---------------------------------------- | -------------------------------- |
| HTTP `401` o `403`                       | `provider_authentication_failed` |
| HTTP `408` o `504`; timeout local        | `provider_timeout`               |
| HTTP `429`                               | `provider_rate_limited`          |
| HTTP `5xx` excepto `504`; fallo de red   | `provider_unavailable`           |
| Otros HTTP fuera de `2xx`                | `provider_request_rejected`      |
| JSON o estructura de respuesta no válida | `provider_invalid_response`      |
| URL no HTTPS, inválida o sin hostname    | `provider_configuration_error`   |

El mapeo usa estado y clase de fallo, nunca el cuerpo controlado por el proveedor. Esto evita que
detalles sensibles o no confiables crucen el adaptador. Un worker puede usar `retryable` para decidir
si RQ debe reintentar y debe persistir exclusivamente `error_code` al agotar los intentos.

La suite contractual multi-provider exige la misma decisión en OpenAI, Gemini y Mock:

- timeout y rate limit producen `retryable=True`;
- JSON o estructura de respuesta inválida produce `retryable=False`;
- el contrato público y los logs omiten clave, prompt, payload y detalle externo.

Esta clasificación no encola por sí sola. El handler captura cada `AiProviderError`, persiste como
fallo definitivo los casos no recuperables y sólo relanza los recuperables para activar el retry de
RQ.

El endpoint síncrono `POST /v1/matters/{matter_id}/ai/results` traduce
`provider_rate_limited` a la respuesta normalizada `429 rate_limited`, con el mensaje público
constante y `Retry-After: 60`. El código persistido en `AIJob.error_code` permanece como
`provider_rate_limited`. Los detalles y encabezados controlados por el proveedor no cruzan el
adaptador.

El mismo endpoint traduce todos los demás fallos del catálogo sin dejarlos escapar como excepciones
no controladas: credencial y solicitud rechazada usan `400`; respuesta inválida usa `502`;
indisponibilidad usa `503`; timeout usa `504`; y configuración interna usa `500`. La respuesta
conserva el código estable `provider_*` y el mensaje público constante.

Las funciones de asistencia que requieren resultados estructurados envían a Gemini el esquema JSON
esperado mediante `responseMimeType=application/json` y `responseJsonSchema`. El adaptador concatena
las partes textuales, ignora metadatos de pensamiento y el servicio vuelve a validar localmente el
JSON contra el esquema de la función antes de persistirlo.

## Mock y pruebas

`MockProvider(failure_code=...)` falla de forma determinista con cualquier miembro del catálogo. Esto
permite probar el mismo contrato que OpenAI y Gemini sin llamadas externas ni excepciones especiales
para el modo demostrativo.
