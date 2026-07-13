import { createQueryClient } from "@/app/query-client";
import { t } from "@/shared/i18n/ui-text";
import { QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import { MatterDetailPage, MatterList, NewMatterPage } from "./MattersPage";
import { parseMatter, parseMatterList } from "./contracts";

const matter = {
  id: 1,
  client_id: 2,
  title: "Pensión",
  matter_type: "Familiar",
  status: "active",
  counterparty: null,
  description: null,
  next_action: "Pedir actas",
  next_action_date: null,
  created_at: "2026-07-12T00:00:00Z",
  updated_at: "2026-07-12T00:00:00Z",
};

describe("matter contracts", () => {
  it("parses records and lists", () => {
    expect(parseMatter(matter).title).toBe("Pensión");
    expect(
      parseMatterList({ items: [matter], total: 1, limit: 50, offset: 0 })
        .items,
    ).toHaveLength(1);
  });

  it("rejects malformed records", () => {
    expect(() => parseMatter({ ...matter, status: "unknown" })).toThrow();
    expect(() =>
      parseMatterList({ items: null, total: 0, limit: 50, offset: 0 }),
    ).toThrow();
  });
});

const clientList = {
  items: [
    {
      id: 2,
      full_name: "María López",
      phone: "5512345678",
      email: null,
      address: null,
      notes: null,
      created_at: matter.created_at,
      updated_at: matter.updated_at,
    },
    {
      id: 3,
      full_name: "Ana García",
      phone: "5512345679",
      email: null,
      address: null,
      notes: null,
      created_at: matter.created_at,
      updated_at: matter.updated_at,
    },
  ],
  total: 2,
  limit: 100,
  offset: 0,
};

const response = (payload: unknown, status = 200): Partial<Response> => ({
  ok: true,
  status,
  statusText: "OK",
  headers: new Headers(),
  json: () => Promise.resolve(payload),
});

const renderMatterRoute = (
  path: string,
  fetchMock: ReturnType<typeof vi.fn>,
) => {
  vi.stubGlobal("fetch", fetchMock);
  const queryClient = createQueryClient();
  queryClient.setQueryDefaults(["clients"], { retry: false });
  queryClient.setQueryDefaults(["matters"], { retry: false });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[path]}>
        <Routes>
          <Route path="/matters/new" element={<NewMatterPage />} />
          <Route
            path="/matters/:matterId/edit"
            element={<MatterDetailPage edit />}
          />
          <Route path="/matters/:matterId" element={<p>Detalle</p>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
};

describe("matter client selector", () => {
  it("shows empty and error states for client options", async () => {
    let resolveClients: ((value: Partial<Response>) => void) | undefined;
    const pendingFetch = vi.fn().mockReturnValue(
      new Promise<Partial<Response>>((resolve) => {
        resolveClients = resolve;
      }),
    );
    const pendingView = renderMatterRoute("/matters/new", pendingFetch);
    await userEvent
      .setup()
      .click(
        screen.getByRole("combobox", { name: t("matters.fields.client") }),
      );
    expect(
      screen.getByText(t("matters.fields.clientLoading")),
    ).toBeInTheDocument();
    resolveClients?.(response({ ...clientList, items: [], total: 0 }));
    pendingView.unmount();

    const emptyFetch = vi
      .fn()
      .mockResolvedValue(response({ ...clientList, items: [], total: 0 }));
    const { unmount } = renderMatterRoute("/matters/new", emptyFetch);
    await userEvent
      .setup()
      .click(
        screen.getByRole("combobox", { name: t("matters.fields.client") }),
      );
    expect(
      await screen.findByText(t("matters.fields.clientEmpty")),
    ).toBeInTheDocument();
    unmount();

    renderMatterRoute(
      "/matters/new",
      vi.fn().mockResolvedValue(response({ ...clientList, items: null })),
    );
    await userEvent
      .setup()
      .click(
        screen.getByRole("combobox", { name: t("matters.fields.client") }),
      );
    expect(
      await screen.findByText(t("matters.fields.clientError")),
    ).toBeInTheDocument();
  });

  it("filters clients by name and creates with the selected client id", async () => {
    const fetchMock = vi
      .fn()
      .mockImplementation((url: string, options?: RequestInit) => {
        if (options?.method === "POST")
          return Promise.resolve(response({ ...matter, client_id: 3 }, 201));
        return Promise.resolve(response(clientList));
      });
    renderMatterRoute("/matters/new", fetchMock);
    const user = userEvent.setup();
    const client = screen.getByRole("combobox", {
      name: t("matters.fields.client"),
    });
    await user.type(client, "Ana");
    await user.click(await screen.findByRole("button", { name: "Ana García" }));
    await user.type(
      screen.getByLabelText(t("matters.fields.title")),
      "Divorcio",
    );
    await user.type(
      screen.getByLabelText(t("matters.fields.type")),
      "Familiar",
    );
    await user.click(screen.getByRole("button", { name: t("matters.save") }));
    await waitFor(() =>
      expect(
        fetchMock.mock.calls.some(
          ([url, options]) =>
            String(url).includes("/matters") &&
            (options as RequestInit | undefined)?.method === "POST",
        ),
      ).toBe(true),
    );
    const createCall = fetchMock.mock.calls.find(
      ([, options]) => (options as RequestInit | undefined)?.method === "POST",
    );
    const requestBody = (createCall?.[1] as RequestInit | undefined)?.body;
    expect(typeof requestBody === "string" ? requestBody : "").toContain(
      '"client_id":3',
    );
    expect(
      fetchMock.mock.calls.some(([url]) => String(url).includes("search=Ana")),
    ).toBe(true);
  });

  it("preselects a contextual client and validates required fields", async () => {
    renderMatterRoute(
      "/matters/new?clientId=2",
      vi.fn().mockResolvedValue(response(clientList)),
    );
    expect(await screen.findByDisplayValue("María López")).toBeInTheDocument();
    await userEvent
      .setup()
      .click(screen.getByRole("button", { name: t("matters.save") }));
    expect(screen.getByRole("alert")).toHaveTextContent(
      t("matters.validation"),
    );
  });

  it("asks for confirmation before changing the client while editing", async () => {
    const fetchMock = vi
      .fn()
      .mockImplementation((url: string, options?: RequestInit) => {
        if (options?.method === "PATCH")
          return Promise.resolve(response({ ...matter, client_id: 3 }));
        if (String(url).includes("/clients"))
          return Promise.resolve(response(clientList));
        return Promise.resolve(response(matter));
      });
    const confirm = vi
      .spyOn(window, "confirm")
      .mockReturnValueOnce(false)
      .mockReturnValueOnce(true);
    renderMatterRoute("/matters/1/edit", fetchMock);
    const user = userEvent.setup();
    await user.click(
      await screen.findByRole("combobox", { name: t("matters.fields.client") }),
    );
    await user.click(await screen.findByRole("button", { name: "Ana García" }));
    await user.click(screen.getByRole("button", { name: t("matters.save") }));
    expect(
      fetchMock.mock.calls.some(
        ([, options]) =>
          (options as RequestInit | undefined)?.method === "PATCH",
      ),
    ).toBe(false);
    await user.click(screen.getByRole("button", { name: t("matters.save") }));
    await waitFor(() =>
      expect(
        fetchMock.mock.calls.some(
          ([, options]) =>
            (options as RequestInit | undefined)?.method === "PATCH",
        ),
      ).toBe(true),
    );
    expect(confirm).toHaveBeenCalledTimes(2);
  });

  it("saves edits without confirmation when the client is unchanged", async () => {
    const fetchMock = vi
      .fn()
      .mockImplementation((url: string, options?: RequestInit) => {
        if (options?.method === "PATCH")
          return Promise.resolve(response(matter));
        if (String(url).includes("/clients"))
          return Promise.resolve(response(clientList));
        return Promise.resolve(response(matter));
      });
    const confirm = vi.spyOn(window, "confirm");
    renderMatterRoute("/matters/1/edit", fetchMock);
    await screen.findByDisplayValue("María López");
    await userEvent
      .setup()
      .click(screen.getByRole("button", { name: t("matters.save") }));
    await waitFor(() =>
      expect(
        fetchMock.mock.calls.some(
          ([, options]) =>
            (options as RequestInit | undefined)?.method === "PATCH",
        ),
      ).toBe(true),
    );
    expect(confirm).not.toHaveBeenCalled();
  });
});

it("renders a matter list item without an optional next action", async () => {
  vi.stubGlobal(
    "fetch",
    vi
      .fn()
      .mockResolvedValue(
        response({
          items: [{ ...matter, next_action: null }],
          total: 1,
          limit: 50,
          offset: 0,
        }),
      ),
  );
  const queryClient = createQueryClient();
  render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <MatterList />
      </MemoryRouter>
    </QueryClientProvider>,
  );
  expect(
    await screen.findByRole("link", { name: matter.title }),
  ).toBeInTheDocument();
  expect(
    screen.queryByText(t("matters.next"), { exact: false }),
  ).not.toBeInTheDocument();
});
