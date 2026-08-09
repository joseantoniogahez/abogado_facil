# Ciclo de vida persistente de ejecuciones de IA

## Alcance

`app.features.ai_jobs` registra ejecuciones de IA como una capacidad backend interna. No expone un
router ni ejecuta proveedores por sí misma. Las funciones actuales de asistencia y borradores crean
y transicionan un `AIJob` mediante el servicio antes de persistir o mostrar un resultado; cualquier
función nueva debe conservar el mismo gate.

## Datos y aislamiento

Cada job conserva:

- `execution_id` opaco y único, además del `request_id` de la solicitud;
- `firm_id` y `user_id`, obligatorios en toda lectura y mutación;
- función, proveedor, modelo, versión de prompt y versión de schema;
- estado, número de intentos y timestamps de inicio/finalización;
- resultado JSON estructurado o un código de error seguro.

No se almacenan prompts, credenciales, texto de documentos, respuestas sin validar ni mensajes de
error del proveedor. Las consultas sin coincidencia exacta de despacho y usuario se comportan como
recurso inexistente.

Cada creación y transición emite un evento `ai_job_*` con `request_id`, `execution_id`, estado e
intento. Los eventos de fallo añaden sólo el `error_code` normalizado. Resultado, prompt, texto
documental y mensajes de excepción quedan fuera del log.

## Estados y transiciones

| Estado origen | Transición permitida  | Estado destino |
| ------------- | --------------------- | -------------- |
| `queued`      | iniciar               | `running`      |
| `queued`      | cancelar              | `cancelled`    |
| `running`     | completar             | `succeeded`    |
| `running`     | fallar                | `failed`       |
| `running`     | cancelar              | `cancelled`    |
| `failed`      | iniciar nuevo intento | `running`      |

`succeeded` y `cancelled` son terminales. Cada inicio incrementa `attempt_count`. Las transiciones
bloquean la fila dentro de Unit of Work y rechazan estados incompatibles. Un job exitoso exige
resultado y no permite error; un job fallido exige `error_code` y no permite resultado.
Además, `AIJobsService.succeed` sólo acepta `ValidatedAIOutput` producido por
`validate_ai_output`, y su `schema_version` debe coincidir con la registrada en el job.

## Límites de responsabilidad

- `AI-010` define en `rq_ai_queue.md` la política de retry, backoff y prevención de duplicados.
- `AI-011` define en `ai_provider_errors.md` la taxonomía cerrada que alimenta `error_code`; un
  worker persiste el código normalizado y nunca el mensaje o cuerpo externo.
- `OBS-001` conecta la correlación persistente con RQ y los adaptadores; cada worker futuro debe
  recuperar el par desde este registro antes de llamar al proveedor.
- Los endpoints de producto deciden qué resultados estructurados están autorizados y validados.
- `AI-007` exige en `structured_ai_outputs.md` validación y versión coincidente antes de persistir,
  mostrar, copiar o exportar un resultado.
- `AI-008` exige en `ai_context_minimization.md` que cada caller use datos aislados y que
  `AiTextRequest` reciba solo campos autorizados y necesarios mediante `MinimizedAIContext`; un
  futuro worker deberá reconstruirlos desde PostgreSQL con el scope persistido.
