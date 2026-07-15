import { expectBooleanField, expectNumberField, expectRecord, expectStringField } from "@/shared/api/contracts";

export type ChecklistStatus = "pending" | "complete" | "not_applicable";
export interface ChecklistItem { id: number; matter_id: number; label: string; status: ChecklistStatus; is_custom: boolean; position: number; created_at: string; updated_at: string }
export const parseChecklistItem = (payload: unknown): ChecklistItem => {
  const r = expectRecord(payload, "ChecklistItem");
  const status = expectStringField(r, "status", "ChecklistItem");
  if (status !== "pending" && status !== "complete" && status !== "not_applicable") throw new Error("ChecklistItem: invalid status");
  return { id: expectNumberField(r, "id", "ChecklistItem"), matter_id: expectNumberField(r, "matter_id", "ChecklistItem"), label: expectStringField(r, "label", "ChecklistItem"), status, is_custom: expectBooleanField(r, "is_custom", "ChecklistItem"), position: expectNumberField(r, "position", "ChecklistItem"), created_at: expectStringField(r, "created_at", "ChecklistItem"), updated_at: expectStringField(r, "updated_at", "ChecklistItem") };
};
export const parseChecklist = (payload: unknown) => { const r = expectRecord(payload, "Checklist"); if (!Array.isArray(r.items)) throw new Error("Checklist: invalid items"); return { items: r.items.map(parseChecklistItem), total: expectNumberField(r, "total", "Checklist") }; };
