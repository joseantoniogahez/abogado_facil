import { QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import axe from "axe-core";

import { createQueryClient } from "@/app/query-client";
import { AiSettingsPage } from "@/features/ai-settings/AiSettingsPage";
import { t } from "@/shared/i18n/ui-text";

const renderPage = () => {
  const queryClient = createQueryClient();
  const view = render(
    <QueryClientProvider client={queryClient}>
      <AiSettingsPage />
    </QueryClientProvider>,
  );
  return { queryClient, view };
};

describe("AiSettingsPage", () => {
  it("loads provider status and saves a key", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({ ok: true, status: 200, json: () => Promise.resolve({ items: [{ provider: "openai", configured: true, created_at: "2026-01-01T00:00:00Z", updated_at: "2026-01-01T00:00:00Z" }] }) })
      .mockResolvedValue({ ok: true, status: 200, json: () => Promise.resolve({ provider: "gemini", configured: true, created_at: "2026-01-01T00:00:00Z", updated_at: "2026-01-01T00:00:00Z" }) });
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup();
    renderPage();

    expect(await screen.findByText(t("aiSettings.configured"))).toBeInTheDocument();
    await user.type(screen.getByLabelText(t("aiSettings.key"), { selector: "#gemini-key" }), "gemini-secret");
    await user.click(screen.getAllByRole("button", { name: t("aiSettings.save") })[1]);
    expect(await screen.findByRole("status")).toHaveTextContent(t("aiSettings.success.save"));
    expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining("/ai/credentials/gemini"), expect.objectContaining({ method: "PUT" }));
  });

  it("keeps the secret input empty and renders an accessible notice", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true, status: 200, json: () => Promise.resolve({ items: [] }) }));
    const { view } = renderPage();
    expect(await screen.findByRole("note")).toHaveTextContent(t("aiSettings.notice"));
    expect(await screen.findAllByText(t("aiSettings.notConfigured"))).toHaveLength(2);
    expect(screen.getByLabelText(t("aiSettings.key"), { selector: "#openai-key" })).toHaveValue("");
    expect((await axe.run(view.container, { rules: { "color-contrast": { enabled: false } } })).violations).toHaveLength(0);
  });

  it("deletes a configured credential", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({ ok: true, status: 200, json: () => Promise.resolve({ items: [{ provider: "openai", configured: true, created_at: "2026-01-01T00:00:00Z", updated_at: "2026-01-01T00:00:00Z" }] }) })
      .mockResolvedValueOnce({ ok: true, status: 204 })
      .mockResolvedValue({ ok: true, status: 200, json: () => Promise.resolve({ items: [] }) });
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup();
    renderPage();
    await screen.findByText(t("aiSettings.configured"));
    await user.click(screen.getAllByRole("button", { name: t("aiSettings.delete") })[0]);
    await waitFor(() => expect(screen.getByRole("status")).toHaveTextContent(t("aiSettings.success.delete")));
  });
});
