# Frontend Mutation Policy Matrix

This document defines deterministic mutation retry and invalidation behavior by domain.

## Policy Matrix

| Domain                     | Retry Policy                                     | Invalidation Strategy                                  |
| -------------------------- | ------------------------------------------------ | ------------------------------------------------------ |
| Default mutation           | Retry only transient/network errors, max 1 retry | Caller-defined                                         |
| Auth login mutation        | No retry                                         | Set `SESSION_QUERY_KEY` and invalidate session query   |
| Auth logout mutation       | No retry                                         | Clear `SESSION_QUERY_KEY` and invalidate session query |
| Auth registration mutation | No retry                                         | Keep session unchanged; show explicit login transition |
| Profile update mutation    | No retry                                         | Write returned profile through `SESSION_QUERY_KEY`     |
| Client/matter mutation     | Default mutation policy                          | Explicit domain list/detail and dashboard invalidation |
| Matter note mutation       | Default mutation policy                          | Invalidate only the note list for its matter           |
| Matter document mutation   | Default mutation policy                          | Invalidate only the document list for its matter       |
| Matter checklist mutation  | Default mutation policy                          | Invalidate only the checklist for its matter           |
| Matter task mutation       | Default mutation policy                          | Invalidate its matter task list and dashboard summary  |
| Matter payment mutation    | Default mutation policy                          | Invalidate the payment summary for its matter          |

## Implementation References

- Mutation policies: `src/app/mutation-policy.ts`
- QueryClient defaults: `src/app/query-client.ts`
- Login mutation consumer: `src/features/auth/LoginPage.tsx`
- Registration mutation consumer: `src/features/auth/RegisterPage.tsx`
- Profile mutation consumer: `src/features/profile/ProfilePage.tsx`
- Logout mutation consumer: `src/shared/routing/RootLayout.tsx`
- Matter document mutations: `src/features/matters/matter-documents/api.ts`
- Matter checklist mutations: `src/features/matters/matter-checklist/api.ts`
- Matter task mutations: `src/features/matters/matter-tasks/api.ts`
- Matter payment mutations: `src/features/matters/matter-payments/api.ts`

## Failure Behavior Contract

- `401` and `409` mutation failures are non-retryable.
- Transient/network failures retry once under default mutation policy.
- Auth mutations never retry to avoid duplicate auth-side effects and confusing user state.
- Registration never writes an access token or authenticated user into the session cache.
- An unauthorized profile update clears the cached session; a successful update replaces the
  complete cached product account profile.
