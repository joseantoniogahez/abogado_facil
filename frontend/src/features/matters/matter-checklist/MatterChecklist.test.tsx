import { QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { createQueryClient } from "@/app/query-client";
import { t } from "@/shared/i18n/ui-text";

import { parseChecklistItem } from "./contracts";
import { MatterChecklist } from "./MatterChecklist";

const item = {
  id: 1,
  matter_id: 3,
  label: "Acta de matrimonio",
  status: "pending",
  is_custom: false,
  position: 0,
  created_at: "2026-07-14T10:00:00Z",
  updated_at: "2026-07-14T10:00:00Z",
};
const response = (payload: unknown, status = 200): Partial<Response> => ({
  ok: status < 400,
  status,
  statusText: status < 400 ? "OK" : "Error",
  headers: new Headers(),
  json: () => Promise.resolve(payload),
});

describe("MatterChecklist", () => {
  it("parses status strictly", () => {
    expect(parseChecklistItem(item).status).toBe("pending");
    expect(() => parseChecklistItem({ ...item, status: "invalid" })).toThrow();
  });
  it("renders, changes status, and adds a custom item", async () => {
    const fetchMock = vi.fn().mockImplementation((_url: string, options?: RequestInit) => {
      const method = options?.method ?? "GET";
      if (method === "PATCH") return Promise.resolve(response({ ...item, status: "complete" }));
      if (method === "POST")
        return Promise.resolve(
          response({ ...item, id: 2, label: "Fotografías", is_custom: true }, 201),
        );
      return Promise.resolve(response({ items: [item], total: 1 }));
    });
    vi.stubGlobal("fetch", fetchMock);
    const client = createQueryClient();
    client.setQueryDefaults(["matter-checklist"], { retry: false });
    render(
      <QueryClientProvider client={client}>
        <MatterChecklist matterId={3} />
      </QueryClientProvider>,
    );
    const user = userEvent.setup();
    expect(await screen.findByText(item.label)).toBeInTheDocument();
    await user.selectOptions(
      screen.getByLabelText(`${t("matterChecklist.statusLabel")}: ${item.label}`),
      "complete",
    );
    await waitFor(() =>
      expect(
        fetchMock.mock.calls.some(
          call => (call[1] as RequestInit | undefined)?.method === "PATCH",
        ),
      ).toBe(true),
    );
    await user.type(screen.getByLabelText(t("matterChecklist.newLabel")), "Fotografías");
    await user.click(screen.getByRole("button", { name: t("matterChecklist.add") }));
    await waitFor(() =>
      expect(
        fetchMock.mock.calls.some(
          call => (call[1] as RequestInit | undefined)?.method === "POST",
        ),
      ).toBe(true),
    );
  });
});
