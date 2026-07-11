import { ApiContractError, expectNumberField, expectRecord, expectStringField } from "@/shared/api/contracts";

export interface DashboardSummary {
  firm_id: number;
  firm_name: string;
  clients: { value: number; available: boolean };
  active_matters: { value: number; available: boolean };
  pending_tasks: { value: number; available: boolean };
  upcoming_tasks: unknown[];
  ai_status: "not_available" | "not_configured" | "configured" | "error";
  actions: { id: string; available: boolean }[];
}

const parseMetric = (value: unknown, context: string) => {
  const record = expectRecord(value, context);
  if (typeof record.available !== "boolean") throw new ApiContractError(`${context}: invalid availability`);
  return { value: expectNumberField(record, "value", context), available: record.available };
};

export const parseDashboardSummary = (payload: unknown): DashboardSummary => {
  const record = expectRecord(payload, "DashboardSummary");
  const aiStatus = expectStringField(record, "ai_status", "DashboardSummary");
  if (!["not_available", "not_configured", "configured", "error"].includes(aiStatus)) {
    throw new ApiContractError("DashboardSummary: invalid ai_status");
  }
  if (!Array.isArray(record.upcoming_tasks) || !Array.isArray(record.actions)) {
    throw new ApiContractError("DashboardSummary: invalid collections");
  }
  return {
    firm_id: expectNumberField(record, "firm_id", "DashboardSummary"),
    firm_name: expectStringField(record, "firm_name", "DashboardSummary", { minLength: 1 }),
    clients: parseMetric(record.clients, "DashboardSummary.clients"),
    active_matters: parseMetric(record.active_matters, "DashboardSummary.active_matters"),
    pending_tasks: parseMetric(record.pending_tasks, "DashboardSummary.pending_tasks"),
    upcoming_tasks: record.upcoming_tasks,
    ai_status: aiStatus as DashboardSummary["ai_status"],
    actions: record.actions.map((item) => {
      const action = expectRecord(item, "DashboardAction");
      if (typeof action.available !== "boolean") throw new ApiContractError("DashboardAction: invalid availability");
      return { id: expectStringField(action, "id", "DashboardAction"), available: action.available };
    }),
  };
};
