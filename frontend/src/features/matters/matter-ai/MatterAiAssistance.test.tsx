import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { vi } from "vitest";

import { t } from "@/shared/i18n/ui-text";

import { MatterAiAssistance } from "./MatterAiAssistance";

const clipboardWriteText = vi.fn();

const result = (status = "pending") => ({
  id: 7,
  matter_id: 3,
  execution_id: "execution",
  feature: "intake_analysis",
  provider: "openai",
  model: "gpt-4.1-mini",
  source_version: "version",
  source_snapshot: {},
  generated_content: { summary: "Resumen", relevant_facts: ["Hecho"] },
  reviewed_content: status === "pending" ? null : { summary: "Resumen", relevant_facts: ["Hecho"] },
  review_status: status,
  problem_report: null,
  converted_actions: [],
  is_stale: false,
  reviewed_at: null,
  created_at: "2026-07-26T12:00:00Z",
  updated_at: "2026-07-26T12:00:00Z",
});

const response = (body: unknown, ok = true) =>
  Promise.resolve(new Response(JSON.stringify(body), {
    status: ok ? 200 : 500,
    headers: { "Content-Type": "application/json" },
  }));

const renderFeature = () => {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } });
  return render(
    <QueryClientProvider client={client}>
      <MatterAiAssistance matterId={3} />
    </QueryClientProvider>,
  );
};

describe("MatterAiAssistance", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    clipboardWriteText.mockReset().mockResolvedValue(undefined);
    Object.assign(navigator, { clipboard: { writeText: clipboardWriteText } });
  });

  it("previews context, executes a function and persists human review", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch")
      .mockImplementationOnce(() => response({ items: [], total: 0 }))
      .mockImplementationOnce(() => response({
        feature: "intake_analysis",
        provider: "openai",
        model: "gpt-4.1-mini",
        included_sources: ["relato proporcionado"],
        excluded_sources: ["documentos"],
        character_count: 40,
        estimated_max_output_tokens: 1200,
        cost_notice: "Costo BYOK",
        confirmation_token: "a".repeat(64),
      }))
      .mockImplementationOnce(() => response(result()))
      .mockImplementationOnce(() => response({ items: [result()], total: 1 }))
      .mockImplementationOnce(() => response(result("accepted")))
      .mockImplementationOnce(() => response({ items: [result("accepted")], total: 1 }))
      .mockImplementationOnce(() => response({
        ...result("accepted"),
        converted_actions: [{ action_type: "note", content: "Resumen" }],
      }))
      .mockImplementationOnce(() => response({ items: [result("accepted")], total: 1 }));

    renderFeature();
    await screen.findByText(t("ai.results.empty"));
    expect(screen.getByRole("option", { name: t("ai.feature.matter_summary") })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: t("ai.feature.matter_timeline") })).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText(t("ai.feature.label")), { target: { value: "client_questions" } });
    fireEvent.change(screen.getByLabelText(t("ai.provider")), { target: { value: "gemini" } });
    expect(screen.getByLabelText(t("ai.model"))).toHaveValue("gemini-3.5-flash-lite");
    expect(screen.getByRole("option", { name: "Gemini 2.5 Flash" })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "Gemini 2.5 Flash-Lite" })).toHaveValue("gemini-2.5-flash-lite");
    expect(screen.queryByRole("option", { name: "GPT-4.1" })).not.toBeInTheDocument();
    fireEvent.change(screen.getByLabelText(t("ai.provider")), { target: { value: "openai" } });
    expect(screen.getByRole("option", { name: "GPT-4.1" })).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText(t("ai.feature.label")), { target: { value: "intake_analysis" } });
    fireEvent.change(screen.getByLabelText(t("ai.narrative")), {
      target: { value: "Relato suficientemente largo para la prueba." },
    });
    fireEvent.click(screen.getByLabelText(t("ai.includeDescription")));
    fireEvent.click(screen.getByRole("button", { name: t("ai.preview") }));
    await screen.findByText("Costo BYOK");
    fireEvent.click(screen.getByRole("button", { name: t("ai.execute") }));
    await screen.findByText(t("ai.feature.intake_analysis"));
    fireEvent.change(screen.getByLabelText(t("ai.review.problem")), {
      target: { value: "Falta contexto" },
    });
    fireEvent.click(screen.getByRole("button", { name: t("ai.review.accept") }));
    await waitFor(() => expect(screen.getByText(/Aceptado/)).toBeInTheDocument());
    fireEvent.click(screen.getByRole("button", { name: t("ai.actions.convert") }));
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(8));
    fireEvent.click(screen.getByRole("button", { name: t("ai.result.regenerate") }));
    expect(screen.getByLabelText(t("ai.narrative"))).toHaveValue("");
    expect(screen.getByRole("status")).toHaveTextContent(t("ai.result.regenerationReady"));
  });

  it("renders recoverable API failures", async () => {
    vi.spyOn(globalThis, "fetch")
      .mockImplementationOnce(() => response({ items: [], total: 0 }))
      .mockImplementationOnce(() => response({}, false));
    renderFeature();
    await screen.findByText(t("ai.results.empty"));
    fireEvent.change(screen.getByLabelText(t("ai.narrative")), {
      target: { value: "Relato suficientemente largo para la prueba." },
    });
    fireEvent.click(screen.getByRole("button", { name: t("ai.preview") }));
    await screen.findByRole("alert");
  });

  it("renders dated and undated timeline events with their available source", async () => {
    const timelineContent = {
      events: [
        null,
        { date: 42, description: 9, source: false },
        { date: "2026-01-10", description: "Firma del contrato", source: "Contrato" },
        { date: null, description: "Consulta inicial", source: null },
      ],
    };
    const timeline = {
      ...result("accepted"),
      feature: "matter_timeline",
      generated_content: timelineContent,
      reviewed_content: timelineContent,
    };
    vi.spyOn(globalThis, "fetch").mockImplementationOnce(() => response({ items: [timeline], total: 1 }));
    renderFeature();
    expect(await screen.findByText("Firma del contrato")).toBeInTheDocument();
    expect(screen.getByText(`${t("ai.timeline.source")}: Contrato`)).toBeInTheDocument();
    expect(screen.getByText(t("ai.timeline.unknownDate"))).toBeInTheDocument();
    expect(screen.getByLabelText(t("ai.review.content"))).toHaveValue(
      "2026-01-10\tFirma del contrato\tContrato\n\tConsulta inicial\t",
    );
    fireEvent.click(screen.getByRole("button", { name: t("ai.review.copy") }));
    await waitFor(() =>
      expect(clipboardWriteText).toHaveBeenCalledWith(
        "2026-01-10 — Firma del contrato — Contrato\nFecha no determinada — Consulta inicial",
      ));
  });

  it("blocks conversion after editing an accepted result until the review persists", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch")
      .mockImplementationOnce(() => response({ items: [result("accepted")], total: 1 }))
      .mockImplementationOnce(() => response({}, false));
    renderFeature();
    const convert = await screen.findByRole("button", { name: t("ai.actions.convert") });
    expect(convert).toBeEnabled();
    fireEvent.change(screen.getByLabelText(t("ai.review.content")), {
      target: { value: "Resumen todavía no aceptado" },
    });
    expect(screen.queryByRole("button", { name: t("ai.actions.convert") })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: t("ai.review.accept") }));
    await screen.findByRole("alert");
    expect(screen.getByRole("button", { name: t("ai.review.copy") })).toBeDisabled();
    expect(screen.queryByRole("button", { name: t("ai.actions.convert") })).not.toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });
});
