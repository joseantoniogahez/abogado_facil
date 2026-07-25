import { QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import { createMemoryRouter } from "react-router";
import { RouterProvider } from "react-router/dom";

import { createQueryClient } from "@/app/query-client";
import { appRoutes } from "@/app/routes";
import { getAccessToken, setAccessToken } from "@/shared/auth/storage";
import { t } from "@/shared/i18n/ui-text";

const toRequestPathname = (input: RequestInfo | URL): string => {
  if (input instanceof URL) {
    return input.pathname;
  }
  if (typeof input === "string") {
    return new URL(input).pathname;
  }
  return new URL(input.url).pathname;
};

describe("routing integration", () => {
  it("clears expired token and redirects to login from protected route", async () => {
    setAccessToken("expired-token");

    const fetchMock = vi.fn().mockResolvedValue({
      ok: false,
      status: 401,
      statusText: "Unauthorized",
      json: () =>
        Promise.resolve({
          detail: "Could not validate credentials",
          code: "unauthorized",
        }),
    } satisfies Partial<Response>);
    vi.stubGlobal("fetch", fetchMock);

    const queryClient = createQueryClient();
    const router = createMemoryRouter(appRoutes, {
      initialEntries: ["/welcome"],
    });

    render(
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} />
      </QueryClientProvider>,
    );

    await waitFor(
      () => {
        expect(router.state.location.pathname).toBe("/login");
      },
      { timeout: 5_000 },
    );
    expect(
      await screen.findByRole("button", { name: t("auth.login.submit.default") }),
    ).toBeInTheDocument();
    expect(getAccessToken()).toBeNull();
  }, 10_000);

  it("shows protected-route diagnostic when session check fails with request id", async () => {
    setAccessToken("server-error-token");

    const fetchMock = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
      statusText: "Internal Server Error",
      headers: {
        get: (header: string) => (header === "X-Request-ID" ? "req-protected-500" : null),
      },
      json: () =>
        Promise.resolve({
          detail: "Unexpected backend error",
          code: "internal_error",
        }),
    } satisfies Partial<Response>);
    vi.stubGlobal("fetch", fetchMock);

    const queryClient = createQueryClient();
    const router = createMemoryRouter(appRoutes, {
      initialEntries: ["/welcome"],
    });

    render(
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} />
      </QueryClientProvider>,
    );

    expect(
      await screen.findByRole("heading", { name: t("routing.protected.error.title") }),
    ).toBeInTheDocument();
    expect(await screen.findByText(/request_id=req-protected-500/)).toBeInTheDocument();
  });

  it("renders explicit not-found page for unknown routes", async () => {
    const queryClient = createQueryClient();
    const router = createMemoryRouter(appRoutes, {
      initialEntries: ["/unknown-route"],
    });

    render(
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} />
      </QueryClientProvider>,
    );

    expect(
      await screen.findByRole("heading", { name: t("routing.notFound.title") }),
    ).toBeInTheDocument();
    expect(screen.getByText(t("routing.notFound.body"))).toBeInTheDocument();
  });

  it.each([
    ["/matters", "matters.title"],
    ["/matters/new", "matters.create.title"],
    ["/matters/1", "Matter under test"],
    ["/matters/1/edit", "matters.edit"],
  ] as const)("renders the lazy route %s", async (path, heading) => {
    setAccessToken("valid-matters-token");

    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const pathname = toRequestPathname(input);

      if (pathname === "/v1/users/me") {
        return {
          ok: true,
          status: 200,
          json: () =>
            Promise.resolve({
              id: 1,
              email: "lawyer@example.com",
              first_name: "Test",
              middle_name: null,
              last_name: "Lawyer",
              display_name: "Test Lawyer",
              firm_name: "Test Legal",
              disabled: false,
              permissions: [],
            }),
        } satisfies Partial<Response>;
      }

      if (pathname === "/v1/matters") {
        return {
          ok: true,
          status: 200,
          json: () => Promise.resolve({ items: [], total: 0, limit: 50, offset: 0 }),
        } satisfies Partial<Response>;
      }

      if (pathname === "/v1/matters/1") {
        return {
          ok: true,
          status: 200,
          json: () =>
            Promise.resolve({
              id: 1,
              client_id: 2,
              title: "Matter under test",
              matter_type: "Civil",
              status: "active",
              counterparty: null,
              description: null,
              next_action: null,
              next_action_date: null,
              created_at: "2026-07-12T00:00:00Z",
              updated_at: "2026-07-12T00:00:00Z",
            }),
        } satisfies Partial<Response>;
      }

      throw new Error(`Unhandled route integration request: ${pathname}`);
    });
    vi.stubGlobal("fetch", fetchMock);

    const queryClient = createQueryClient();
    const router = createMemoryRouter(appRoutes, { initialEntries: [path] });

    render(
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} />
      </QueryClientProvider>,
    );

    expect(
      await screen.findByRole("heading", {
        name: heading === "Matter under test" ? heading : t(heading),
      }),
    ).toBeInTheDocument();
  });

  it("renders admin users route when session is valid", async () => {
    setAccessToken("valid-admin-token");

    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const pathname = toRequestPathname(input);

      if (pathname === "/v1/users/me") {
        return {
          ok: true,
          status: 200,
          json: () =>
            Promise.resolve({
              id: 1,
              email: "admin",
              first_name: "Test",
              middle_name: null,
              last_name: "User",
              display_name: "Test User",
              firm_name: "Test Legal",
              disabled: false,
              permissions: ["users:manage"],
            }),
        } satisfies Partial<Response>;
      }

      if (pathname === "/v1/rbac/users") {
        return {
          ok: true,
          status: 200,
          json: () => Promise.resolve([]),
        } satisfies Partial<Response>;
      }

      if (pathname === "/v1/rbac/roles") {
        return {
          ok: true,
          status: 200,
          json: () => Promise.resolve([]),
        } satisfies Partial<Response>;
      }

      throw new Error(`Unhandled route integration request: ${pathname}`);
    });
    vi.stubGlobal("fetch", fetchMock);

    const queryClient = createQueryClient();
    const router = createMemoryRouter(appRoutes, {
      initialEntries: ["/admin/users"],
    });

    render(
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} />
      </QueryClientProvider>,
    );

    expect(
      await screen.findByRole("heading", { name: t("admin.users.title") }),
    ).toBeInTheDocument();
  });

  it("renders audit log route when session has audit_logs:read", async () => {
    setAccessToken("valid-audit-admin-token");

    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const pathname = toRequestPathname(input);

      if (pathname === "/v1/users/me") {
        return {
          ok: true,
          status: 200,
          json: () =>
            Promise.resolve({
              id: 1,
              email: "audit_admin",
              first_name: "Test",
              middle_name: null,
              last_name: "User",
              display_name: "Test User",
              firm_name: "Test Legal",
              disabled: false,
              permissions: ["audit_logs:read"],
            }),
        } satisfies Partial<Response>;
      }

      if (pathname === "/v1/audit-log") {
        return {
          ok: true,
          status: 200,
          json: () => Promise.resolve([]),
        } satisfies Partial<Response>;
      }

      throw new Error(`Unhandled route integration request: ${pathname}`);
    });
    vi.stubGlobal("fetch", fetchMock);

    const queryClient = createQueryClient();
    const router = createMemoryRouter(appRoutes, {
      initialEntries: ["/admin/audit-log"],
    });

    render(
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} />
      </QueryClientProvider>,
    );

    expect(
      await screen.findByRole("heading", { name: t("admin.auditLog.title") }),
    ).toBeInTheDocument();
  });

  it("renders admin assignments route when session has user_roles:manage", async () => {
    setAccessToken("valid-assignment-admin-token");

    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const pathname = toRequestPathname(input);

      if (pathname === "/v1/users/me") {
        return {
          ok: true,
          status: 200,
          json: () =>
            Promise.resolve({
              id: 1,
              email: "rbac_admin",
              first_name: "Test",
              middle_name: null,
              last_name: "User",
              display_name: "Test User",
              firm_name: "Test Legal",
              disabled: false,
              permissions: ["user_roles:manage"],
            }),
        } satisfies Partial<Response>;
      }

      throw new Error(`Unhandled route integration request: ${pathname}`);
    });
    vi.stubGlobal("fetch", fetchMock);

    const queryClient = createQueryClient();
    const router = createMemoryRouter(appRoutes, {
      initialEntries: ["/admin/assignments"],
    });

    render(
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} />
      </QueryClientProvider>,
    );

    expect(await screen.findByRole("heading", { name: t("admin.as.title") })).toBeInTheDocument();
  });

  it("renders admin permissions route when session has role_permissions:manage", async () => {
    setAccessToken("valid-permission-admin-token");

    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const pathname = toRequestPathname(input);

      if (pathname === "/v1/users/me") {
        return {
          ok: true,
          status: 200,
          json: () =>
            Promise.resolve({
              id: 1,
              email: "permission_admin",
              first_name: "Test",
              middle_name: null,
              last_name: "User",
              display_name: "Test User",
              firm_name: "Test Legal",
              disabled: false,
              permissions: ["role_permissions:manage"],
            }),
        } satisfies Partial<Response>;
      }

      if (pathname === "/v1/rbac/permissions") {
        return {
          ok: true,
          status: 200,
          json: () => Promise.resolve([]),
        } satisfies Partial<Response>;
      }

      throw new Error(`Unhandled route integration request: ${pathname}`);
    });
    vi.stubGlobal("fetch", fetchMock);

    const queryClient = createQueryClient();
    const router = createMemoryRouter(appRoutes, {
      initialEntries: ["/admin/permissions"],
    });

    render(
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} />
      </QueryClientProvider>,
    );

    expect(await screen.findByRole("heading", { name: t("admin.pm.title") })).toBeInTheDocument();
  });
});
