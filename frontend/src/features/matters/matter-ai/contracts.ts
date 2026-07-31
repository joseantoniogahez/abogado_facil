import { expectNumberField, expectRecord, expectStringField } from "@/shared/api/contracts";

export type AiFeature
  = | "intake_analysis"
    | "client_questions"
    | "client_message"
    | "matter_summary"
    | "matter_timeline";

export interface AiContextPreview {
  feature: AiFeature;
  provider: string;
  model: string;
  included_sources: string[];
  excluded_sources: string[];
  character_count: number;
  estimated_max_output_tokens: number;
  cost_notice: string;
  confirmation_token: string;
}

export interface AiResult {
  id: number;
  matter_id: number;
  execution_id: string;
  feature: AiFeature;
  provider: string;
  model: string;
  source_version: string;
  source_snapshot: Record<string, unknown>;
  generated_content: Record<string, unknown>;
  reviewed_content: Record<string, unknown> | null;
  review_status: "pending" | "accepted" | "partially_accepted" | "rejected";
  converted_actions: Record<string, unknown>[];
  is_stale: boolean;
  created_at: string;
  updated_at: string;
}

const strings = (value: unknown, name: string) => {
  if (!Array.isArray(value) || value.some(item => typeof item !== "string"))
    throw new Error(`${name}: invalid string list`);
  return value as string[];
};
const array = (value: unknown, name: string): unknown[] => {
  if (!Array.isArray(value)) throw new Error(`${name}: invalid array`);
  return value;
};

export const parseAiPreview = (payload: unknown): AiContextPreview => {
  const item = expectRecord(payload, "AiContextPreview");
  return {
    feature: expectStringField(item, "feature", "AiContextPreview") as AiFeature,
    provider: expectStringField(item, "provider", "AiContextPreview"),
    model: expectStringField(item, "model", "AiContextPreview"),
    included_sources: strings(item.included_sources, "AiContextPreview.included_sources"),
    excluded_sources: strings(item.excluded_sources, "AiContextPreview.excluded_sources"),
    character_count: expectNumberField(item, "character_count", "AiContextPreview"),
    estimated_max_output_tokens: expectNumberField(item, "estimated_max_output_tokens", "AiContextPreview"),
    cost_notice: expectStringField(item, "cost_notice", "AiContextPreview"),
    confirmation_token: expectStringField(item, "confirmation_token", "AiContextPreview"),
  };
};

export const parseAiResult = (payload: unknown): AiResult => {
  const item = expectRecord(payload, "AiResult");
  return {
    id: expectNumberField(item, "id", "AiResult"),
    matter_id: expectNumberField(item, "matter_id", "AiResult"),
    execution_id: expectStringField(item, "execution_id", "AiResult"),
    feature: expectStringField(item, "feature", "AiResult") as AiFeature,
    provider: expectStringField(item, "provider", "AiResult"),
    model: expectStringField(item, "model", "AiResult"),
    source_version: expectStringField(item, "source_version", "AiResult"),
    source_snapshot: expectRecord(item.source_snapshot, "AiResult.source_snapshot"),
    generated_content: expectRecord(item.generated_content, "AiResult.generated_content"),
    reviewed_content: item.reviewed_content === null
      ? null
      : expectRecord(item.reviewed_content, "AiResult.reviewed_content"),
    review_status: expectStringField(item, "review_status", "AiResult") as AiResult["review_status"],
    converted_actions: array(item.converted_actions, "AiResult.converted_actions").map(action =>
      expectRecord(action, "AiResult.action"),
    ),
    is_stale: item.is_stale === true,
    created_at: expectStringField(item, "created_at", "AiResult"),
    updated_at: expectStringField(item, "updated_at", "AiResult"),
  };
};

export const parseAiResultList = (payload: unknown) => {
  const list = expectRecord(payload, "AiResultList");
  return {
    items: array(list.items, "AiResultList.items").map(parseAiResult),
    total: expectNumberField(list, "total", "AiResultList"),
  };
};
