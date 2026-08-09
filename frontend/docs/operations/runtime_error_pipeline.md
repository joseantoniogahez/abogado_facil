# Frontend Global Runtime Error Pipeline

This document defines the global capture behavior for uncaught runtime errors and unhandled promise rejections.

## Scope

- `window.error` events
- `window.unhandledrejection` events

## Behavior Contract

- Handlers are installed once at app bootstrap (`src/main.tsx`).
- Captured failures emit structured observability events through `src/shared/observability/events.ts`.
- Correlation behavior:
  - If the runtime failure value is directly an `ApiError`, `request_id` is propagated.
  - Wrapped errors and `Error.cause` chains are not traversed by the current implementation.
  - Otherwise, `request_id` is logged as `null`.

## Implementation and Tests

- Implementation: `src/shared/observability/runtime-errors.ts`
- Tests: `src/shared/observability/runtime-errors.test.ts`
