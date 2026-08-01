import { apiRequest } from "@/shared/api/http";

import {
  type DocumentDraftInput,
  parseDocumentDraft,
  parseDocumentDraftPreview,
  parseDocumentTemplateCatalog,
} from "./contracts";

export const DOCUMENT_TEMPLATES_QUERY_KEY = ["document-templates"] as const;

export const readDocumentTemplates = () =>
  apiRequest("/document-templates", { parse: parseDocumentTemplateCatalog });

export const previewDocumentDraft = (input: DocumentDraftInput) =>
  apiRequest("/document-templates/drafts/preview", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
    parse: parseDocumentDraftPreview,
  });

export const generateDocumentDraft = (input: DocumentDraftInput, confirmationToken: string) =>
  apiRequest("/document-templates/drafts", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...input, confirmation_token: confirmationToken }),
    parse: parseDocumentDraft,
  });
