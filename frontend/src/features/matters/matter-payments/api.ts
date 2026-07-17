import { defaultQueryPolicy } from "@/app/query-policy";
import { apiRequest } from "@/shared/api/http";

import { parseMatterBilling } from "./contracts";

export const matterPaymentsQueryKey = (matterId: number) => ["matter-payments", matterId] as const;
export const matterPaymentsQueryOptions = (matterId: number) => ({
  queryKey: matterPaymentsQueryKey(matterId),
  queryFn: () => apiRequest(`/matters/${matterId}/payments`, { parse: parseMatterBilling }),
  ...defaultQueryPolicy,
});
const write = (matterId: number, method: "PUT" | "POST", payload: object) =>
  apiRequest(`/matters/${matterId}/payments`, {
    method, headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload), parse: parseMatterBilling,
  });
export const updateMatterBilling = (matterId: number, agreedFee: string, notes: string) =>
  write(matterId, "PUT", { agreed_fee: agreedFee, notes: notes || null });
export const createMatterPayment = (
  matterId: number, payload: { amount: string; payment_type: "advance" | "partial"; paid_on: string; note: string | null },
) => write(matterId, "POST", payload);
