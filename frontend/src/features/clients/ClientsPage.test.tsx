import { QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes, useLocation } from "react-router";
import { describe, expect, it, vi } from "vitest";

import { createQueryClient } from "@/app/query-client";
import { ClientDetailPage, ClientsPage, NewClientPage } from "@/features/clients/ClientsPage";
import { parseClient, parseClientList } from "@/features/clients/contracts";
import { t } from "@/shared/i18n/ui-text";

const client = {
  id: 7,
  full_name: "María López",
  phone: "5512345678",
  email: "maria@example.com",
  address: null,
  notes: null,
  created_at: "2026-07-11T12:00:00Z",
  updated_at: "2026-07-11T12:00:00Z",
};

describe("clients contracts", () => {
  it("parses a client and paginated list", () => {
    expect(parseClient(client).full_name).toBe("María López");
    expect(parseClientList({ items: [client], total: 1, limit: 50, offset: 0 }).items).toHaveLength(1);
  });

  it("rejects malformed client payloads", () => {
    expect(() => parseClient({ ...client, id: "7" })).toThrow();
    expect(() => parseClientList({ items: null, total: 0, limit: 50, offset: 0 })).toThrow();
  });
});

const response = (payload: unknown, ok = true, status = 200): Partial<Response> => ({
  ok,
  status,
  statusText: ok ? "OK" : "Error",
  headers: new Headers(),
  json: () => Promise.resolve(payload),
});

const Location = () => <span data-testid="location">{useLocation().pathname}</span>;

const renderRoute = (path: string, fetchMock: ReturnType<typeof vi.fn>) => {
  vi.stubGlobal("fetch", fetchMock);
  const queryClient = createQueryClient();
  queryClient.setQueryDefaults(["clients"], { retry: false });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[path]}>
        <Routes>
          <Route path="/clients" element={<ClientsPage />} />
          <Route path="/clients/new" element={<NewClientPage />} />
          <Route path="/clients/:clientId" element={<ClientDetailPage />} />
          <Route path="/clients/:clientId/edit" element={<ClientDetailPage edit />} />
        </Routes>
        <Location />
      </MemoryRouter>
    </QueryClientProvider>,
  );
};

describe("clients pages", () => {
  it("renders list, search results, and empty states", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(response({ items: [client], total: 1, limit: 50, offset: 0 }))
      .mockResolvedValueOnce(response({ items: [], total: 0, limit: 50, offset: 0 }));
    renderRoute("/clients", fetchMock);
    expect(
      await screen.findByRole("link", { name: client.full_name }, { timeout: 5_000 }),
    ).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText(t("clients.search")), { target: { value: "nadie" } });
    expect(
      await screen.findByText(t("clients.noResults"), undefined, { timeout: 5_000 }),
    ).toBeInTheDocument();
    expect(fetchMock).toHaveBeenLastCalledWith(expect.stringContaining("search=nadie"), expect.anything());
  });

  it("shows request diagnostics and retries list failures", async () => {
    const error = response({ detail: "Failed", code: "invalid_input", request_id: "req-clients" }, false, 400);
    error.headers = new Headers({ "X-Request-ID": "req-clients" });
    const fetchMock = vi.fn().mockResolvedValueOnce(error).mockResolvedValueOnce(response({ items: [], total: 0, limit: 50, offset: 0 }));
    renderRoute("/clients", fetchMock);
    expect(await screen.findByText(/request_id=req-clients/)).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: t("dashboard.retry") }));
    expect(await screen.findByText(t("clients.empty"))).toBeInTheDocument();
  });

  it("validates and creates a client", async () => {
    const fetchMock = vi.fn().mockResolvedValue(response(client, true, 201));
    renderRoute("/clients/new", fetchMock);
    const user = userEvent.setup();
    await user.type(screen.getByLabelText(t("clients.fields.name")), " ");
    await user.type(screen.getByRole("textbox", { name: /^Teléfono/ }), "5512345678");
    await user.click(screen.getByRole("button", { name: t("clients.save") }));
    expect(screen.getByRole("alert")).toHaveTextContent(t("clients.validation.required"));
    await user.clear(screen.getByLabelText(t("clients.fields.name")));
    await user.clear(screen.getByRole("textbox", { name: /^Teléfono/ }));
    await user.type(screen.getByLabelText(t("clients.fields.name")), client.full_name);
    await user.type(screen.getByRole("textbox", { name: /^Teléfono/ }), "55 1234-5678");
    await user.type(screen.getByLabelText(t("clients.fields.email")), client.email);
    await user.click(screen.getByRole("button", { name: t("clients.save") }));
    await waitFor(() => expect(screen.getByTestId("location")).toHaveTextContent("/clients/7"));
    expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining("/clients"), expect.objectContaining({ method: "POST" }));
  });

  it("renders detail and updates a client", async () => {
    const updated = { ...client, notes: "Actualizada" };
    const fetchMock = vi.fn().mockResolvedValueOnce(response(client)).mockResolvedValueOnce(response(client)).mockResolvedValueOnce(response(updated));
    const { unmount } = renderRoute("/clients/7", fetchMock);
    expect(await screen.findByRole("heading", { name: client.full_name })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: t("matters.viewForClient") })).toHaveAttribute("href", "/matters?clientId=7");
    unmount();
    renderRoute("/clients/7/edit", fetchMock);
    const notes = await screen.findByLabelText(t("clients.fields.notes"));
    const user = userEvent.setup();
    await user.type(notes, "Actualizada");
    await user.click(screen.getByRole("button", { name: t("clients.save") }));
    await waitFor(() => expect(screen.getByTestId("location")).toHaveTextContent("/clients/7"));
    expect(fetchMock.mock.calls.some(([, options]) => (options as RequestInit | undefined)?.method === "PATCH")).toBe(true);
  });
});
