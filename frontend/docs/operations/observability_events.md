# Frontend Observability Event Contract

This document defines the standardized frontend observability schema for API, routing, and runtime diagnostics.

## Event Schema

Required fields:

- `event_name`: stable event identifier.
- `level`: `info` | `warn` | `error`.
- `timestamp`: ISO-8601 timestamp emitted at event time.
- `request_id`: backend correlation id when available; otherwise `null`.
- `context`: metadata map that must be redaction-safe before emission.

## Redaction Rules

- Sensitive keys are redacted before logging:
  - `authorization`
  - `password`
  - `token`
  - `access_token`

The current sanitizer matches those key names recursively. It does not redact sensitive substrings
inside arbitrary string values, URLs, error messages, or query parameters.

## Current Repository Gap

- `src/shared/api/http.ts` emits the complete request `path` on API failures.
- Some consumers include user-entered values in that path. In particular,
  `src/features/clients/api.ts` places the client search term in `?search=...`.
- Consequently, a failed client search can write a client name or phone number to the browser
  console even though the event schema requires redaction-safe context.

Treat current frontend console diagnostics as potentially sensitive and do not forward them to an
external collector or support artifact without review. Remediation requires normalizing logged
paths to a pathname or route template, excluding query values, and adding a regression test; this
documentation change does not claim that remediation is implemented.

## Core Event Names

- `api.request.network_error`
- `api.request.response_error`
- `routing.protected.error`
- `routing.route_error`
- `runtime.error`
- `runtime.unhandled_rejection`

## References

- Event emitter: `src/shared/observability/events.ts`
- Event tests: `src/shared/observability/events.test.ts`
- API diagnostic emission: `src/shared/api/http.ts`
- Search consumer containing user input: `src/features/clients/api.ts`
