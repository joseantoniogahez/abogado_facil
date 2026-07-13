# Frontend Route Inventory

This document is the canonical inventory of runtime routes, access policies, and route-level ownership.

## Route Catalog

| Path                      | Access Policy | Owner Module                                      | Notes                                                                                                                                                              |
| ------------------------- | ------------- | ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `/`                       | `public`      | `features/landing/LandingPage`                    | Root index route.                                                                                                                                                  |
| `/login`                  | `public`      | `features/auth/LoginPage`                         | Email/password authentication; successful login writes the bearer session and redirects to `/dashboard`.                                                           |
| `/register`               | `public`      | `features/auth/RegisterPage`                      | Captures product account names, email, password, and optional firm; success offers login without creating a session token.                                         |
| `/dashboard`              | `protected`   | `features/dashboard/DashboardPage`                | Canonical authenticated home; loads one firm-scoped summary request.                                                                                               |
| `/welcome`                | `protected`   | `app/routes`                                      | Temporary compatibility redirect to `/dashboard`; no duplicate page implementation.                                                                                |
| `/profile`                | `protected`   | `features/profile/ProfilePage`                    | Protected route; updates legal-name components, display name, email, firm name, and password.                                                                      |
| `/clients`                | `protected`   | `features/clients/ClientsPage`                    | Firm-scoped list and search by name or phone.                                                                                                                      |
| `/clients/new`            | `protected`   | `features/clients/NewClientPage`                  | Creates a client without exposing firm selection.                                                                                                                  |
| `/clients/:clientId`      | `protected`   | `features/clients/ClientDetailPage`               | Client detail with contextual navigation to list or create its matters.                                                                                            |
| `/clients/:clientId/edit` | `protected`   | `features/clients/ClientDetailPage`               | Partial client update using the shared client form.                                                                                                                |
| `/matters`                | `protected`   | `features/matters/MattersPage`                    | Firm-scoped list, optionally filtered by client.                                                                                                                   |
| `/matters/new`            | `protected`   | `features/matters/NewMatterPage`                  | Creates a matter for a client in the current firm.                                                                                                                 |
| `/matters/:matterId`      | `protected`   | `features/matters/MatterDetailPage`               | Matter detail with status, counterparty, next action, and firm-scoped expediente notes CRUD.                                                                       |
| `/matters/:matterId/edit` | `protected`   | `features/matters/MatterDetailPage`               | Partial matter update, including status and next action.                                                                                                           |
| `/admin/audit-log`        | `protected`   | `features/audit-log/AuditLogPage`                 | Requires `audit_logs:read`; missing permission redirects to `/dashboard`.                                                                                          |
| `/admin/assignments`      | `protected`   | `features/admin-assignments/AdminAssignmentsPage` | Requires `user_roles:manage`; missing permission redirects to `/dashboard`.                                                                                        |
| `/admin/permissions`      | `protected`   | `features/admin-permissions/AdminPermissionsPage` | Requires `role_permissions:manage`; role inventory falls back to manual ID without `roles:manage`.                                                                 |
| `/admin/users`            | `protected`   | `features/admin-users/AdminUsersPage`             | Requires `users:manage`; missing permission redirects to `/dashboard`, while role-related controls stay hidden in-page unless the session also has `roles:manage`. |
| `/admin/roles`            | `protected`   | `features/admin-roles/AdminRolesPage`             | Requires `roles:manage`; missing permission redirects to `/dashboard`.                                                                                             |
| `/*`                      | `public`      | `features/not-found/NotFoundPage`                 | Explicit catch-all for unknown routes.                                                                                                                             |

## Route-Level Error Handling

- Root route uses `shared/routing/RouteErrorBoundary` as `errorElement`.
- Protected route failures render user-safe messages and include request-id diagnostics when available.
- Route errors must render user-safe messages and include request-id diagnostics when available.

## 404 Behavior

- Unknown paths must resolve to `/*` and render `features/not-found/NotFoundPage`.
- Redirect-based 404 behavior is disallowed; the route tree must keep explicit not-found ownership.
