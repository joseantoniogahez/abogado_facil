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

## Mock y pruebas

`MockProvider(failure_code=...)` falla de forma determinista con cualquier miembro del catálogo. Esto
permite probar el mismo contrato que OpenAI y Gemini sin llamadas externas ni excepciones especiales
para el modo demostrativo.
