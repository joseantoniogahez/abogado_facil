import { useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { ApiError, appendRequestIdDiagnostic, getApiErrorRequestId } from "@/shared/api/errors";
import { t } from "@/shared/i18n/ui-text";
import { SECONDARY_ACTION_CLASS_NAME } from "@/shared/ui/actionStyles";

import { DOCUMENT_TEMPLATES_QUERY_KEY, readDocumentTemplates } from "./api";
import type { DocumentTemplate } from "./contracts";
import { DocumentDraftGenerator } from "./DocumentDraftGenerator";

export const DocumentTemplatesPage = () => {
  const [selectedTemplate, setSelectedTemplate] = useState<DocumentTemplate | null>(null);
  const catalog = useQuery({
    queryKey: DOCUMENT_TEMPLATES_QUERY_KEY,
    queryFn: readDocumentTemplates,
  });
  const error = catalog.error instanceof ApiError
    ? appendRequestIdDiagnostic(t("documentTemplates.error"), getApiErrorRequestId(catalog.error))
    : t("documentTemplates.error");

  return (
    <main className="mx-auto max-w-5xl p-6 sm:p-10">
      <p className="mono-label text-(--app-subtle)">{t("documentTemplates.badge")}</p>
      <h1 className="mt-3 text-4xl font-semibold">{t("documentTemplates.title")}</h1>
      <p className="mt-3 max-w-3xl text-(--app-subtle)">{t("documentTemplates.subtitle")}</p>
      <p className="mt-4 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900" role="note">
        {t("documentTemplates.notice")}
      </p>
      {catalog.isPending ? <p className="mt-8">{t("documentTemplates.loading")}</p> : null}
      {catalog.isError
        ? (
            <div className="mt-8" role="alert">
              <p>{error}</p>
              <button
                className={`${SECONDARY_ACTION_CLASS_NAME} mt-4`}
                onClick={() => void catalog.refetch()}
                type="button"
              >
                {t("documentTemplates.retry")}
              </button>
            </div>
          )
        : null}
      {catalog.data
        ? (
            <section aria-label={t("documentTemplates.catalogLabel")} className="mt-8 grid gap-5 md:grid-cols-2">
              {catalog.data.items.map(template => (
                <article className="rounded-2xl border border-(--app-border) bg-(--app-surface) p-5" key={template.key}>
                  <h2 className="text-xl font-semibold">{template.name}</h2>
                  <p className="mt-2 text-(--app-subtle)">{template.description}</p>
                  <h3 className="mt-5 font-semibold">{t("documentTemplates.purpose")}</h3>
                  <p className="mt-1 text-sm">{template.purpose}</p>
                  <h3 className="mt-5 font-semibold">{t("documentTemplates.fields")}</h3>
                  <ul className="mt-2 space-y-2">
                    {template.fields.map(field => (
                      <li className="flex items-start justify-between gap-3 text-sm" key={field.key}>
                        <span>{field.label}</span>
                        <span className="rounded-full bg-(--app-muted) px-2 py-1 text-xs">
                          {field.required ? t("documentTemplates.required") : t("documentTemplates.optional")}
                        </span>
                      </li>
                    ))}
                  </ul>
                  <button
                    className={`${SECONDARY_ACTION_CLASS_NAME} mt-5`}
                    onClick={() => setSelectedTemplate(template)}
                    type="button"
                  >
                    {t("documentTemplates.use")}
                  </button>
                </article>
              ))}
            </section>
          )
        : null}
      {selectedTemplate ? <DocumentDraftGenerator key={selectedTemplate.key} template={selectedTemplate} /> : null}
    </main>
  );
};
