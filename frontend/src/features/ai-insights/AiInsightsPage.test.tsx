import { QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";

import { createQueryClient } from "@/app/query-client";
import { AiInsightsPage } from "@/features/ai-insights/AiInsightsPage";
import { AI_INSIGHTS_QUERY_KEY } from "@/features/ai-insights/api";
import { t } from "@/shared/i18n/ui-text";

const metrics = {
  generated_at: "2026-08-01T00:00:00Z",
  stuck_after_minutes: 15,
  operational: {
    total_jobs: 4, successful_jobs: 3, failed_jobs: 1, success_rate: 75,
    average_latency_ms: 1200, estimated_input_tokens: 100, estimated_output_tokens: 50,
    cost_usd: null, cost_coverage_percent: 0, retry_count: 1, stuck_jobs: 1,
    errors: [{ name: "provider_timeout", count: 1 }],
  },
  product: {
    total_results: 3, accepted_results: 1, partially_accepted_results: 1,
    rejected_results: 0, pending_results: 1, edited_results: 1, converted_results: 1,
    regenerated_results: 1, abandoned_results: 1,
    feedback: [{ name: "useful", count: 2 }],
  },
};

const renderPage = (fetchMock: ReturnType<typeof vi.fn>) => {
  vi.stubGlobal("fetch", fetchMock);
  const client = createQueryClient();
  client.setQueryDefaults(AI_INSIGHTS_QUERY_KEY, { retry: false });
  return render(<QueryClientProvider client={client}><AiInsightsPage /></QueryClientProvider>);
};

describe("AiInsightsPage", () => {
  it("renders reproducible operational and product metrics", async () => {
    renderPage(vi.fn().mockResolvedValue({ ok: true, status: 200, json: () => Promise.resolve(metrics) }));
    expect(await screen.findByRole("heading", { name: t("aiInsights.title") })).toBeInTheDocument();
    expect(screen.getByText(t("aiInsights.costUnavailable"))).toBeInTheDocument();
    expect(screen.getByText(`${t("ai.feedback.useful")}: 2`)).toBeInTheDocument();
  });

  it("renders captured cost and empty feedback", async () => {
    renderPage(vi.fn().mockResolvedValue({
      ok: true, status: 200,
      json: () => Promise.resolve({
        ...metrics,
        operational: { ...metrics.operational, cost_usd: 1.25, cost_coverage_percent: 100 },
        product: { ...metrics.product, feedback: [] },
      }),
    }));
    expect(await screen.findByText("$1.25")).toBeInTheDocument();
    expect(screen.getByText(t("aiInsights.feedbackEmpty"))).toBeInTheDocument();
  });

  it("renders a recoverable load failure", async () => {
    renderPage(vi.fn().mockResolvedValue({ ok: false, status: 500, json: () => Promise.resolve({ detail: "fail" }) }));
    expect(await screen.findByRole("heading", { name: t("aiInsights.error") })).toBeInTheDocument();
  });
});
