import { expectNumberField, expectRecord, expectStringField } from "@/shared/api/contracts";

export type MatterStatus = "active" | "pending" | "closed";
export interface MatterRecord { id: number; client_id: number; title: string; matter_type: string; status: MatterStatus; counterparty: string | null; description: string | null; next_action: string | null; next_action_date: string | null; created_at: string; updated_at: string }
const optional = (r: Record<string, unknown>, key: string) => r[key] === null ? null : expectStringField(r, key, "Matter");
export const parseMatter = (payload: unknown): MatterRecord => { const r = expectRecord(payload, "Matter"); const status = expectStringField(r, "status", "Matter"); if (!["active", "pending", "closed"].includes(status)) throw new Error("Matter: invalid status"); return { id: expectNumberField(r, "id", "Matter"), client_id: expectNumberField(r, "client_id", "Matter"), title: expectStringField(r, "title", "Matter"), matter_type: expectStringField(r, "matter_type", "Matter"), status: status as MatterStatus, counterparty: optional(r, "counterparty"), description: optional(r, "description"), next_action: optional(r, "next_action"), next_action_date: optional(r, "next_action_date"), created_at: expectStringField(r, "created_at", "Matter"), updated_at: expectStringField(r, "updated_at", "Matter") }; };
export const parseMatterList = (payload: unknown) => { const r = expectRecord(payload, "MatterList"); if (!Array.isArray(r.items)) throw new Error("MatterList: invalid items"); return { items: r.items.map(parseMatter), total: expectNumberField(r, "total", "MatterList"), limit: expectNumberField(r, "limit", "MatterList"), offset: expectNumberField(r, "offset", "MatterList") }; };
export interface MatterInput { client_id: number; title: string; matter_type: string; status: MatterStatus; counterparty?: string | null; description?: string | null; next_action?: string | null; next_action_date?: string | null }
export interface MatterTypeOption { value: string }
export const parseMatterTypes = (payload: unknown): MatterTypeOption[] => {
  if (!Array.isArray(payload)) throw new Error("MatterTypes: invalid payload");
  return payload.map((item) => {
    const option = expectRecord(item, "MatterType");
    return { value: expectStringField(option, "value", "MatterType", { minLength: 1 }) };
  });
};
