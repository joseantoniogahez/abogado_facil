import { QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import axe from "axe-core";
import { createMemoryRouter, MemoryRouter, RouterProvider } from "react-router-dom";

import { createQueryClient } from "@/app/query-client";
import { appRoutes } from "@/app/routes";
import { ProfilePage } from "@/features/profile/ProfilePage";
import { SESSION_QUERY_KEY } from "@/shared/auth/session";
import { clearAccessToken, setAccessToken } from "@/shared/auth/storage";
import { t } from "@/shared/i18n/ui-text";

const AXE_RUN_OPTIONS: axe.RunOptions = {
  rules: {
    "color-contrast": { enabled: false },
  },
};

const SESSION_USER = {
  id: 7,
  email: "profile@example.com",
  first_name: "Test",
  middle_name: null,
  last_name: "User",
  display_name: "Test User",
  firm_name: "Test Legal",
  disabled: false,
  permissions: [],
};

const renderProfilePage = () => {
  const queryClient = createQueryClient();
  queryClient.setQueryData(SESSION_QUERY_KEY, SESSION_USER);

  const view = render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <ProfilePage />
      </MemoryRouter>
    </QueryClientProvider>,
  );

  return { queryClient, view };
};

describe("ProfilePage", () => {
  beforeEach(() => {
    clearAccessToken();
  });

  it("redirects unauthenticated access from /profile to /login", async () => {
    const queryClient = createQueryClient();
    queryClient.setQueryData(SESSION_QUERY_KEY, null);
    const router = createMemoryRouter(appRoutes, {
      initialEntries: ["/profile"],
    });

    render(
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} />
      </QueryClientProvider>,
    );

    await waitFor(() => {
      expect(router.state.location.pathname).toBe("/login");
    });
    expect(await screen.findByRole("heading", { name: t("auth.login.title") })).toBeInTheDocument();
  });

  it("updates profile data and writes through the session cache", async () => {
    setAccessToken("profile-token");
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: () =>
        Promise.resolve({
          id: 7,
          email: "profile.v2@example.com",
          first_name: "Test",
          middle_name: null,
          last_name: "User",
          display_name: "Test User",
          firm_name: "Test Legal",
          disabled: false,
          permissions: [],
        }),
    } satisfies Partial<Response>);
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup();

    const { queryClient } = renderProfilePage();

    await user.clear(screen.getByLabelText(t("profile.fields.firstName")));
    await user.type(screen.getByLabelText(t("profile.fields.firstName")), "Updated");
    await user.clear(screen.getByLabelText(t("profile.fields.firmName")));
    await user.type(screen.getByLabelText(t("profile.fields.firmName")), "Updated Legal");
    await user.clear(screen.getByLabelText(t("profile.fields.email")));
    await user.type(screen.getByLabelText(t("profile.fields.email")), " profile.v2@example.com ");
    await user.type(screen.getByLabelText(t("profile.fields.currentPassword")), "ProfilePass1");
    await user.type(screen.getByLabelText(t("profile.fields.newPassword")), "ProfilePass2");
    await user.click(screen.getByRole("button", { name: t("profile.submit.default") }));

    expect(
      await screen.findByText(t("profile.success.body", { email: "profile.v2@example.com" })),
    ).toBeInTheDocument();
    expect(
      await screen.findByText(t("profile.currentUser", { email: "profile.v2@example.com" })),
    ).toBeInTheDocument();
    expect(queryClient.getQueryData(SESSION_QUERY_KEY)).toEqual({
      id: 7,
      email: "profile.v2@example.com",
      first_name: "Test",
      middle_name: null,
      last_name: "User",
      display_name: "Test User",
      firm_name: "Test Legal",
      disabled: false,
      permissions: [],
    });
  });

  it("shows deterministic diagnostics when profile update fails", async () => {
    setAccessToken("profile-token");
    const fetchMock = vi.fn().mockResolvedValue({
      ok: false,
      status: 409,
      statusText: "Conflict",
      headers: {
        get: (header: string) => (header === "X-Request-ID" ? "req-profile-409" : null),
      },
      json: () =>
        Promise.resolve({
          detail: "Email already exists",
          code: "conflict",
        }),
    } satisfies Partial<Response>);
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup();

    renderProfilePage();

    await user.clear(screen.getByLabelText(t("profile.fields.firstName")));
    await user.type(screen.getByLabelText(t("profile.fields.firstName")), "Updated");
    await user.clear(screen.getByLabelText(t("profile.fields.firmName")));
    await user.type(screen.getByLabelText(t("profile.fields.firmName")), "Updated Legal");
    await user.clear(screen.getByLabelText(t("profile.fields.email")));
    await user.type(screen.getByLabelText(t("profile.fields.email")), "admin@example.com");
    await user.click(screen.getByRole("button", { name: t("profile.submit.default") }));

    expect(
      await screen.findByText("Email already exists (request_id=req-profile-409)"),
    ).toBeInTheDocument();
  });

  it("clears the session cache when the profile update returns unauthorized", async () => {
    setAccessToken("profile-token");
    const fetchMock = vi.fn().mockResolvedValue({
      ok: false,
      status: 401,
      statusText: "Unauthorized",
      json: () =>
        Promise.resolve({
          detail: "Current password is invalid",
          code: "unauthorized",
        }),
    } satisfies Partial<Response>);
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup();

    const { queryClient } = renderProfilePage();

    await user.type(screen.getByLabelText(t("profile.fields.currentPassword")), "WrongPass1");
    await user.type(screen.getByLabelText(t("profile.fields.newPassword")), "ProfilePass2");
    await user.click(screen.getByRole("button", { name: t("profile.submit.default") }));

    await waitFor(() => {
      expect(queryClient.getQueryData(SESSION_QUERY_KEY)).toBeNull();
    });
  });

  it("keeps the profile form accessible", async () => {
    const { view } = renderProfilePage();

    expect(await screen.findByRole("heading", { name: t("profile.title") })).toBeInTheDocument();
    expect((await axe.run(view.container, AXE_RUN_OPTIONS)).violations).toHaveLength(0);
  });
});
