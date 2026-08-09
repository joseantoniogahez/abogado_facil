# Frontend Mutation Policy Matrix

This document defines deterministic mutation retry and invalidation behavior by domain.

## Policy Matrix

| Domain                     | Retry Policy                                     | Invalidation Strategy                                                                                                                                               |
| -------------------------- | ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Default mutation           | Retry only transient/network errors, max 1 retry | Caller-defined                                                                                                                                                      |
| Auth login mutation        | No retry                                         | Set `SESSION_QUERY_KEY` and invalidate session query                                                                                                                |
| Auth logout mutation       | No retry                                         | Clear `SESSION_QUERY_KEY` and invalidate session query                                                                                                              |
| Auth registration mutation | No retry                                         | Keep session unchanged; show explicit login transition                                                                                                              |
| Profile update mutation    | No retry                                         | Write returned profile through `SESSION_QUERY_KEY`                                                                                                                  |
| AI credential mutation     | No retry                                         | Invalidate `AI_CREDENTIALS_QUERY_KEY` and `AI_MODELS_QUERY_KEY`                                                                                                     |
| Client/matter mutation     | Default mutation policy                          | Explicit domain list/detail and dashboard invalidation                                                                                                              |
| Matter note mutation       | Default mutation policy                          | Invalidate only the note list for its matter                                                                                                                        |
| Matter document mutation   | Default mutation policy                          | Invalidate only the document list for its matter                                                                                                                    |
| Matter checklist mutation  | Default mutation policy                          | Invalidate only the checklist for its matter                                                                                                                        |
| Matter task mutation       | Default mutation policy                          | Invalidate its matter task list and dashboard summary                                                                                                               |
| Matter payment mutation    | Default mutation policy                          | Invalidate the payment summary for its matter                                                                                                                       |
| Matter calculation save    | Default mutation policy                          | Invalidate saved calculations for its matter                                                                                                                        |
| Matter AI assistance       | Default mutation policy                          | Preview input changes clear its signed confirmation; execution/review invalidate AI results; conversion also invalidates the created note, task or checklist domain |

## Implementation References

- Mutation policies: `src/app/mutation-policy.ts`
- QueryClient defaults: `src/app/query-client.ts`
- Login mutation consumer: `src/features/auth/LoginPage.tsx`
- Registration mutation consumer: `src/features/auth/RegisterPage.tsx`
- Profile mutation consumer: `src/features/profile/ProfilePage.tsx`
- AI credential mutations: `src/features/ai-settings/AiSettingsPage.tsx`
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
- AI credential mutations do not retry automatically, clear stale action feedback before each
  attempt, and refresh provider status and the dynamic model catalog after success. The AI settings
  connection check also uses explicit user retry so credential, permission, or quota failures are
  visible and actionable.

## Current Contract Violation

The default retry function is currently inherited by non-idempotent writes, including the
`POST /matters/{matter_id}/payments` consumer. A network failure can occur after the backend has
accepted a write but before the browser receives the response; retrying that request without an
idempotency key can create a duplicate payment or another duplicate resource.

The required invariant is:

- non-idempotent mutations must not retry automatically unless end-to-end idempotency is proven;
- explicit user retry must remain available for recoverable failures;
- idempotent operations may opt into a bounded retry after their backend contract is verified.

The current implementation does not yet satisfy this invariant. This is a code/contract remediation
item; the table above records current behavior and must not be interpreted as approving automatic
retry for non-idempotent writes.

Evidence:

- Default retry implementation: `src/app/mutation-policy.ts`
- Payment consumer: `src/features/matters/matter-payments/MatterPayments.tsx`
- Payment request functions: `src/features/matters/matter-payments/api.ts`
