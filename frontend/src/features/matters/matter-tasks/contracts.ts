import { expectBooleanField, expectNumberField, expectRecord, expectStringField } from "@/shared/api/contracts";

export interface MatterTask {
  id: number;
  matter_id: number;
  title: string;
  due_date: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

export const parseMatterTask = (payload: unknown): MatterTask => {
  const record = expectRecord(payload, "MatterTask");
  return {
    id: expectNumberField(record, "id", "MatterTask"),
    matter_id: expectNumberField(record, "matter_id", "MatterTask"),
    title: expectStringField(record, "title", "MatterTask", { minLength: 1 }),
    due_date: expectStringField(record, "due_date", "MatterTask", { minLength: 10 }),
    completed: expectBooleanField(record, "completed", "MatterTask"),
    created_at: expectStringField(record, "created_at", "MatterTask"),
    updated_at: expectStringField(record, "updated_at", "MatterTask"),
  };
};

export const parseMatterTasks = (payload: unknown) => {
  const record = expectRecord(payload, "MatterTaskList");
  if (!Array.isArray(record.items)) throw new Error("MatterTaskList: invalid items");
  return {
    items: record.items.map(parseMatterTask),
    total: expectNumberField(record, "total", "MatterTaskList"),
  };
};
