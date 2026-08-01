import { queryOptions } from "@tanstack/react-query";

import { apiRequest } from "@/shared/api/http";

export interface NamedCount { name: string; count: number }
export interface AiInsights {
  generated_at: string;
  stuck_after_minutes: number;
  operational: {
    total_jobs: number; successful_jobs: number; failed_jobs: number; success_rate: number;
    average_latency_ms: number; estimated_input_tokens: number; estimated_output_tokens: number;
    cost_usd: number | null; cost_coverage_percent: number; retry_count: number; stuck_jobs: number;
    errors: NamedCount[];
  };
  product: {
    total_results: number; accepted_results: number; partially_accepted_results: number;
    rejected_results: number; pending_results: number; edited_results: number;
    converted_results: number; regenerated_results: number; abandoned_results: number;
    feedback: NamedCount[];
  };
}

export const AI_INSIGHTS_QUERY_KEY = ["ai-insights"] as const;
export const aiInsightsQueryOptions = () => queryOptions({
  queryKey: AI_INSIGHTS_QUERY_KEY,
  queryFn: () => apiRequest<AiInsights>("/ai/insights"),
});
