# Frontend Runtime Configuration Contract

This document defines the build-time Vite configuration contract that frontend startup and API
utilities validate when the generated bundle runs in the browser.

## Required Configuration

| Variable             | Purpose            | Validation Rule                                                                                                        | Default                 |
| -------------------- | ------------------ | ---------------------------------------------------------------------------------------------------------------------- | ----------------------- |
| `VITE_API_ORIGIN`    | Backend API origin | Must be a valid `http` or `https` URL                                                                                  | `http://localhost:8000` |
| `VITE_API_BASE_PATH` | API prefix path    | Must be a non-empty string without spaces; normalized to a leading-slash path, and `/` collapses to an empty base path | `/v1`                   |

## Fail-Fast Behavior

- Frontend startup calls `readFrontendEnvConfig()` from `src/shared/api/env.ts`.
- Invalid configuration throws `FrontendEnvError` and blocks runtime boot.
- API URL builders (`getApiBaseUrl`, `buildApiUrl`) use the same validated config path.

## Build-Time Delivery

- Vite resolves `VITE_API_ORIGIN` and `VITE_API_BASE_PATH` while building the static bundle.
- Changing those variables on an already-built production container does not reconfigure its
  JavaScript. Rebuild the frontend image or bundle after changing either value.
- `compose.yaml` passes both values as frontend build arguments. Its repeated container environment
  values do not replace the values already embedded in the static assets.

## Validation References

- Contract tests: `src/shared/api/env.test.ts`
- Runtime bootstrap: `src/main.tsx`
