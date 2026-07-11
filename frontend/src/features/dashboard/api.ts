import { defaultQueryPolicy } from "@/app/query-policy";
import { apiRequest } from "@/shared/api/http";
import { parseDashboardSummary } from "@/features/dashboard/contracts";

export const DASHBOARD_QUERY_KEY = ["dashboard", "summary"] as const;
export const dashboardQueryOptions = () => ({
  queryKey: DASHBOARD_QUERY_KEY,
  queryFn: () => apiRequest("/dashboard", { parse: parseDashboardSummary }),
  ...defaultQueryPolicy,
});
