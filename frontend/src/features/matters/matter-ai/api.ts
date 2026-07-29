import { defaultQueryPolicy } from "@/app/query-policy";
import { apiRequest } from "@/shared/api/http";

import { type AiFeature, parseAiPreview, parseAiResult, parseAiResultList } from "./contracts";

export interface AiExecutionInput {
  feature: AiFeature;
  narrative: string;
  provider: "openai" | "gemini";
  model: string;
  include_matter_description: boolean;
  regenerates_result_id?: number;
}

export const matterAiQueryKey = (matterId: number) => ["matter-ai", matterId] as const;
export const matterAiQueryOptions = (matterId: number) => ({
  queryKey: matterAiQueryKey(matterId),
  queryFn: () => apiRequest(`/matters/${matterId}/ai/results`, { parse: parseAiResultList }),
  ...defaultQueryPolicy,
});
const post = <T>(path: string, payload: unknown, parse: (value: unknown) => T) =>
  apiRequest(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    parse,
  });
export const previewMatterAi = (matterId: number, input: AiExecutionInput) =>
  post(`/matters/${matterId}/ai/preview`, input, parseAiPreview);
export const executeMatterAi = (matterId: number, input: AiExecutionInput, confirmationToken: string) =>
  post(`/matters/${matterId}/ai/results`, { ...input, confirmation_token: confirmationToken }, parseAiResult);
export const reviewMatterAi = (
  matterId: number,
  resultId: number,
  status: string,
  content?: Record<string, unknown>,
  problemReport?: string,
) =>
  apiRequest(`/matters/${matterId}/ai/results/${resultId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      status,
      content: status === "rejected" ? null : content,
      problem_report: problemReport?.trim() ? problemReport.trim() : null,
    }),
    parse: parseAiResult,
  });
export const convertMatterAi = (
  matterId: number,
  resultId: number,
  actionType: string,
  content: string,
  dueDate?: string,
) =>
  post(`/matters/${matterId}/ai/results/${resultId}/actions`, {
    action_type: actionType,
    content,
    due_date: dueDate?.trim() ? dueDate : null,
  }, parseAiResult);
