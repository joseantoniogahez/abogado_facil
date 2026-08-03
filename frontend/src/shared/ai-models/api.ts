import { defaultQueryPolicy } from "@/app/query-policy";
import { apiRequest } from "@/shared/api/http";

import { parseAiModelCatalog } from "./contracts";

export const AI_MODELS_QUERY_KEY = ["ai-models"] as const;
export const aiModelsQueryOptions = {
  queryKey: AI_MODELS_QUERY_KEY,
  queryFn: () => apiRequest("/ai/credentials/models", { parse: parseAiModelCatalog }),
  ...defaultQueryPolicy,
};
