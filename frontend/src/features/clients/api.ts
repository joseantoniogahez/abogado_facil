import { defaultQueryPolicy } from "@/app/query-policy";
import { type ClientInput, parseClient, parseClientList } from "@/features/clients/contracts";
import { apiRequest } from "@/shared/api/http";

export const CLIENTS_QUERY_KEY = ["clients"] as const;
export const clientsQueryOptions = (search: string) => ({
  queryKey: [...CLIENTS_QUERY_KEY, "list", search] as const,
  queryFn: () =>
    apiRequest(`/clients${search ? `?search=${encodeURIComponent(search)}` : ""}`, {
      parse: parseClientList,
    }),
  ...defaultQueryPolicy,
});
export const clientQueryOptions = (clientId: number) => ({
  queryKey: [...CLIENTS_QUERY_KEY, "detail", clientId] as const,
  queryFn: () => apiRequest(`/clients/${clientId}`, { parse: parseClient }),
  ...defaultQueryPolicy,
});
export const createClient = (payload: ClientInput) =>
  apiRequest("/clients", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    parse: parseClient,
  });
export const updateClient = (clientId: number, payload: ClientInput) =>
  apiRequest(`/clients/${clientId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    parse: parseClient,
  });
