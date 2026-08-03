import { AI_MODELS_QUERY_KEY } from "@/shared/ai-models/api";
import { apiRequest } from "@/shared/api/http";

import { type AiCredential, type AiProvider, parseAiCredential, parseAiCredentialList } from "./contracts";

export const AI_CREDENTIALS_QUERY_KEY = ["ai-credentials"] as const;
export { AI_MODELS_QUERY_KEY };

export const readAiCredentials = async (): Promise<AiCredential[]> =>
  apiRequest("/ai/credentials", { parse: parseAiCredentialList });

export const saveAiCredential = async ({ provider, apiKey }: { provider: AiProvider; apiKey: string }) =>
  apiRequest(`/ai/credentials/${provider}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ api_key: apiKey }),
    parse: parseAiCredential,
  });

export const deleteAiCredential = async (provider: AiProvider): Promise<void> =>
  apiRequest(`/ai/credentials/${provider}`, { method: "DELETE" });
