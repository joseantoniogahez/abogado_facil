# Frontend API Consumer and Error Contract Matrix

This document is the canonical consumer-side inventory of backend endpoints used by the frontend.

## Endpoint Consumer Catalog

| Endpoint                                            | Method   | Consumer Module             | Consumer Function           | Auth Mode | Success Contract                               |
| --------------------------------------------------- | -------- | --------------------------- | --------------------------- | --------- | ---------------------------------------------- |
| `/token`                                            | `POST`   | `shared/auth/session.ts`    | `loginWithCredentials`      | `public`  | `access_token` + `token_type`                  |
| `/users/register`                                   | `POST`   | `shared/auth/session.ts`    | `registerUser`              | `public`  | product account profile; no implicit session   |
| `/users/me`                                         | `GET`    | `shared/auth/session.ts`    | `readCurrentUser`           | `bearer`  | product account profile + permissions snapshot |
| `/users/me`                                         | `PATCH`  | `shared/auth/session.ts`    | `updateCurrentUser`         | `bearer`  | updated product account profile + permissions  |
| `/audit-log`                                        | `GET`    | `features/audit-log/api.ts` | `readAuditLogEntries`       | `bearer`  | `AuditLogEntry[]`                              |
| `/dashboard`                                        | `GET`    | `features/dashboard/api.ts` | dashboard query             | `bearer`  | `DashboardSummary`                             |
| `/clients`                                          | `GET`    | `features/clients/api.ts`   | `clientsQueryOptions`       | `bearer`  | `ClientList`                                   |
| `/clients`                                          | `POST`   | `features/clients/api.ts`   | `createClient`              | `bearer`  | `ClientRecord`                                 |
| `/clients/{client_id}`                              | `GET`    | `features/clients/api.ts`   | `clientQueryOptions`        | `bearer`  | `ClientRecord`                                 |
| `/clients/{client_id}`                              | `PATCH`  | `features/clients/api.ts`   | `updateClient`              | `bearer`  | `ClientRecord`                                 |
| `/matters`                                          | `GET`    | `features/matters/api.ts`   | `mattersQueryOptions`       | `bearer`  | `MatterList`                                   |
| `/matters`                                          | `POST`   | `features/matters/api.ts`   | `createMatter`              | `bearer`  | `MatterRecord`                                 |
| `/matters/{matter_id}`                              | `GET`    | `features/matters/api.ts`   | `matterQueryOptions`        | `bearer`  | `MatterRecord`                                 |
| `/matters/{matter_id}`                              | `PATCH`  | `features/matters/api.ts`   | `updateMatter`              | `bearer`  | `MatterRecord`                                 |
| `/rbac/users`                                       | `GET`    | `shared/rbac/admin.ts`      | `readAdminUsers`            | `bearer`  | `AdminUser[]`                                  |
| `/rbac/users`                                       | `POST`   | `shared/rbac/admin.ts`      | `createAdminUser`           | `bearer`  | `AdminUser`                                    |
| `/rbac/users/{user_id}`                             | `GET`    | `shared/rbac/admin.ts`      | `readAdminUser`             | `bearer`  | `AdminUser`                                    |
| `/rbac/users/{user_id}/roles`                       | `GET`    | `shared/rbac/admin.ts`      | `readRbacUserRoles`         | `bearer`  | `AssignedRole[]`                               |
| `/rbac/users/{user_id}`                             | `PUT`    | `shared/rbac/admin.ts`      | `updateAdminUser`           | `bearer`  | `AdminUser`                                    |
| `/rbac/users/{user_id}`                             | `DELETE` | `shared/rbac/admin.ts`      | `softDeleteAdminUser`       | `bearer`  | `204 no-content`                               |
| `/rbac/roles`                                       | `GET`    | `shared/rbac/admin.ts`      | `readRbacRoles`             | `bearer`  | `RbacRole[]`                                   |
| `/rbac/roles`                                       | `POST`   | `shared/rbac/admin.ts`      | `createRbacRole`            | `bearer`  | `RbacRole`                                     |
| `/rbac/roles/{role_id}/users`                       | `GET`    | `shared/rbac/admin.ts`      | `readRbacRoleUsers`         | `bearer`  | `AssignedUser[]`                               |
| `/rbac/roles/{role_id}`                             | `PUT`    | `shared/rbac/admin.ts`      | `updateRbacRole`            | `bearer`  | `RbacRole`                                     |
| `/rbac/roles/{role_id}`                             | `DELETE` | `shared/rbac/admin.ts`      | `deleteRbacRole`            | `bearer`  | `204 no-content`                               |
| `/rbac/roles/{role_id}/inherits/{parent_role_id}`   | `PUT`    | `shared/rbac/admin.ts`      | `assignRbacRoleInheritance` | `bearer`  | `204 no-content`                               |
| `/rbac/roles/{role_id}/inherits/{parent_role_id}`   | `DELETE` | `shared/rbac/admin.ts`      | `removeRbacRoleInheritance` | `bearer`  | `204 no-content`                               |
| `/rbac/permissions`                                 | `GET`    | `shared/rbac/admin.ts`      | `readRbacPermissions`       | `bearer`  | `RbacPermission[]`                             |
| `/rbac/roles/{role_id}/permissions/{permission_id}` | `PUT`    | `shared/rbac/admin.ts`      | `assignRbacRolePermission`  | `bearer`  | `RbacRolePermission`                           |
| `/rbac/roles/{role_id}/permissions/{permission_id}` | `DELETE` | `shared/rbac/admin.ts`      | `removeRbacRolePermission`  | `bearer`  | `204 no-content`                               |
| `/rbac/users/{user_id}/roles/{role_id}`             | `PUT`    | `shared/rbac/admin.ts`      | `assignRbacUserRole`        | `bearer`  | `UserRoleAssignmentResponse`                   |
| `/rbac/users/{user_id}/roles/{role_id}`             | `DELETE` | `shared/rbac/admin.ts`      | `removeRbacUserRole`        | `bearer`  | `204 no-content`                               |

