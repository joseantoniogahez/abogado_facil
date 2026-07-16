import { defaultQueryPolicy } from "@/app/query-policy";
import { apiRequest } from "@/shared/api/http";

import { type ChecklistStatus, parseChecklist, parseChecklistItem } from "./contracts";

export const matterChecklistQueryKey = (matterId: number) =>
  ["matter-checklist", matterId] as const;
export const matterChecklistQueryOptions = (matterId: number) => ({
  queryKey: matterChecklistQueryKey(matterId),
  queryFn: () => apiRequest(`/matters/${matterId}/checklist`, { parse: parseChecklist }),
  ...defaultQueryPolicy,
});
export const createChecklistItem = (matterId: number, label: string) =>
  apiRequest(`/matters/${matterId}/checklist`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ label }),
    parse: parseChecklistItem,
  });
export const updateChecklistItem = (matterId: number, itemId: number, status: ChecklistStatus) =>
  apiRequest(`/matters/${matterId}/checklist/${itemId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
    parse: parseChecklistItem,
  });
