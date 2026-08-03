import { expectRecord, expectStringField } from "@/shared/api/contracts";

export type AiProvider = "openai" | "gemini";
export interface AiModel { id: string; label: string }
export interface AiProviderModels { provider: AiProvider; models: AiModel[] }

export const parseAiModelCatalog = (payload: unknown): AiProviderModels[] => {
  const catalog = expectRecord(payload, "AiModelCatalog");
  if (!Array.isArray(catalog.providers)) throw new Error("AiModelCatalog: providers must be an array");
  return catalog.providers.map((value) => {
    const entry = expectRecord(value, "AiProviderModels");
    const provider = expectStringField(entry, "provider", "AiProviderModels");
    if (provider !== "openai" && provider !== "gemini") throw new Error("AiProviderModels: unsupported provider");
    if (!Array.isArray(entry.models)) throw new Error("AiProviderModels: models must be an array");
    return {
      provider,
      models: entry.models.map((model) => {
        const item = expectRecord(model, "AiModel");
        return {
          id: expectStringField(item, "id", "AiModel", { minLength: 1 }),
          label: expectStringField(item, "label", "AiModel", { minLength: 1 }),
        };
      }),
    };
  });
};
