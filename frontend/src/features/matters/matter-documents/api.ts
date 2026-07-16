import { defaultQueryPolicy } from "@/app/query-policy";
import { apiBlobRequest, apiRequest } from "@/shared/api/http";

import { type DocumentType, parseMatterDocument, parseMatterDocumentList } from "./contracts";

export const matterDocumentsQueryKey = (matterId: number) =>
  ["matter-documents", matterId] as const;
export const matterDocumentsQueryOptions = (matterId: number) => ({
  queryKey: matterDocumentsQueryKey(matterId),
  queryFn: () => apiRequest(`/matters/${matterId}/documents`, { parse: parseMatterDocumentList }),
  ...defaultQueryPolicy,
});
export const uploadMatterDocument = (matterId: number, documentType: DocumentType, file: File) => {
  const body = new FormData();
  body.append("document_type", documentType);
  body.append("file", file);
  return apiRequest(`/matters/${matterId}/documents`, {
    method: "POST",
    body,
    parse: parseMatterDocument,
  });
};
export const deleteMatterDocument = (matterId: number, documentId: string) =>
  apiRequest(`/matters/${matterId}/documents/${documentId}`, { method: "DELETE" });
export const downloadMatterDocument = (matterId: number, documentId: string) =>
  apiBlobRequest(`/matters/${matterId}/documents/${documentId}/download`);
