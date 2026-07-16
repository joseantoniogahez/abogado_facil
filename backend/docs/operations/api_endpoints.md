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

| Method   | Path                                                       | Auth | Permission                | Main Request Contract                                   | Success Response                   | Common Error Statuses                    |
| -------- | ---------------------------------------------------------- | ---- | ------------------------- | ------------------------------------------------------- | ---------------------------------- | ---------------------------------------- |
| `GET`    | `/v1/audit-log`                                            | Yes  | `audit_logs:read`         | No body                                                 | `200` `AuditLogEntryResponse[]`    | `401`, `403`, `500`                      |
| `GET`    | `/v1/dashboard`                                            | Yes  | No                        | No body                                                 | `200` `DashboardSummaryResponse`   | `401`, `403`, `500`                      |
| `GET`    | `/v1/health`                                               | No   | No                        | No body                                                 | `200` `{ "status": "ok" }`         | -                                        |
| `POST`   | `/v1/token`                                                | No   | No                        | OAuth2 form (`username` carries email, plus `password`) | `200` bearer token                 | `400`, `401`, `403`, `500`               |
| `POST`   | `/v1/users/register`                                       | No   | No                        | JSON `RegisterUserRequest`                              | `201` `AuthenticatedUserResponse`  | `400`, `409`, `500`                      |
| `GET`    | `/v1/users/me`                                             | Yes  | No                        | No body                                                 | `200` `AuthenticatedUserResponse`  | `401`, `403`, `500`                      |
| `POST`   | `/v1/clients`                                              | Yes  | No                        | JSON `CreateClientRequest`                              | `201` `ClientResponse`             | `400`, `401`, `500`                      |
| `GET`    | `/v1/clients`                                              | Yes  | No                        | Query `search`, `limit`, `offset`                       | `200` `ClientListResponse`         | `400`, `401`, `500`                      |
| `GET`    | `/v1/clients/{client_id}`                                  | Yes  | No                        | Path `client_id`                                        | `200` `ClientResponse`             | `400`, `401`, `404`, `500`               |
| `PATCH`  | `/v1/clients/{client_id}`                                  | Yes  | No                        | Path `client_id` + JSON `UpdateClientRequest`           | `200` `ClientResponse`             | `400`, `401`, `404`, `500`               |
| `POST`   | `/v1/matters`                                              | Yes  | No                        | JSON `CreateMatterRequest`                              | `201` `MatterResponse`             | `400`, `401`, `404`, `500`               |
| `GET`    | `/v1/matters`                                              | Yes  | No                        | Query `client_id`, `limit`, `offset`                    | `200` `MatterListResponse`         | `400`, `401`, `404`, `500`               |
| `GET`    | `/v1/matters/types`                                        | Yes  | No                        | No body                                                 | `200` `MatterTypeResponse[]`       | `401`, `500`                             |
| `GET`    | `/v1/matters/{matter_id}`                                  | Yes  | No                        | Path `matter_id`                                        | `200` `MatterResponse`             | `400`, `401`, `404`, `500`               |
| `PATCH`  | `/v1/matters/{matter_id}`                                  | Yes  | No                        | Path `matter_id` + JSON `UpdateMatterRequest`           | `200` `MatterResponse`             | `400`, `401`, `404`, `500`               |
| `POST`   | `/v1/matters/{matter_id}/notes`                            | Yes  | No                        | JSON `CreateMatterNoteRequest`                          | `201` `MatterNoteResponse`         | `400`, `401`, `404`, `500`               |
| `GET`    | `/v1/matters/{matter_id}/notes`                            | Yes  | No                        | Path `matter_id`                                        | `200` `MatterNoteListResponse`     | `400`, `401`, `404`, `500`               |
| `PATCH`  | `/v1/matters/{matter_id}/notes/{note_id}`                  | Yes  | No                        | JSON `UpdateMatterNoteRequest`                          | `200` `MatterNoteResponse`         | `400`, `401`, `404`, `500`               |
| `DELETE` | `/v1/matters/{matter_id}/notes/{note_id}`                  | Yes  | No                        | Path identifiers                                        | `204` no body                      | `400`, `401`, `404`, `500`               |
| `GET`    | `/v1/matters/{matter_id}/checklist`                        | Yes  | No                        | Path `matter_id`                                        | `200` `ChecklistResponse`          | `400`, `401`, `404`, `500`               |
| `POST`   | `/v1/matters/{matter_id}/checklist`                        | Yes  | No                        | JSON `CreateChecklistItemRequest`                       | `201` `ChecklistItemResponse`      | `400`, `401`, `404`, `500`               |
| `PATCH`  | `/v1/matters/{matter_id}/checklist/{item_id}`              | Yes  | No                        | JSON `UpdateChecklistItemRequest`                       | `200` `ChecklistItemResponse`      | `400`, `401`, `404`, `500`               |
| `GET`    | `/v1/matters/{matter_id}/tasks`                            | Yes  | No                        | Path `matter_id`                                        | `200` `MatterTaskListResponse`     | `400`, `401`, `404`, `500`               |
| `POST`   | `/v1/matters/{matter_id}/tasks`                            | Yes  | No                        | JSON `CreateMatterTaskRequest`                          | `201` `MatterTaskResponse`         | `400`, `401`, `404`, `500`               |
| `PATCH`  | `/v1/matters/{matter_id}/tasks/{task_id}`                  | Yes  | No                        | JSON `UpdateMatterTaskRequest`                          | `200` `MatterTaskResponse`         | `400`, `401`, `404`, `500`               |
| `POST`   | `/v1/matters/{matter_id}/documents`                        | Yes  | No                        | Multipart `document_type` + PDF/DOCX/TXT `file`         | `201` `MatterDocumentResponse`     | `400`, `401`, `404`, `409`, `500`        |
| `GET`    | `/v1/matters/{matter_id}/documents`                        | Yes  | No                        | Path `matter_id`                                        | `200` `MatterDocumentListResponse` | `400`, `401`, `404`, `500`               |
| `GET`    | `/v1/matters/{matter_id}/documents/{document_id}/download` | Yes  | No                        | Path identifiers                                        | `200` streamed attachment          | `400`, `401`, `404`, `500`               |
| `DELETE` | `/v1/matters/{matter_id}/documents/{document_id}`          | Yes  | No                        | Path identifiers                                        | `204` no body                      | `400`, `401`, `404`, `500`               |
| `PATCH`  | `/v1/users/me`                                             | Yes  | No                        | JSON `UpdateCurrentUserRequest`                         | `200` `AuthenticatedUserResponse`  | `400`, `401`, `403`, `409`, `500`        |
| `GET`    | `/v1/rbac/roles`                                           | Yes  | `roles:manage`            | No body                                                 | `200` `RBACRole[]`                 | `401`, `403`, `500`                      |
| `GET`    | `/v1/rbac/permissions`                                     | Yes  | `role_permissions:manage` | No body                                                 | `200` `RBACPermission[]`           | `401`, `403`, `500`                      |
| `GET`    | `/v1/rbac/users`                                           | Yes  | `users:manage`            | No body                                                 | `200` `AdminUserResponse[]`        | `401`, `403`, `500`                      |
| `GET`    | `/v1/rbac/users/{user_id}`                                 | Yes  | `users:manage`            | Path `user_id`                                          | `200` `AdminUserResponse`          | `400`, `401`, `403`, `404`, `500`        |
| `GET`    | `/v1/rbac/users/{user_id}/roles`                           | Yes  | `user_roles:manage`       | Path `user_id`                                          | `200` `AssignedRole[]`             | `400`, `401`, `403`, `404`, `500`        |
| `GET`    | `/v1/rbac/roles/{role_id}/users`                           | Yes  | `user_roles:manage`       | Path `role_id`                                          | `200` `AssignedUser[]`             | `400`, `401`, `403`, `404`, `500`        |
| `POST`   | `/v1/rbac/users`                                           | Yes  | `users:manage`            | JSON `CreateAdminUserRequest`                           | `201` `AdminUserResponse`          | `400`, `401`, `403`, `404`, `409`, `500` |
| `PUT`    | `/v1/rbac/users/{user_id}`                                 | Yes  | `users:manage`            | Path `user_id` + JSON `UpdateAdminUserRequest`          | `200` `AdminUserResponse`          | `400`, `401`, `403`, `404`, `409`, `500` |
| `DELETE` | `/v1/rbac/users/{user_id}`                                 | Yes  | `users:manage`            | Path `user_id`                                          | `204` no body                      | `400`, `401`, `403`, `404`, `500`        |
| `POST`   | `/v1/rbac/roles`                                           | Yes  | `roles:manage`            | JSON `CreateRoleRequest`                                | `201` `RBACRole`                   | `400`, `401`, `403`, `409`, `500`        |
| `PUT`    | `/v1/rbac/roles/{role_id}`                                 | Yes  | `roles:manage`            | Path `role_id` + JSON `UpdateRoleRequest`               | `200` `RBACRole`                   | `400`, `401`, `403`, `404`, `409`, `500` |
| `DELETE` | `/v1/rbac/roles/{role_id}`                                 | Yes  | `roles:manage`            | Path `role_id`                                          | `204` no body                      | `400`, `401`, `403`, `404`, `500`        |
| `PUT`    | `/v1/rbac/roles/{role_id}/inherits/{parent_role_id}`       | Yes  | `roles:manage`            | Path `role_id` + `parent_role_id`                       | `204` no body                      | `400`, `401`, `403`, `404`, `409`, `500` |
| `DELETE` | `/v1/rbac/roles/{role_id}/inherits/{parent_role_id}`       | Yes  | `roles:manage`            | Path `role_id` + `parent_role_id`                       | `204` no body                      | `400`, `401`, `403`, `404`, `500`        |
| `PUT`    | `/v1/rbac/roles/{role_id}/permissions/{permission_id}`     | Yes  | `role_permissions:manage` | Path IDs + JSON `SetRolePermissionRequest`              | `200` `RBACRolePermission`         | `400`, `401`, `403`, `404`, `500`        |
| `DELETE` | `/v1/rbac/roles/{role_id}/permissions/{permission_id}`     | Yes  | `role_permissions:manage` | Path `role_id` + `permission_id`                        | `204` no body                      | `400`, `401`, `403`, `404`, `500`        |
| `PUT`    | `/v1/rbac/users/{user_id}/roles/{role_id}`                 | Yes  | `user_roles:manage`       | Path `user_id` + `role_id`                              | `200` `UserRoleAssignmentResponse` | `400`, `401`, `403`, `404`, `500`        |
| `DELETE` | `/v1/rbac/users/{user_id}/roles/{role_id}`                 | Yes  | `user_roles:manage`       | Path `user_id` + `role_id`                              | `204` no body                      | `400`, `401`, `403`, `404`, `500`        |

