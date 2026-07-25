import { QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import { createMemoryRouter } from "react-router";
import { RouterProvider } from "react-router/dom";

import { createQueryClient } from "@/app/query-client";
import { appRoutes } from "@/app/routes";
import { SESSION_QUERY_KEY } from "@/shared/auth/session";
import { t } from "@/shared/i18n/ui-text";

type AdminRoutePath
  = | "/admin/audit-log"
    | "/admin/assignments"
    | "/admin/permissions"
    | "/admin/users"
    | "/admin/roles";

const renderAppAt = (path: AdminRoutePath) => {
  const queryClient = createQueryClient();
  queryClient.setQueryData(SESSION_QUERY_KEY, {
    id: 7,
    email: "reader_user",
    first_name: "Test",
    middle_name: null,
    last_name: "User",
    display_name: "Test User",
    firm_name: "Test Legal",
    disabled: false,
    permissions: [],
  });

  const router = createMemoryRouter(appRoutes, {
    initialEntries: [path],
  });

  render(
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>,
  );

  return router;
};

describe("PermissionRoute", () => {
  const dashboardResponse = {
    ok: true,
    status: 200,
    json: () =>
      Promise.resolve({
        firm_id: 1,
        firm_name: "Test Legal",
        clients: { value: 0, available: false },
        active_matters: { value: 0, available: false },
        pending_tasks: { value: 0, available: false },
        upcoming_tasks: [],
        ai_status: "not_available",
        actions: [],
      }),
  } satisfies Partial<Response>;

  it("redirects unauthorized direct navigation from /admin/users to /dashboard", async () => {
    const fetchMock = vi.fn().mockResolvedValue(dashboardResponse);
    vi.stubGlobal("fetch", fetchMock);
    const router = renderAppAt("/admin/users");

    await waitFor(() => {
      expect(router.state.location.pathname).toBe("/dashboard");
    });
    expect(
      await screen.findByRole("heading", {
        name: t("dashboard.greeting", { displayName: "Test User" }),
      }),
    ).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledTimes(1);
  }, 10_000);

  it("redirects unauthorized direct navigation from /admin/audit-log to /dashboard", async () => {
    const fetchMock = vi.fn().mockResolvedValue(dashboardResponse);
    vi.stubGlobal("fetch", fetchMock);
    const router = renderAppAt("/admin/audit-log");

    await waitFor(() => {
      expect(router.state.location.pathname).toBe("/dashboard");
    });
    expect(
      await screen.findByRole("heading", {
        name: t("dashboard.greeting", { displayName: "Test User" }),
      }),
    ).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledTimes(1);
  }, 10_000);

  it("redirects unauthorized direct navigation from /admin/roles to /dashboard", async () => {
    const fetchMock = vi.fn().mockResolvedValue(dashboardResponse);
    vi.stubGlobal("fetch", fetchMock);
    const router = renderAppAt("/admin/roles");

    await waitFor(() => {
      expect(router.state.location.pathname).toBe("/dashboard");
    });
    expect(
      await screen.findByRole("heading", {
        name: t("dashboard.greeting", { displayName: "Test User" }),
      }),
    ).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledTimes(1);
  }, 10_000);

  it("redirects unauthorized direct navigation from /admin/assignments to /dashboard", async () => {
    const fetchMock = vi.fn().mockResolvedValue(dashboardResponse);
    vi.stubGlobal("fetch", fetchMock);
    const router = renderAppAt("/admin/assignments");

    await waitFor(() => {
      expect(router.state.location.pathname).toBe("/dashboard");
    });
    expect(
      await screen.findByRole("heading", {
        name: t("dashboard.greeting", { displayName: "Test User" }),
      }),
    ).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledTimes(1);
  }, 10_000);

  it("redirects unauthorized direct navigation from /admin/permissions to /dashboard", async () => {
    const fetchMock = vi.fn().mockResolvedValue(dashboardResponse);
    vi.stubGlobal("fetch", fetchMock);
    const router = renderAppAt("/admin/permissions");

    await waitFor(() => {
      expect(router.state.location.pathname).toBe("/dashboard");
    });
    expect(
      await screen.findByRole("heading", {
        name: t("dashboard.greeting", { displayName: "Test User" }),
      }),
    ).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledTimes(1);
  }, 10_000);
});
