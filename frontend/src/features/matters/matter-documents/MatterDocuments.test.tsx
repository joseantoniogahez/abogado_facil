import { createQueryClient } from "@/app/query-client";
import { t } from "@/shared/i18n/ui-text";
import { QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import axe from "axe-core";
import { afterEach, describe, expect, it, vi } from "vitest";
import { MatterDocuments } from "./MatterDocuments";
import { parseMatterDocument, parseMatterDocumentList } from "./contracts";

const documentRecord = {
  id: "doc-1", matter_id: 7, original_filename: "demanda.pdf", document_type: "filing",
  media_type: "application/pdf", size_bytes: 2048, created_at: "2026-07-14T12:00:00Z",
};
const jsonResponse = (payload: unknown, status = 200): Partial<Response> => ({
  ok: status >= 200 && status < 300, status, statusText: status === 200 ? "OK" : "Error",
  headers: new Headers(), json: () => Promise.resolve(payload),
});
const renderDocuments = (fetchMock: ReturnType<typeof vi.fn>) => {
  vi.stubGlobal("fetch", fetchMock);
  const client = createQueryClient();
  client.setQueryDefaults(["matter-documents"], { retry: false });
  return render(<QueryClientProvider client={client}><MatterDocuments matterId={7} /></QueryClientProvider>);
};

afterEach(() => vi.restoreAllMocks());

describe("matter document contracts", () => {
  it("parses records and lists", () => {
    expect(parseMatterDocument(documentRecord).document_type).toBe("filing");
    expect(parseMatterDocumentList({ items: [documentRecord], total: 1 }).items).toHaveLength(1);
  });
  it("rejects malformed records and lists", () => {
    expect(() => parseMatterDocument({ ...documentRecord, document_type: "bad" })).toThrow();
    expect(() => parseMatterDocumentList({ items: null, total: 0 })).toThrow();
  });
});

describe("MatterDocuments", () => {
  it("has no obvious accessibility violations in its empty state", async () => {
    const view = renderDocuments(vi.fn().mockResolvedValue(jsonResponse({ items: [], total: 0 })));
    await screen.findByText(t("matterDocuments.empty"));
    expect((await axe.run(view.container, { rules: { "color-contrast": { enabled: false } } })).violations).toHaveLength(0);
  });
  it("shows empty, required, format, size, upload and list states", async () => {
    let items: typeof documentRecord[] = [];
    const fetchMock = vi.fn((_url: string, options?: RequestInit) => {
      if (options?.method === "POST") { items = [documentRecord]; return Promise.resolve(jsonResponse(documentRecord, 201)); }
      return Promise.resolve(jsonResponse({ items, total: items.length }));
    });
    renderDocuments(fetchMock);
    expect(await screen.findByText(t("matterDocuments.empty"))).toBeInTheDocument();
    const user = userEvent.setup({ applyAccept: false });
    await user.click(screen.getByRole("button", { name: t("matterDocuments.upload") }));
    expect(screen.getByRole("alert")).toHaveTextContent(t("matterDocuments.validation.required"));
    const input = screen.getByLabelText(t("matterDocuments.file"));
    await user.upload(input, new File(["bad"], "bad.exe"));
    await user.click(screen.getByRole("button", { name: t("matterDocuments.upload") }));
    expect(screen.getByRole("alert")).toHaveTextContent(t("matterDocuments.validation.format"));
    await user.upload(input, new File([new Uint8Array(10 * 1024 * 1024 + 1)], "large.pdf", { type: "application/pdf" }));
    await user.click(screen.getByRole("button", { name: t("matterDocuments.upload") }));
    expect(screen.getByRole("alert")).toHaveTextContent(t("matterDocuments.validation.size"));
    await user.selectOptions(screen.getByLabelText(t("matterDocuments.type")), "filing");
    await user.upload(input, new File(["%PDF-test"], "demanda.pdf", { type: "application/pdf" }));
    await user.click(screen.getByRole("button", { name: t("matterDocuments.upload") }));
    expect(await screen.findByText("demanda.pdf")).toBeInTheDocument();
    const post = fetchMock.mock.calls.find(([, options]) => options?.method === "POST");
    expect(post![1]?.body).toBeInstanceOf(FormData);
  });

  it("retries list errors", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(jsonResponse({ detail: "bad" }, 400))
      .mockResolvedValueOnce(jsonResponse({ items: [], total: 0 }));
    renderDocuments(fetchMock);
    expect(await screen.findByText(t("matterDocuments.error"))).toBeInTheDocument();
    await userEvent.setup().click(screen.getByRole("button", { name: t("matterDocuments.retry") }));
    expect(await screen.findByText(t("matterDocuments.empty"))).toBeInTheDocument();
  });

  it("downloads with the server filename and deletes after confirmation", async () => {
    let items = [documentRecord];
    const blob = new Blob(["pdf"]);
    const fetchMock = vi.fn((url: string, options?: RequestInit) => {
      if (String(url).endsWith("/download")) return Promise.resolve({ ok: true, status: 200, headers: new Headers({ "Content-Disposition": "attachment; filename*=UTF-8''escrito%20final.pdf" }), blob: () => Promise.resolve(blob) });
      if (options?.method === "DELETE") { items = []; return Promise.resolve(jsonResponse(undefined, 204)); }
      return Promise.resolve(jsonResponse({ items, total: items.length }));
    });
    const createObjectURL = vi.fn(() => "blob:test");
    const revokeObjectURL = vi.fn();
    vi.stubGlobal("URL", Object.assign(URL, { createObjectURL, revokeObjectURL }));
    const click = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => undefined);
    vi.spyOn(window, "confirm").mockReturnValue(true);
    renderDocuments(fetchMock);
    await screen.findByText("demanda.pdf");
    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: t("matterDocuments.download") }));
    await waitFor(() => expect(click).toHaveBeenCalled());
    expect(createObjectURL).toHaveBeenCalledWith(blob);
    expect(revokeObjectURL).toHaveBeenCalledWith("blob:test");
    await user.click(screen.getByRole("button", { name: t("matterDocuments.delete") }));
    expect(await screen.findByText(t("matterDocuments.empty"))).toBeInTheDocument();
  });

  it("keeps a document when deletion is cancelled and exposes action errors", async () => {
    const fetchMock = vi.fn((url: string) => String(url).endsWith("/download")
      ? Promise.resolve(jsonResponse({ detail: "failure" }, 400))
      : Promise.resolve(jsonResponse({ items: [documentRecord], total: 1 })));
    vi.spyOn(window, "confirm").mockReturnValue(false);
    renderDocuments(fetchMock);
    await screen.findByText("demanda.pdf");
    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: t("matterDocuments.delete") }));
    expect(fetchMock.mock.calls.some(([, options]) => (options as RequestInit | undefined)?.method === "DELETE")).toBe(false);
    await user.click(screen.getByRole("button", { name: t("matterDocuments.download") }));
    expect(await screen.findByRole("alert")).toHaveTextContent(t("matterDocuments.actionError"));
  });
});