Protected rows (`Permission != No`) are contract-checked by
`tests/routers/test_authorization_policy_coverage.py`.

## Read Access Classification

This table classifies each `GET` endpoint as `public`, `authenticated`, or `permission`.

| Method | Path                                                       | Access Level    | Permission                |
| ------ | ---------------------------------------------------------- | --------------- | ------------------------- |
| `GET`  | `/v1/audit-log`                                            | `permission`    | `audit_logs:read`         |
| `GET`  | `/v1/dashboard`                                            | `authenticated` | No                        |
| `GET`  | `/v1/clients`                                              | `authenticated` | No                        |
| `GET`  | `/v1/clients/{client_id}`                                  | `authenticated` | No                        |
| `GET`  | `/v1/matters`                                              | `authenticated` | No                        |
| `GET`  | `/v1/matters/types`                                        | `authenticated` | No                        |
| `GET`  | `/v1/matters/{matter_id}`                                  | `authenticated` | No                        |
| `GET`  | `/v1/matters/{matter_id}/notes`                            | `authenticated` | No                        |
| `GET`  | `/v1/matters/{matter_id}/checklist`                        | `authenticated` | No                        |
| `GET`  | `/v1/matters/{matter_id}/tasks`                            | `authenticated` | No                        |
| `GET`  | `/v1/matters/{matter_id}/documents`                        | `authenticated` | No                        |
| `GET`  | `/v1/matters/{matter_id}/documents/{document_id}/download` | `authenticated` | No                        |
| `GET`  | `/v1/health`                                               | `public`        | No                        |
| `GET`  | `/v1/users/me`                                             | `authenticated` | No                        |
| `GET`  | `/v1/rbac/roles`                                           | `permission`    | `roles:manage`            |
| `GET`  | `/v1/rbac/permissions`                                     | `permission`    | `role_permissions:manage` |
| `GET`  | `/v1/rbac/users`                                           | `permission`    | `users:manage`            |
| `GET`  | `/v1/rbac/users/{user_id}`                                 | `permission`    | `users:manage`            |
| `GET`  | `/v1/rbac/users/{user_id}/roles`                           | `permission`    | `user_roles:manage`       |
| `GET`  | `/v1/rbac/roles/{role_id}/users`                           | `permission`    | `user_roles:manage`       |

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
- Client endpoints resolve `firm_id` from the authenticated principal. List, detail, search, and
  update are always firm-scoped; an absent or foreign `client_id` returns the same `404`.
- Client phones use Mexico country code `52` in a separate persisted column and expose only the
  normalized 10-digit national number. Create/update accept common formatting and optional `+52`;
  phone search removes formatting and an optional leading `52` before matching.
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

### Matter document text extraction

- Validated PDF uploads are parsed locally and their normalized text is persisted for future backend
  AI workflows; extraction does not trigger an AI analysis.
- PDFs without a text layer remain stored with state `empty`; parser failures remain stored with
  state `failed`. No OCR is attempted.
- Existing documents use `unprocessed`, while DOCX and TXT uploads use `not_applicable`.
- Extracted text and extraction state are internal metadata and do not change
  `MatterDocumentResponse` or the public document endpoint shapes.
