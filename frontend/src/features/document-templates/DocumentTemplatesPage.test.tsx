import { QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import axe from "axe-core";

import { createQueryClient } from "@/app/query-client";
import { DocumentTemplatesPage } from "@/features/document-templates/DocumentTemplatesPage";
import { t } from "@/shared/i18n/ui-text";

const template = (key: string, name: string) => ({
  key,
  name,
  description: `Descripción de ${name}`,
  purpose: `Finalidad de ${name}`,
  fields: [{ key: "name", label: "Nombre", field_type: "text", required: true }],
});

const catalog = {
  generation_available: false,
  items: [
    template("payment_demand", "Requerimiento de pago"),
    template("payment_agreement", "Convenio de pago simple"),
    template("document_request", "Solicitud de documentos"),
    template("internal_matter_summary", "Resumen interno del asunto"),
  ],
};

const renderPage = () => render(
  <QueryClientProvider client={createQueryClient()}>
    <DocumentTemplatesPage />
  </QueryClientProvider>,
);

describe("DocumentTemplatesPage", () => {
  it("renders the four catalog entries and their required fields accessibly", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: () => Promise.resolve(catalog),
    }));

    const view = renderPage();

    expect(await screen.findByRole("region", { name: t("documentTemplates.catalogLabel") }))
      .toBeInTheDocument();
    expect(screen.getAllByRole("article")).toHaveLength(4);
    expect(screen.getAllByText(t("documentTemplates.required"))).toHaveLength(4);
    expect(screen.getByRole("note")).toHaveTextContent(t("documentTemplates.notice"));
    expect((await axe.run(view.container, { rules: { "color-contrast": { enabled: false } } })).violations)
      .toHaveLength(0);
  });

  it("shows a correlated recoverable error", async () => {
    const failedResponse = {
      ok: false,
      status: 500,
      headers: { get: () => "req-templates" },
      json: () => Promise.resolve({ detail: "Failed", code: "internal_error" }),
    };
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(failedResponse)
      .mockResolvedValueOnce(failedResponse)
      .mockResolvedValueOnce({ ok: true, status: 200, json: () => Promise.resolve(catalog) });
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup();
    renderPage();

    expect(await screen.findByRole("alert", undefined, { timeout: 3000 })).toHaveTextContent("req-templates");
    await user.click(screen.getByRole("button", { name: t("documentTemplates.retry") }));
    expect(await screen.findByRole("region", { name: t("documentTemplates.catalogLabel") }))
      .toBeInTheDocument();
  });
});
