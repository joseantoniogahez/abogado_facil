import { startTransition, useEffect, useMemo, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Link, Outlet, useLocation, useNavigate } from "react-router-dom";

import { authLogoutMutationPolicy } from "@/app/mutation-policy";
import { logout, SESSION_QUERY_KEY, useSession } from "@/shared/auth/session";
import { IAM_PERMISSION } from "@/shared/iam/contracts";
import { userHasPermission } from "@/shared/iam/api";
import { t } from "@/shared/i18n/ui-text";

interface AdminMenuItem {
  key:
    | "routing.nav.admin.auditLog"
    | "routing.nav.admin.assignments"
    | "routing.nav.admin.permissions"
    | "routing.nav.admin.users"
    | "routing.nav.admin.roles";
  permissionId: string;
  to: "/admin/audit-log" | "/admin/assignments" | "/admin/permissions" | "/admin/users" | "/admin/roles";
}

interface PrimaryMenuItem {
  key: "routing.nav.home" | "routing.nav.profile";
  to: "/dashboard" | "/profile";
}

const PRIMARY_MENU_ITEMS: readonly PrimaryMenuItem[] = [
  {
    key: "routing.nav.home",
    to: "/dashboard",
  },
  {
    key: "routing.nav.profile",
    to: "/profile",
  },
];

const ADMIN_MENU_ITEMS: readonly AdminMenuItem[] = [
  {
    key: "routing.nav.admin.auditLog",
    permissionId: IAM_PERMISSION.AUDIT_LOGS_READ,
    to: "/admin/audit-log",
  },
  {
    key: "routing.nav.admin.permissions",
    permissionId: IAM_PERMISSION.ROLE_PERMISSIONS_MANAGE,
    to: "/admin/permissions",
  },
  {
    key: "routing.nav.admin.assignments",
    permissionId: IAM_PERMISSION.USER_ROLES_MANAGE,
    to: "/admin/assignments",
  },
  {
    key: "routing.nav.admin.users",
    permissionId: IAM_PERMISSION.USERS_MANAGE,
    to: "/admin/users",
  },
  {
    key: "routing.nav.admin.roles",
    permissionId: IAM_PERMISSION.ROLES_MANAGE,
    to: "/admin/roles",
  },
];

export const RootLayout = () => {
  const { data: user } = useSession();
  const location = useLocation();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const logoutMutation = useMutation({
    ...authLogoutMutationPolicy,
    mutationFn: () => logout(),
    onSuccess: async () => {
      queryClient.setQueryData(SESSION_QUERY_KEY, null);
      await queryClient.invalidateQueries({ queryKey: SESSION_QUERY_KEY });
      startTransition(() => void navigate("/login", { replace: true }));
    },
  });

  useEffect(() => {
    setIsMenuOpen(false);
  }, [location.pathname]);

  const visibleAdminItems = useMemo(() => {
    if (!user) {
      return [];
    }
    return ADMIN_MENU_ITEMS.filter((menuItem) => userHasPermission(user, menuItem.permissionId));
  }, [user]);

  if (!user) {
    return <Outlet />;
  }

  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-20 border-b border-[var(--app-border)] bg-[var(--app-surface)]">
        <div className="mx-auto flex w-full max-w-6xl items-center justify-between px-4 py-3">
          <button
            aria-controls="app-navigation-panel"
            aria-expanded={isMenuOpen}
            aria-label={t("routing.nav.menu.toggle")}
            className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-[var(--app-border)]"
            onClick={() => setIsMenuOpen((previous) => !previous)}
            type="button"
          >
            <span aria-hidden className="text-lg">
              &#8801;
            </span>
          </button>
          <div className="flex items-center gap-4">
            <Link className="text-sm font-semibold" to="/dashboard">{t("routing.nav.home")}</Link>
            <button className="text-sm font-semibold" disabled={logoutMutation.isPending} onClick={() => logoutMutation.mutate()} type="button">
              {logoutMutation.isPending ? t("routing.logout.pending") : t("routing.logout")}
            </button>
          </div>
        </div>
      </header>

      <div className="mx-auto flex w-full max-w-6xl">
        <nav
          className="w-64 shrink-0 border-r border-[var(--app-border)] bg-[var(--app-surface)] p-4"
          hidden={!isMenuOpen}
          id="app-navigation-panel"
        >
          <ul className="space-y-2">
            {PRIMARY_MENU_ITEMS.map((menuItem) => (
              <li key={menuItem.to}>
                <Link className="block rounded-xl px-3 py-2 text-sm font-medium hover:bg-[var(--app-bg)]" to={menuItem.to}>
                  {t(menuItem.key)}
                </Link>
              </li>
            ))}
            {visibleAdminItems.length > 0 ? (
              <li>
                <p className="px-3 pt-2 text-xs font-semibold uppercase tracking-wide text-[var(--app-subtle)]">
                  {t("routing.nav.admin.group")}
                </p>
                <ul className="mt-1 space-y-1">
                  {visibleAdminItems.map((menuItem) => (
                    <li key={menuItem.to}>
                      <Link
                        className="block rounded-xl px-3 py-2 text-sm font-medium hover:bg-[var(--app-bg)]"
                        to={menuItem.to}
                      >
                        {t(menuItem.key)}
                      </Link>
                    </li>
                  ))}
                </ul>
              </li>
            ) : null}
          </ul>
        </nav>

        <div className="min-w-0 flex-1">
          <Outlet />
        </div>
      </div>
    </div>
  );
};
