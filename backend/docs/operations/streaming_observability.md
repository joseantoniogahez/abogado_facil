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

Provider failures become the stable `error` event and `provider_error` code. The original exception
is intentionally not sent to the client.

## Verification

`backend/tests/test_streaming.py` covers lifecycle correlation, heartbeat delivery, safe provider
failure, cancellation propagation, iterator cleanup, and invalid heartbeat configuration.
