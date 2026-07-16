import { defaultQueryPolicy } from "@/app/query-policy";
import { apiRequest } from "@/shared/api/http";

import { type MatterInput, parseMatter, parseMatterList, parseMatterTypes } from "./contracts";
export const MATTERS_QUERY_KEY = ["matters"] as const;
export const MATTER_TYPES_QUERY_KEY = [...MATTERS_QUERY_KEY, "types"] as const;
export const matterTypesQueryOptions = () => ({
  queryKey: MATTER_TYPES_QUERY_KEY,
  queryFn: () => apiRequest("/matters/types", { parse: parseMatterTypes }),
  ...defaultQueryPolicy,
});
export const mattersQueryOptions = (clientId?: number) => ({
  queryKey: [...MATTERS_QUERY_KEY, "list", clientId ?? null],
  queryFn: () =>
    apiRequest(`/matters${clientId ? `?client_id=${clientId}` : ""}`, { parse: parseMatterList }),
  ...defaultQueryPolicy,
});
export const matterQueryOptions = (matterId: number) => ({
  queryKey: [...MATTERS_QUERY_KEY, "detail", matterId],
  queryFn: () => apiRequest(`/matters/${matterId}`, { parse: parseMatter }),
  ...defaultQueryPolicy,
});
export const createMatter = (payload: MatterInput) =>
  apiRequest("/matters", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    parse: parseMatter,
  });
export const updateMatter = (matterId: number, payload: Partial<MatterInput>) =>
  apiRequest(`/matters/${matterId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    parse: parseMatter,
  });
