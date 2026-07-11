# API Endpoints

For implementation rules and extension workflows, see `../backend_playbook.md`.

All routes are versioned under `/v1`.

## Global Conventions

- Bearer auth header: `Authorization: Bearer <access_token>`.
- Standard error payload: `{ detail, status, code, meta?, request_id }`.
- Normalized error responses echo the same `request_id` in the `X-Request-ID` response header.
- Request validation errors are normalized to `400 invalid_input` (not exposed as `422`).
- Write endpoints (`POST`/`PUT`/`PATCH`/`DELETE`) run inside a Unit of Work transaction scope.

## Endpoint Summary

| Method   | Path                                                   | Auth | Permission                | Main Request Contract                                   | Success Response                   | Common Error Statuses                    |
| -------- | ------------------------------------------------------ | ---- | ------------------------- | ------------------------------------------------------- | ---------------------------------- | ---------------------------------------- |
| `GET`    | `/v1/audit-log`                                        | Yes  | `audit_logs:read`         | No body                                                 | `200` `AuditLogEntryResponse[]`    | `401`, `403`, `500`                      |
| `GET`    | `/v1/dashboard`                                        | Yes  | No                        | No body                                                 | `200` `DashboardSummaryResponse`   | `401`, `403`, `500`                      |
| `GET`    | `/v1/health`                                           | No   | No                        | No body                                                 | `200` `{ "status": "ok" }`         | -                                        |
| `POST`   | `/v1/token`                                            | No   | No                        | OAuth2 form (`username` carries email, plus `password`) | `200` bearer token                 | `400`, `401`, `403`, `500`               |
| `POST`   | `/v1/users/register`                                   | No   | No                        | JSON `RegisterUserRequest`                              | `201` `AuthenticatedUserResponse`  | `400`, `409`, `500`                      |
| `GET`    | `/v1/users/me`                                         | Yes  | No                        | No body                                                 | `200` `AuthenticatedUserResponse`  | `401`, `403`, `500`                      |
| `PATCH`  | `/v1/users/me`                                         | Yes  | No                        | JSON `UpdateCurrentUserRequest`                         | `200` `AuthenticatedUserResponse`  | `400`, `401`, `403`, `409`, `500`        |
| `GET`    | `/v1/rbac/roles`                                       | Yes  | `roles:manage`            | No body                                                 | `200` `RBACRole[]`                 | `401`, `403`, `500`                      |
| `GET`    | `/v1/rbac/permissions`                                 | Yes  | `role_permissions:manage` | No body                                                 | `200` `RBACPermission[]`           | `401`, `403`, `500`                      |
| `GET`    | `/v1/rbac/users`                                       | Yes  | `users:manage`            | No body                                                 | `200` `AdminUserResponse[]`        | `401`, `403`, `500`                      |
| `GET`    | `/v1/rbac/users/{user_id}`                             | Yes  | `users:manage`            | Path `user_id`                                          | `200` `AdminUserResponse`          | `400`, `401`, `403`, `404`, `500`        |
| `GET`    | `/v1/rbac/users/{user_id}/roles`                       | Yes  | `user_roles:manage`       | Path `user_id`                                          | `200` `AssignedRole[]`             | `400`, `401`, `403`, `404`, `500`        |
| `GET`    | `/v1/rbac/roles/{role_id}/users`                       | Yes  | `user_roles:manage`       | Path `role_id`                                          | `200` `AssignedUser[]`             | `400`, `401`, `403`, `404`, `500`        |
| `POST`   | `/v1/rbac/users`                                       | Yes  | `users:manage`            | JSON `CreateAdminUserRequest`                           | `201` `AdminUserResponse`          | `400`, `401`, `403`, `404`, `409`, `500` |
| `PUT`    | `/v1/rbac/users/{user_id}`                             | Yes  | `users:manage`            | Path `user_id` + JSON `UpdateAdminUserRequest`          | `200` `AdminUserResponse`          | `400`, `401`, `403`, `404`, `409`, `500` |
| `DELETE` | `/v1/rbac/users/{user_id}`                             | Yes  | `users:manage`            | Path `user_id`                                          | `204` no body                      | `400`, `401`, `403`, `404`, `500`        |
| `POST`   | `/v1/rbac/roles`                                       | Yes  | `roles:manage`            | JSON `CreateRoleRequest`                                | `201` `RBACRole`                   | `400`, `401`, `403`, `409`, `500`        |
| `PUT`    | `/v1/rbac/roles/{role_id}`                             | Yes  | `roles:manage`            | Path `role_id` + JSON `UpdateRoleRequest`               | `200` `RBACRole`                   | `400`, `401`, `403`, `404`, `409`, `500` |
| `DELETE` | `/v1/rbac/roles/{role_id}`                             | Yes  | `roles:manage`            | Path `role_id`                                          | `204` no body                      | `400`, `401`, `403`, `404`, `500`        |
| `PUT`    | `/v1/rbac/roles/{role_id}/inherits/{parent_role_id}`   | Yes  | `roles:manage`            | Path `role_id` + `parent_role_id`                       | `204` no body                      | `400`, `401`, `403`, `404`, `409`, `500` |
| `DELETE` | `/v1/rbac/roles/{role_id}/inherits/{parent_role_id}`   | Yes  | `roles:manage`            | Path `role_id` + `parent_role_id`                       | `204` no body                      | `400`, `401`, `403`, `404`, `500`        |
| `PUT`    | `/v1/rbac/roles/{role_id}/permissions/{permission_id}` | Yes  | `role_permissions:manage` | Path IDs + JSON `SetRolePermissionRequest`              | `200` `RBACRolePermission`         | `400`, `401`, `403`, `404`, `500`        |
| `DELETE` | `/v1/rbac/roles/{role_id}/permissions/{permission_id}` | Yes  | `role_permissions:manage` | Path `role_id` + `permission_id`                        | `204` no body                      | `400`, `401`, `403`, `404`, `500`        |
| `PUT`    | `/v1/rbac/users/{user_id}/roles/{role_id}`             | Yes  | `user_roles:manage`       | Path `user_id` + `role_id`                              | `200` `UserRoleAssignmentResponse` | `400`, `401`, `403`, `404`, `500`        |
| `DELETE` | `/v1/rbac/users/{user_id}/roles/{role_id}`             | Yes  | `user_roles:manage`       | Path `user_id` + `role_id`                              | `204` no body                      | `400`, `401`, `403`, `404`, `500`        |

