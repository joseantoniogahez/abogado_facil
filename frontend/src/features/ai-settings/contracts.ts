import {
  expectRecord,
  expectStringField,
} from "@/shared/api/contracts";

export type AiProvider = "openai" | "gemini";

export interface AiCredential {
  provider: AiProvider;
  configured: boolean;
  created_at: string;
  updated_at: string;
}

const parseProvider = (value: string, context: string): AiProvider => {
  if (value !== "openai" && value !== "gemini") {
    throw new Error(`${context}: unsupported provider`);
  }
  return value;
};

export const parseAiCredential = (payload: unknown): AiCredential => {
  const record = expectRecord(payload, "AiCredential");
  return {
    provider: parseProvider(expectStringField(record, "provider", "AiCredential"), "AiCredential"),
    configured: record.configured === true,
    created_at: expectStringField(record, "created_at", "AiCredential"),
    updated_at: expectStringField(record, "updated_at", "AiCredential"),
  };
};

export const parseAiCredentialList = (payload: unknown): AiCredential[] => {
  const record = expectRecord(payload, "AiCredentialList");
  if (!Array.isArray(record.items)) throw new Error("AiCredentialList: items must be an array");
  return record.items.map(parseAiCredential);
};
