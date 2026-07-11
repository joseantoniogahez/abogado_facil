import { QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen } from "@testing-library/react";

import { createQueryClient } from "@/app/query-client";
import { DashboardPage } from "@/features/dashboard/DashboardPage";
import { SESSION_QUERY_KEY } from "@/shared/auth/session";
import { t } from "@/shared/i18n/ui-text";

const user = { id: 1, email: "test@example.com", first_name: "Test", middle_name: null, last_name: "User", display_name: "Test User", firm_name: "Despacho Prueba", disabled: false, permissions: [] };
const summary = { firm_id: 1, firm_name: "Despacho Prueba", clients: { value: 0, available: false }, active_matters: { value: 0, available: false }, pending_tasks: { value: 0, available: false }, upcoming_tasks: [], ai_status: "not_available", actions: [{ id: "create_client", available: false }] };

const renderPage = (fetchMock: ReturnType<typeof vi.fn>) => {
  vi.stubGlobal("fetch", fetchMock);
  const queryClient = createQueryClient();
  queryClient.setQueryDefaults(["dashboard", "summary"], { retry: false });
  queryClient.setQueryData(SESSION_QUERY_KEY, user);
  render(<QueryClientProvider client={queryClient}><DashboardPage /></QueryClientProvider>);
};

describe("DashboardPage", () => {
  it("renders empty and unavailable product states", async () => {
    renderPage(vi.fn().mockResolvedValue({ ok: true, status: 200, json: () => Promise.resolve(summary) }));
    expect(await screen.findByRole("heading", { name: t("dashboard.greeting", { displayName: "Test User" }) })).toBeInTheDocument();
    expect(screen.getByText(t("dashboard.upcoming.empty"))).toBeInTheDocument();
    expect(screen.getByText(t("dashboard.ai.notAvailable"))).toBeInTheDocument();
    expect(screen.getAllByRole("button").every((button) => button.hasAttribute("disabled"))).toBe(true);
  });

  it("renders request-id diagnostics and retries", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({ ok: false, status: 400, statusText: "Error", headers: { get: () => "req-dashboard" }, json: () => Promise.resolve({ detail: "Failed", code: "invalid_input" }) })
      .mockResolvedValueOnce({ ok: true, status: 200, json: () => Promise.resolve(summary) });
    renderPage(fetchMock);
    expect(await screen.findByText(/request_id=req-dashboard/)).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: t("dashboard.retry") }));
    expect(await screen.findByRole("heading", { name: t("dashboard.greeting", { displayName: "Test User" }) })).toBeInTheDocument();
  });
});
