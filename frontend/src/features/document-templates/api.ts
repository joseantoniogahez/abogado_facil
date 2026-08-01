import { apiRequest } from "@/shared/api/http";

import { parseDocumentTemplateCatalog } from "./contracts";

export const DOCUMENT_TEMPLATES_QUERY_KEY = ["document-templates"] as const;

export const readDocumentTemplates = () =>
  apiRequest("/document-templates", { parse: parseDocumentTemplateCatalog });
