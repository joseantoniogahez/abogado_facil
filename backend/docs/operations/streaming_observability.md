# Streaming y observabilidad para IA

This contract defines the backend transport pattern available to future AI provider features. It
does not call a provider or expose an AI endpoint by itself.

## Transport

Future AI responses use Server-Sent Events through `stream_ai_events` in
`app.core.common.streaming`. The provider adapter supplies an async iterable of chunks; the shared
wrapper owns lifecycle events, correlation, heartbeats, safe failures, and cancellation.

Every event has an opaque SSE `id` in the form `<execution_id>:<sequence>` and uses one of these
event names:

| Event       | Data contract                                |
| ----------- | -------------------------------------------- |
| `started`   | `execution_id`                               |
| `delta`     | `sequence`, provider chunk under `data`      |
| `heartbeat` | `execution_id`                               |
| `completed` | `execution_id`, emitted `chunks`             |
| `error`     | `execution_id`, stable `code=provider_error` |

The wrapper emits heartbeats while waiting for a provider chunk. Disconnect cancellation is
propagated to the consumer and closes the provider iterator; no synthetic success or error event
is emitted after the client has disconnected.

## Correlation and redaction

The caller provides the HTTP `request_id`; the wrapper creates or accepts an opaque
`execution_id`. Logs include only `request_id`, `execution_id`, lifecycle event, duration, chunk
count, and exception type. Prompts, provider responses, document text, credentials, and provider
exception messages must not be logged.

`app.features.ai_jobs` persists the same `request_id` and `execution_id` pair for execution
lifecycles. A future SSE endpoint must pass the job's existing `execution_id` to
`stream_ai_events`; it must not create a second identifier for the same provider call.

`AiCorrelationContext` is the shared log contract. Both identifiers are bounded to 100 characters
and accept only letters, digits, `.`, `_`, `:`, and `-`. The HTTP middleware preserves a valid
incoming `X-Request-ID`; an empty or unsafe value is replaced with a server-generated 32-character
hex ID before it reaches state, persistence, responses, or logs.

## Correlated execution events

All events below include `request_id` and `execution_id` through `log_ai_event`:

| Layer         | Stable events                                                                               | Additional safe fields                               |
| ------------- | ------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| `ai_job`      | `ai_job_created`, `ai_job_started`, `ai_job_succeeded`, `ai_job_failed`, `ai_job_cancelled` | `status`, `attempt_count`, optional `error_code`     |
| `ai_queue`    | `ai_job_enqueued`, `ai_job_duplicate`, `ai_job_enqueue_failed`                              | allowlisted `job_name`, optional `error_type`        |
| `ai_provider` | `ai_provider_started`, `ai_provider_succeeded`, `ai_provider_failed`                        | provider, model, duration, normalized error metadata |
| `ai_stream`   | `ai_stream_started`, `ai_stream_completed`, `ai_stream_failed`, `ai_stream_cancelled`       | duration, chunks, optional `error_type`              |

Future workers receive only `execution_id` from RQ. Before provider work they must load the
tenant-scoped `AIJob`, call `AIJobsService.start`, and construct provider requests with the
persisted `request_id` and `execution_id`. They complete through `succeed` or `fail`; workers must
not invent a request ID or read one from Redis.

Provider failures become the stable `error` event and `provider_error` code. The original exception
is intentionally not sent to the client.

## Verification

`backend/tests/test_streaming.py` covers lifecycle correlation, heartbeat delivery, safe provider
failure, cancellation propagation, iterator cleanup, and invalid heartbeat configuration.
