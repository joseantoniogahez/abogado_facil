import { QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { createQueryClient } from "@/app/query-client";
import { t } from "@/shared/i18n/ui-text";

import { parseMatterNote, parseMatterNoteList } from "./contracts";
import { MatterNotes } from "./MatterNotes";

const note = {
  id: 7,
  matter_id: 3,
  content: "Llamada inicial",
  is_relevant: false,
  created_at: "2026-07-12T10:00:00Z",
  updated_at: "2026-07-12T10:00:00Z",
};

const response = (payload: unknown, status = 200): Partial<Response> => ({
  ok: status >= 200 && status < 300,
  status,
  statusText: status >= 400 ? "Error" : "OK",
  headers: new Headers(),
  json: () => Promise.resolve(payload),
});

const renderNotes = (fetchMock: ReturnType<typeof vi.fn>) => {
  vi.stubGlobal("fetch", fetchMock);
  const queryClient = createQueryClient();
  queryClient.setQueryDefaults(["matter-notes"], { retry: false });
  return render(
    <QueryClientProvider client={queryClient}>
      <MatterNotes matterId={3} />
    </QueryClientProvider>,
  );
};

const methodForCall = (call: unknown[]): string | undefined => {
  const options = call[1] as RequestInit | undefined;
  return options?.method;
};

describe("matter note contracts", () => {
  it("parses records and rejects malformed lists", () => {
    expect(parseMatterNote(note).content).toBe(note.content);
    expect(parseMatterNoteList({ items: [note], total: 1 }).items).toHaveLength(1);
    expect(() => parseMatterNoteList({ items: null, total: 0 })).toThrow();
  });
});

describe("MatterNotes", () => {
  it("renders loading, empty, and recoverable error states", async () => {
    let resolveRequest: ((value: Partial<Response>) => void) | undefined;
    const pending = vi.fn().mockReturnValue(
      new Promise<Partial<Response>>((resolve) => {
        resolveRequest = resolve;
      }),
    );
    const pendingView = renderNotes(pending);
    expect(screen.getByText(t("matterNotes.loading"))).toBeInTheDocument();
    resolveRequest?.(response({ items: [], total: 0 }));
    expect(await screen.findByText(t("matterNotes.empty"))).toBeInTheDocument();
    pendingView.unmount();

    const failed = vi
      .fn()
      .mockResolvedValueOnce(response({ items: null, total: 0 }))
      .mockResolvedValueOnce(response({ items: null, total: 0 }))
      .mockResolvedValueOnce(response({ items: [], total: 0 }));
    renderNotes(failed);
    await userEvent
      .setup()
      .click(
        await screen.findByRole("button", { name: t("matterNotes.retry") }, { timeout: 5000 }),
      );
    await waitFor(() => expect(failed).toHaveBeenCalledTimes(3));
  });

  it("creates, edits, marks, and deletes a note after confirmation", async () => {
    let current = { ...note };
    const fetchMock = vi.fn().mockImplementation((url: string, options?: RequestInit) => {
      const method = options?.method ?? "GET";
      if (method === "POST") {
        current = { ...current, content: "Nueva llamada" };
        return Promise.resolve(response(current, 201));
      }
      if (method === "PATCH") {
        const payload = JSON.parse(
          typeof options?.body === "string" ? options.body : "{}",
        ) as Partial<typeof current>;
        current = { ...current, ...payload, updated_at: "2026-07-12T11:00:00Z" };
        return Promise.resolve(response(current));
      }
      if (method === "DELETE") return Promise.resolve(response(undefined, 204));
      return Promise.resolve(response({ items: [current], total: 1 }));
    });
    const confirm = vi
      .spyOn(window, "confirm")
      .mockReturnValueOnce(false)
      .mockReturnValueOnce(true);
    renderNotes(fetchMock);
    const user = userEvent.setup();

    expect(await screen.findByText(note.content)).toBeInTheDocument();
    await user.type(
      screen.getByLabelText(t("matterNotes.content"), { selector: "textarea" }),
      "  Nueva llamada  ",
    );
    await user.click(screen.getByRole("button", { name: t("matterNotes.add") }));
    await waitFor(() =>
      expect(fetchMock.mock.calls.some(call => methodForCall(call) === "POST")).toBe(true),
    );

    await user.click(screen.getByRole("button", { name: t("matterNotes.edit") }));
    const editField = screen.getAllByLabelText(t("matterNotes.content"), {
      selector: "textarea",
    })[1];
    await user.clear(editField);
    await user.type(editField, "Seguimiento editado");
    await user.click(screen.getByRole("button", { name: t("matterNotes.save") }));
    await waitFor(() =>
      expect(fetchMock.mock.calls.filter(call => methodForCall(call) === "PATCH")).toHaveLength(
        1,
      ),
    );

    await user.click(screen.getByRole("button", { name: t("matterNotes.mark") }));
    await waitFor(() =>
      expect(fetchMock.mock.calls.filter(call => methodForCall(call) === "PATCH")).toHaveLength(
        2,
      ),
    );

    const deleteButton = screen.getByRole("button", { name: t("matterNotes.delete") });
    await user.click(deleteButton);
    expect(fetchMock.mock.calls.some(call => methodForCall(call) === "DELETE")).toBe(false);
    await user.click(deleteButton);
    await waitFor(() =>
      expect(fetchMock.mock.calls.some(call => methodForCall(call) === "DELETE")).toBe(true),
    );
    expect(confirm).toHaveBeenCalledTimes(2);
  });
});