## Conditional Consumer Notes

- The product account profile contract is
  `{ id, email, first_name, middle_name, last_name, display_name, firm_name, disabled, permissions[] }`.

- Login sends normalized email through OAuth2's form field named `username`; this is a transport
  constraint, not a separate user-facing identity.

- Registration sends the name components and editable `display_name`; omitted `firm_name` is handled
  by the backend fallback and a successful registration leaves session state unchanged.

- Successful profile updates write the returned profile through `SESSION_QUERY_KEY` so email, names,
  display name, and firm name update together.

- Client forms display only the 10-digit Mexican national number. The fixed `+52` country code is
  implicit in the MVP, and non-digit formatting is removed before requests are sent.

- `readAuditLogEntries` is routed through `/admin/audit-log`, which requires `audit_logs:read` before the page can request the endpoint.

- `readRbacRoles` is permission-gated on `/admin/users`: the page only requests `/rbac/roles` when the current session has `roles:manage`; otherwise it hides role-related controls and does not send `role_ids`.

## Error Contract Matrix

| Endpoint            | Expected Error Codes                                                                                     | Request-ID Policy                                      | Frontend Handling Contract                                                                                                     |
| ------------------- | -------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| `/token`            | `invalid_input`, `unauthorized`, `forbidden`, `internal_error`, `network_error`                          | Use `X-Request-ID`/payload `request_id` when available | Show user-safe login error and append request-id diagnostic for support.                                                       |
| `/users/register`   | `invalid_input`, `conflict`, `internal_error`, `network_error`                                           | Use `X-Request-ID`/payload `request_id` when available | Show deterministic registration feedback, keep auth/session state unchanged, and expose diagnostics when available.            |
| `/users/me`         | `invalid_input`, `unauthorized`, `forbidden`, `conflict`, `internal_error`, `network_error`              | Use `X-Request-ID`/payload `request_id` when available | `GET` unauthorized clears session; successful `PATCH` writes through `SESSION_QUERY_KEY`; unauthorized `PATCH` clears session. |
| `/audit-log`        | `unauthorized`, `forbidden`, `network_error`, `internal_error`                                           | Use `X-Request-ID`/payload `request_id` when available | Show audit log error panel with backend detail and request-id diagnostic.                                                      |
| `/dashboard`        | `unauthorized`, `forbidden`, `network_error`, `internal_error`                                           | Use `X-Request-ID`/payload `request_id` when available | Protected session handling clears invalid tokens; recoverable errors show retry and request-id diagnostics.                    |
| `/clients*`         | `invalid_input`, `unauthorized`, `not_found`, `network_error`, `internal_error`                          | Use `X-Request-ID`/payload `request_id` when available | List errors offer retry; successful mutations invalidate client list/detail and dashboard summary.                             |
| `/matters*`         | `invalid_input`, `unauthorized`, `not_found`, `network_error`, `internal_error`                          | Use `X-Request-ID`/payload `request_id` when available | Lists support client filters; successful mutations invalidate matter queries and dashboard summary.                            |
| `/rbac/users*`      | `invalid_input`, `unauthorized`, `forbidden`, `not_found`, `conflict`, `network_error`, `internal_error` | Use `X-Request-ID`/payload `request_id` when available | Show admin error panel with backend detail and request-id diagnostic.                                                          |
| `/rbac/roles*`      | `invalid_input`, `unauthorized`, `forbidden`, `not_found`, `conflict`, `network_error`, `internal_error` | Use `X-Request-ID`/payload `request_id` when available | Keep page interactive; explicit-scope permission mutations surface diagnostics without silent fallback.                        |
| `/rbac/permissions` | `unauthorized`, `forbidden`, `network_error`, `internal_error`                                           | Use `X-Request-ID`/payload `request_id` when available | Permission catalog failures block role-permission actions and show diagnostics.                                                |

## Drift Control Rules

1. Endpoint additions/removals in frontend API consumers must update this matrix in the same PR.
1. Contract parser changes in `shared/api/contracts.ts`, `shared/auth/contracts.ts`, or `shared/rbac/contracts.ts` must reflect here when payload expectations change.
1. Error normalization behavior updates in `shared/api/errors.ts` must keep this matrix synchronized.
1. Role-permission assignment UI must send an explicit scope (`own`, `tenant`, or `any`) and must not rely on a client-side default.
