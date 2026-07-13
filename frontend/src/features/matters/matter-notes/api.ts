import { defaultQueryPolicy } from "@/app/query-policy";
import { apiRequest } from "@/shared/api/http";
import { parseMatterNote, parseMatterNoteList } from "./contracts";
export const matterNotesQueryKey = (matterId: number) => ["matter-notes", matterId] as const;
export const matterNotesQueryOptions = (matterId: number) => ({ queryKey: matterNotesQueryKey(matterId), queryFn: () => apiRequest(`/matters/${matterId}/notes`, { parse: parseMatterNoteList }), ...defaultQueryPolicy });
export const createMatterNote = (matterId: number, content: string) => apiRequest(`/matters/${matterId}/notes`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ content }), parse: parseMatterNote });
export const updateMatterNote = (matterId: number, noteId: number, payload: { content?: string; is_relevant?: boolean }) => apiRequest(`/matters/${matterId}/notes/${noteId}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload), parse: parseMatterNote });
export const deleteMatterNote = (matterId: number, noteId: number) => apiRequest(`/matters/${matterId}/notes/${noteId}`, { method: "DELETE" });