Protected rows (`Permission != No`) are contract-checked by
`tests/routers/test_authorization_policy_coverage.py`.

## Read Access Classification

This table classifies each `GET` endpoint as `public`, `authenticated`, or `permission`.

| Method | Path                             | Access Level    | Permission                |
| ------ | -------------------------------- | --------------- | ------------------------- |
| `GET`  | `/v1/audit-log`                  | `permission`    | `audit_logs:read`         |
| `GET`  | `/v1/dashboard`                  | `authenticated` | No                        |
| `GET`  | `/v1/health`                     | `public`        | No                        |
| `GET`  | `/v1/users/me`                   | `authenticated` | No                        |
| `GET`  | `/v1/rbac/roles`                 | `permission`    | `roles:manage`            |
| `GET`  | `/v1/rbac/permissions`           | `permission`    | `role_permissions:manage` |
| `GET`  | `/v1/rbac/users`                 | `permission`    | `users:manage`            |
| `GET`  | `/v1/rbac/users/{user_id}`       | `permission`    | `users:manage`            |
| `GET`  | `/v1/rbac/users/{user_id}/roles` | `permission`    | `user_roles:manage`       |
| `GET`  | `/v1/rbac/roles/{role_id}/users` | `permission`    | `user_roles:manage`       |

## Domain Notes

### Authentication

- `POST /v1/token` uses FastAPI `OAuth2PasswordRequestForm`.
- `POST /v1/users/register` requires `first_name`, `last_name`, `display_name`, `email`, and
  `password`; accepts optional `middle_name` and `firm_name`; normalizes email; creates exactly one
  firm; and assigns `account_owner` atomically. When `firm_name` is omitted, the persisted firm name
  falls back to `display_name`.
- The OAuth2 form field for `POST /v1/token` remains named `username` for protocol compatibility,
  but its value is the account email and the JWT subject is the normalized email.
- `PATCH /v1/users/me` supports legal-name components, display name, email, firm name, and password updates.
- `GET /v1/dashboard` resolves the firm from the authenticated principal and accepts no client-selected firm identifier.
- `POST /v1/users/register`, `GET /v1/users/me`, and `PATCH /v1/users/me` return
  `AuthenticatedUserResponse` with deterministic `permissions` (sorted unique effective permission ids from direct
  and inherited roles).

### RBAC

- `GET /v1/rbac/users` and `GET /v1/rbac/users/{user_id}` expose admin user management views including assigned `role_ids`.
- `POST /v1/rbac/users` creates users with email normalization, password policy enforcement, product
  name fields, firm association, and optional role assignments.
- `PUT /v1/rbac/users/{user_id}` supports email, product name fields, firm association, password,
  disabled status, and full role-set replacement updates.
- `DELETE /v1/rbac/users/{user_id}` performs logical deletion only by setting `disabled=true`.
- `GET /v1/rbac/roles` returns effective permissions (direct + inherited) and direct `parent_role_ids`.
- `PUT /v1/rbac/roles/{role_id}/inherits/{parent_role_id}` manages role inheritance.
- `PUT /v1/rbac/roles/{role_id}/permissions/{permission_id}` is an upsert operation.
- `PUT /v1/rbac/roles/{role_id}/permissions/{permission_id}` requires an explicit `scope` in `SetRolePermissionRequest`; omitted scope is rejected as `400 invalid_input`.
- `GET /v1/rbac/users/{user_id}/roles` returns direct user-role assignments.
- `GET /v1/rbac/roles/{role_id}/users` returns direct role-user assignments.
- `DELETE /v1/rbac/roles/{role_id}` also removes related role links and user-role assignments.

### Audit Log

- `GET /v1/audit-log` returns the most recent audit log entries for administrator review.
- Access requires `audit_logs:read`.
- The current feature exposes existing audit rows only; automatic event capture is intentionally out of scope.
