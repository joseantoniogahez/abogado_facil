import { defaultQueryPolicy } from "@/app/query-policy";
import { apiRequest } from "@/shared/api/http";

import { parseMatterTask, parseMatterTasks } from "./contracts";

export const matterTasksQueryKey = (matterId: number) => ["matter-tasks", matterId] as const;
export const matterTasksQueryOptions = (matterId: number) => ({
  queryKey: matterTasksQueryKey(matterId),
  queryFn: () => apiRequest(`/matters/${matterId}/tasks`, { parse: parseMatterTasks }),
  ...defaultQueryPolicy,
});
export const createMatterTask = (matterId: number, title: string, dueDate: string) =>
  apiRequest(`/matters/${matterId}/tasks`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, due_date: dueDate }),
    parse: parseMatterTask,
  });
export const updateMatterTask = (
  matterId: number,
  taskId: number,
  payload: { title?: string; due_date?: string; completed?: boolean },
) =>
  apiRequest(`/matters/${matterId}/tasks/${taskId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    parse: parseMatterTask,
  });
