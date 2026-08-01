import { lazy, Suspense } from "react";
import type { RouteObject } from "react-router";
import { Navigate } from "react-router";

import { AdminAssignmentsPage } from "@/features/admin-assignments/AdminAssignmentsPage";
import { AdminPermissionsPage } from "@/features/admin-permissions/AdminPermissionsPage";
import { AdminRolesPage } from "@/features/admin-roles/AdminRolesPage";
import { AdminUsersPage } from "@/features/admin-users/AdminUsersPage";
import { AiInsightsPage } from "@/features/ai-insights/AiInsightsPage";
import { AiSettingsPage } from "@/features/ai-settings/AiSettingsPage";
import { AuditLogPage } from "@/features/audit-log/AuditLogPage";
import { LoginPage } from "@/features/auth/LoginPage";
import { RegisterPage } from "@/features/auth/RegisterPage";
import { ClientDetailPage, ClientsPage, NewClientPage } from "@/features/clients/ClientsPage";
import { DashboardPage } from "@/features/dashboard/DashboardPage";
import { DocumentTemplatesPage } from "@/features/document-templates/DocumentTemplatesPage";
import { LandingPage } from "@/features/landing/LandingPage";
import { NotFoundPage } from "@/features/not-found/NotFoundPage";
import { ProfilePage } from "@/features/profile/ProfilePage";
import { IAM_PERMISSION } from "@/shared/iam/contracts";
import { PermissionRoute } from "@/shared/routing/PermissionRoute";
import { ProtectedRoute } from "@/shared/routing/ProtectedRoute";
import { RootLayout } from "@/shared/routing/RootLayout";
import { RouteErrorBoundary } from "@/shared/routing/RouteErrorBoundary";

const MattersPage = lazy(() =>
  import("@/features/matters/MattersPage").then(module => ({ default: module.MattersPage })),
);
const NewMatterPage = lazy(() =>
  import("@/features/matters/MattersPage").then(module => ({ default: module.NewMatterPage })),
);
const MatterDetailPage = lazy(() =>
  import("@/features/matters/MattersPage").then(module => ({ default: module.MatterDetailPage })),
);
/* eslint-disable react-refresh/only-export-components -- route adapters belong with the centralized route composition */
/* v8 ignore next */
const MattersRoute = () => (
  <Suspense fallback={null}>
    <MattersPage />
  </Suspense>
);
/* v8 ignore next */
const NewMatterRoute = () => (
  <Suspense fallback={null}>
    <NewMatterPage />
  </Suspense>
);
/* v8 ignore next */
const MatterDetailRoute = ({ edit = false }: { edit?: boolean }) => (
  <Suspense fallback={null}>
    <MatterDetailPage edit={edit} />
  </Suspense>
);
/* eslint-enable react-refresh/only-export-components */

export const appRoutes: RouteObject[] = [
  {
    path: "/",
    element: <RootLayout />,
    errorElement: <RouteErrorBoundary />,
    children: [
      {
        index: true,
        element: <LandingPage />,
      },
      {
        path: "login",
        element: <LoginPage />,
      },
      {
        path: "register",
        element: <RegisterPage />,
      },
      {
        element: <ProtectedRoute />,
        children: [
          {
            path: "welcome",
            element: <Navigate replace to="/dashboard" />,
          },
          {
            path: "dashboard",
            element: <DashboardPage />,
          },
          {
            path: "profile",
            element: <ProfilePage />,
          },
          {
            path: "settings/ai",
            element: <AiSettingsPage />,
          },
          {
            path: "ai/insights",
            element: <AiInsightsPage />,
          },
          {
            path: "document-templates",
            element: <DocumentTemplatesPage />,
          },
          { path: "clients", element: <ClientsPage /> },
          { path: "clients/new", element: <NewClientPage /> },
          { path: "clients/:clientId", element: <ClientDetailPage /> },
          { path: "clients/:clientId/edit", element: <ClientDetailPage edit /> },
          { path: "matters", element: <MattersRoute /> },
          { path: "matters/new", element: <NewMatterRoute /> },
          { path: "matters/:matterId", element: <MatterDetailRoute /> },
          { path: "matters/:matterId/edit", element: <MatterDetailRoute edit /> },
          {
            element: <PermissionRoute requiredPermission={IAM_PERMISSION.AUDIT_LOGS_READ} />,
            children: [
              {
                path: "admin/audit-log",
                element: <AuditLogPage />,
              },
            ],
          },
          {
            element: <PermissionRoute requiredPermission={IAM_PERMISSION.USERS_MANAGE} />,
            children: [
              {
                path: "admin/users",
                element: <AdminUsersPage />,
              },
            ],
          },
          {
            element: <PermissionRoute requiredPermission={IAM_PERMISSION.ROLES_MANAGE} />,
            children: [
              {
                path: "admin/roles",
                element: <AdminRolesPage />,
              },
            ],
          },
          {
            element: (
              <PermissionRoute requiredPermission={IAM_PERMISSION.ROLE_PERMISSIONS_MANAGE} />
            ),
            children: [
              {
                path: "admin/permissions",
                element: <AdminPermissionsPage />,
              },
            ],
          },
          {
            element: <PermissionRoute requiredPermission={IAM_PERMISSION.USER_ROLES_MANAGE} />,
            children: [
              {
                path: "admin/assignments",
                element: <AdminAssignmentsPage />,
              },
            ],
          },
        ],
      },
      {
        path: "*",
        element: <NotFoundPage />,
      },
    ],
  },
];
