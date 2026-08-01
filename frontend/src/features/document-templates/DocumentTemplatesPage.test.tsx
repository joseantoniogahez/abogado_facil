import { QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import axe from "axe-core";

import { createQueryClient } from "@/app/query-client";
import {
  parseDocumentDraft,
  parseDocumentDraftPreview,
  parseDocumentTemplateCatalog,
} from "@/features/document-templates/contracts";
import { DocumentTemplatesPage } from "@/features/document-templates/DocumentTemplatesPage";
import { t } from "@/shared/i18n/ui-text";

const template = (key: string, name: string) => ({
  key,
  name,
  description: `Descripción de ${name}`,
  purpose: `Finalidad de ${name}`,
  fields: [
    { key: "name", label: "Nombre", field_type: "text", required: true },
    { key: "details", label: "Detalles", field_type: "long_text", required: false },
    { key: "date", label: "Fecha", field_type: "date", required: false },
  ],
});

const catalog = {
  generation_available: true,
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

  it("previews controlled context and renders an editable generated draft", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({ ok: true, status: 200, json: () => Promise.resolve(catalog) })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve({
          template_key: "payment_demand",
          provider: "gemini",
          model: "gemini-2.5-flash",
          included_fields: ["Nombre"],
          character_count: 3,
          estimated_max_output_tokens: 1800,
          cost_notice: "Costo BYOK",
          confirmation_token: "a".repeat(64),
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: () => Promise.resolve({
          template_key: "payment_demand",
          content: "Borrador generado",
          provider: "gemini",
          model: "gemini-2.5-flash",
          execution_id: "execution-1",
          status: "draft",
          requires_professional_review: true,
        }),
      });
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup();
    renderPage();

    await screen.findByRole("region", { name: t("documentTemplates.catalogLabel") });
    await user.click(screen.getAllByRole("button", { name: t("documentTemplates.use") })[0]);
    await user.type(screen.getByLabelText(/Nombre/), "Ana");
    await user.type(screen.getByLabelText(/Detalles/), "Antecedentes");
    await user.type(screen.getByLabelText(/Fecha/), "2026-08-15");
    await user.selectOptions(screen.getByLabelText(t("documentDraft.provider")), "gemini");
    await user.selectOptions(screen.getByLabelText(t("documentDraft.model")), "gemini-2.5-flash");
    await user.click(screen.getByRole("button", { name: t("documentDraft.preview") }));
    expect(await screen.findByRole("complementary", { name: t("documentDraft.previewTitle") }))
      .toHaveTextContent("Costo BYOK");
    await user.click(screen.getByRole("button", { name: t("documentDraft.generate") }));
    const editor = await screen.findByLabelText(t("documentDraft.content"));
    expect(editor).toHaveValue("Borrador generado");
    await user.clear(editor);
    await user.type(editor, "Borrador revisado");
    expect(editor).toHaveValue("Borrador revisado");
    expect(screen.getByText(t("documentDraft.noAutomaticAction"))).toBeInTheDocument();
  });

  it("rejects invalid draft and catalog response contracts", () => {
    expect(() => parseDocumentTemplateCatalog({ ...catalog, generation_available: false })).toThrow();
    expect(() => parseDocumentDraftPreview({
      template_key: "payment_demand",
      provider: "openai",
      model: "model",
      included_fields: "invalid",
      character_count: 1,
      estimated_max_output_tokens: 1,
      cost_notice: "notice",
      confirmation_token: "a".repeat(64),
    })).toThrow();
    expect(() => parseDocumentDraft({
      template_key: "payment_demand",
      content: "draft",
      provider: "openai",
      model: "model",
      execution_id: "execution",
      status: "final",
      requires_professional_review: false,
    })).toThrow();
  });
});
