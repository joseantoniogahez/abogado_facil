# Catálogo reproducible de fallos y reintentos de IA

Este catálogo complementa el contrato normativo de
[`ai_provider_errors.md`](ai_provider_errors.md) con decisiones operativas y casos reproducibles.

| Código                           | Retry | Resultado HTTP síncrono | Reproducción determinista                                |
| -------------------------------- | ----- | ----------------------- | -------------------------------------------------------- |
| `provider_authentication_failed` | no    | 400                     | `MockProvider(failure_code=AUTHENTICATION_FAILED)`       |
| `provider_rate_limited`          | sí    | 429 + `Retry-After`     | `MockProvider(failure_code=RATE_LIMITED)`                |
| `provider_timeout`               | sí    | 504                     | `MockProvider(failure_code=TIMEOUT)`                     |
| `provider_unavailable`           | sí    | 503                     | `MockProvider(failure_code=UNAVAILABLE)`                 |
| `provider_request_rejected`      | no    | 400                     | `MockProvider(failure_code=REQUEST_REJECTED)`            |
| `provider_invalid_response`      | no    | 502                     | respuesta mock con JSON inválido o shape ajeno al schema |
| `provider_configuration_error`   | no    | 500                     | `MockProvider(failure_code=CONFIGURATION_ERROR)`         |

## Política de retry

Sólo rate limit, timeout e indisponibilidad son transitorios. Los endpoints síncronos actuales no
usan el retry de RQ y traducen el fallo al resultado HTTP de la tabla. Cuando se registre un
handler, éste deberá relanzar únicamente esos fallos y el scheduler aplicará
`AI_QUEUE_MAX_RETRIES` con `AI_QUEUE_RETRY_BACKOFF_SECONDS`. Los adapters no deben duplicar esa
política con retries propios. Autenticación, request rechazado, configuración y respuesta inválida
terminarán el job sin repetir ni intentar “reparar” el JSON. Un retry agotado persistirá sólo el
código normalizado.

## Escenarios mínimos antes de registrar un handler

1. Timeout y rate limit alcanzan el mecanismo de retry con los intervalos configurados.
1. JSON inválido falla una sola vez, no persiste texto crudo y no produce acción.
1. El mismo fallo genera código, mensaje público y decisión equivalentes en OpenAI, Gemini y Mock.
1. Logs y respuestas omiten API key, prompt, contexto, cuerpo externo y detalle del SDK.
1. Un reintento conserva `execution_id`; una regeneración solicitada por el usuario crea una nueva
   ejecución y enlaza el resultado anterior, por lo que no son el mismo concepto.
