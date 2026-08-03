import { QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import axe from "axe-core";

import { createQueryClient } from "@/app/query-client";
import { AiSettingsPage } from "@/features/ai-settings/AiSettingsPage";
import { t } from "@/shared/i18n/ui-text";

const credential = (provider: "openai" | "gemini") => ({
  provider,
  configured: true,
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
});
const response = (payload?: unknown, status = 200) => ({
  ok: status >= 200 && status < 300,
  status,
  headers: { get: () => null },
  json: () => Promise.resolve(payload),
});
const renderPage = () => {
  const queryClient = createQueryClient();
  const view = render(<QueryClientProvider client={queryClient}><AiSettingsPage /></QueryClientProvider>);
  return { queryClient, view };
};

describe("AiSettingsPage", () => {
  it("guides provider selection, saves a key, and verifies discovered models", async () => {
    let configured = false;
    const fetchMock = vi.fn((url: string, options?: RequestInit) => {
      if (url.includes("/ai/credentials/models")) return Promise.resolve(response({ providers: [{ provider: "gemini", models: [{ id: "gemini-2", label: "Gemini 2" }] }] }));
      if (options?.method === "PUT") { configured = true; return Promise.resolve(response(credential("gemini"))); }
      return Promise.resolve(response({ items: configured ? [credential("gemini")] : [] }));
    });
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup();
    renderPage();

    await user.click(await screen.findByRole("radio", { name: /Google Gemini/ }));
    expect(screen.getByRole("heading", { name: t("aiSettings.guide.gemini.title") })).toBeVisible();
    await user.type(screen.getByLabelText(t("aiSettings.key")), "gemini-secret");
    await user.click(screen.getByRole("button", { name: t("aiSettings.save") }));

    expect(await screen.findByText(t("aiSettings.verify.success", { count: 1 }))).toBeVisible();
    expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining("/ai/credentials/gemini"), expect.objectContaining({ method: "PUT" }));
  });

  it("presents a clearly labelled local mock demo without making AI requests", async () => {
    const fetchMock = vi.fn().mockResolvedValue(response({ items: [] }));
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup();
    renderPage();

    await user.click(await screen.findByRole("radio", { name: /Probar demo/ }));
    expect(screen.getByText(t("aiSettings.demo.badge"))).toBeVisible();
    expect(screen.getByText(t("aiSettings.demo.body"))).toBeVisible();
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock.mock.calls.some(([url]) => String(url).includes("/ai/credentials/models"))).toBe(false);
  });

  it("keeps secret inputs empty and the guided states accessible", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(response({ items: [] })));
    const { view } = renderPage();
    expect(await screen.findByRole("note")).toHaveTextContent(t("aiSettings.notice"));
    expect(await screen.findByLabelText(t("aiSettings.key"))).toHaveValue("");
    expect((await axe.run(view.container, { rules: { "color-contrast": { enabled: false } } })).violations).toHaveLength(0);
  });

  it("shows an actionable connection error and retries model discovery", async () => {
    let modelAttempts = 0;
    const fetchMock = vi.fn((url: string) => {
      if (url.includes("/ai/credentials/models")) {
        modelAttempts += 1;
        return Promise.resolve(modelAttempts === 1 ? response({ detail: "provider unavailable" }, 503) : response({ providers: [{ provider: "openai", models: [{ id: "gpt", label: "GPT" }] }] }));
      }
      return Promise.resolve(response({ items: [credential("openai")] }));
    });
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup();
    renderPage();

    expect(await screen.findByRole("alert")).toHaveTextContent(t("aiSettings.verify.error"));
    await user.click(screen.getByRole("button", { name: t("aiSettings.verify.retry") }));
    expect(await screen.findByText(t("aiSettings.verify.success", { count: 1 }))).toBeVisible();
  });

  it("deletes an existing credential and clears stale action errors", async () => {
    let configured = true;
    const fetchMock = vi.fn((url: string, options?: RequestInit) => {
      if (url.includes("/ai/credentials/models")) return Promise.resolve(response({ providers: [{ provider: "openai", models: [{ id: "gpt", label: "GPT" }] }] }));
      if (options?.method === "DELETE") { configured = false; return Promise.resolve(response(undefined, 204)); }
      return Promise.resolve(response({ items: configured ? [credential("openai")] : [] }));
    });
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup();
    renderPage();

    await screen.findByText(t("aiSettings.verify.success", { count: 1 }));
    await user.click(screen.getByRole("button", { name: t("aiSettings.delete") }));
    await waitFor(() => expect(screen.getByRole("status")).toHaveTextContent(t("aiSettings.success.delete")));
  });
});
