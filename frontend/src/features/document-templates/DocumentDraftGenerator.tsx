import { useMutation, useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { aiModelsQueryOptions } from "@/shared/ai-models/api";
import { t } from "@/shared/i18n/ui-text";
import { ACCENT_ACTION_CLASS_NAME, SECONDARY_ACTION_CLASS_NAME } from "@/shared/ui/actionStyles";
import { AiGeneratedContentNotice } from "@/shared/ui/AiGeneratedContentNotice";

import { generateDocumentDraft, previewDocumentDraft } from "./api";
import type { DocumentTemplate, DraftProvider } from "./contracts";

export const DocumentDraftGenerator = ({ template }: { template: DocumentTemplate }) => {
  const catalog = useQuery(aiModelsQueryOptions);
  const [fields, setFields] = useState<Record<string, string>>({});
  const [provider, setProvider] = useState<DraftProvider>("openai");
  const [model, setModel] = useState("");
  const [draft, setDraft] = useState<string | null>(null);
  const [reviewConfirmed, setReviewConfirmed] = useState(false);
  const [actionStatus, setActionStatus] = useState<"copied" | "exported" | "copyError" | null>(null);
  const first = catalog.data?.find(entry => entry.models.length > 0);
  const activeProvider = model ? provider : first?.provider ?? provider;
  const selectedModels = catalog.data?.find(entry => entry.provider === activeProvider)?.models ?? [];
  const activeModel = model ? model : (selectedModels[0]?.id ?? "");
  const input = { template_key: template.key, fields, provider: activeProvider, model: activeModel };
  const catalogReady = catalog.isSuccess && selectedModels.length > 0;
  const preview = useMutation({ mutationFn: () => previewDocumentDraft(input) });
  const generate = useMutation({
    mutationFn: () => {
      if (!preview.data) throw new Error("Document draft preview is required");
      return generateDocumentDraft(input, preview.data.confirmation_token);
    },
    onSuccess: (result) => {
      setDraft(result.content);
      setReviewConfirmed(false);
      setActionStatus(null);
    },
  });
  const resetDraft = () => {
    setDraft(null);
    setReviewConfirmed(false);
    setActionStatus(null);
  };
  const updateField = (key: string, value: string) => {
    setFields(previous => ({ ...previous, [key]: value }));
    preview.reset();
    resetDraft();
  };
  const requiredComplete = template.fields
    .filter(field => field.required)
    .every(field => fields[field.key]?.trim());
  const reviewedDraftAvailable = reviewConfirmed && Boolean(draft?.trim());
  const copyDraft = async () => {
    if (!reviewedDraftAvailable || draft === null) return;
    try {
      await navigator.clipboard.writeText(draft);
      setActionStatus("copied");
    }
    catch {
      setActionStatus("copyError");
    }
  };
  const exportDraft = () => {
    if (!reviewedDraftAvailable || draft === null) return;
    const exportContent = `${t("documentDraft.exportWarning")}\n\n${draft}`;
    const url = URL.createObjectURL(new Blob([exportContent], { type: "text/plain;charset=utf-8" }));
    const link = document.createElement("a");
    link.href = url;
    link.download = `borrador-${template.key}.txt`;
    link.click();
    URL.revokeObjectURL(url);
    setActionStatus("exported");
  };

  return (
    <section aria-labelledby="document-draft-title" className="mt-10 rounded-2xl border border-(--app-border) p-5">
      <h2 className="text-2xl font-semibold" id="document-draft-title">{t("documentDraft.title")}</h2>
      <p className="mt-2 text-(--app-subtle)">{template.name}</p>
      <form className="mt-6 grid gap-4" onSubmit={event => event.preventDefault()}>
        {template.fields.map(field => (
          <label key={field.key}>
            {field.label}
            {field.required ? ` (${t("documentTemplates.required")})` : ` (${t("documentTemplates.optional")})`}
            {field.field_type === "long_text"
              ? (
                  <textarea
                    className="mt-1 min-h-28 w-full rounded-xl border p-3"
                    maxLength={20000}
                    onChange={event => updateField(field.key, event.target.value)}
                    required={field.required}
                    value={fields[field.key] ?? ""}
                  />
                )
              : (
                  <input
                    className="mt-1 w-full rounded-xl border p-3"
                    maxLength={field.field_type === "text" ? 500 : undefined}
                    onChange={event => updateField(field.key, event.target.value)}
                    required={field.required}
                    type={field.field_type === "date" ? "date" : "text"}
                    value={fields[field.key] ?? ""}
                  />
                )}
          </label>
        ))}
        <div className="grid gap-3 sm:grid-cols-2">
          <label>
            {t("documentDraft.provider")}
            <select
              className="mt-1 w-full rounded-xl border p-3"
              onChange={(event) => {
                const next = event.target.value as DraftProvider;
                setProvider(next);
                setModel(catalog.data?.find(entry => entry.provider === next)?.models[0]?.id ?? "");
                preview.reset();
                resetDraft();
              }}
              value={activeProvider}
            >
              {(catalog.data ?? []).filter(entry => entry.models.length).map(entry => (
                <option key={entry.provider} value={entry.provider}>{entry.provider === "openai" ? "OpenAI" : "Gemini"}</option>
              ))}
            </select>
          </label>
          <label>
            {t("documentDraft.model")}
            <select
              className="mt-1 w-full rounded-xl border p-3"
              onChange={(event) => {
                setModel(event.target.value);
                preview.reset();
                resetDraft();
              }}
              value={activeModel}
            >
              {selectedModels.map(option => (
                <option key={option.id} value={option.id}>{option.label}</option>
              ))}
            </select>
          </label>
        </div>
        <button
          className={`${SECONDARY_ACTION_CLASS_NAME} w-fit`}
          disabled={!catalogReady || !requiredComplete || preview.isPending}
          onClick={() => preview.mutate()}
          type="button"
        >
          {t("documentDraft.preview")}
        </button>
        {catalog.isPending ? <p role="status">{t("ai.models.loading")}</p> : null}
        {catalog.isError ? <p role="alert">{t("ai.models.error")}</p> : null}
        {catalog.isSuccess && !catalogReady ? <p role="status">{t("ai.models.empty")}</p> : null}
      </form>
      {preview.data
        ? (
            <aside aria-label={t("documentDraft.previewTitle")} className="mt-5 rounded-xl border p-4">
              <h3 className="font-semibold">{t("documentDraft.previewTitle")}</h3>
              <p>{preview.data.included_fields.join(", ")}</p>
              <p>{preview.data.cost_notice}</p>
              <button
                className={`${ACCENT_ACTION_CLASS_NAME} mt-3`}
                disabled={generate.isPending}
                onClick={() => generate.mutate()}
                type="button"
              >
                {generate.isPending ? t("documentDraft.generating") : t("documentDraft.generate")}
              </button>
            </aside>
          )
        : null}
      {preview.isError || generate.isError ? <p className="mt-4" role="alert">{t("documentDraft.error")}</p> : null}
      {draft !== null
        ? (
            <section aria-describedby="document-draft-notice" className="mt-6 grid gap-4">
              <AiGeneratedContentNotice id="document-draft-notice" kind="draft" />
              <label>
                {t("documentDraft.content")}
                <textarea
                  aria-describedby="document-draft-notice"
                  className="mt-1 min-h-96 w-full rounded-xl border p-3 font-mono text-sm"
                  onChange={(event) => {
                    setDraft(event.target.value);
                    setReviewConfirmed(false);
                    setActionStatus(null);
                  }}
                  value={draft}
                />
              </label>
              <p className="text-sm text-(--app-subtle)">{t("documentDraft.noAutomaticAction")}</p>
              <label className="flex items-start gap-2">
                <input
                  checked={reviewConfirmed}
                  className="mt-1"
                  onChange={(event) => {
                    setReviewConfirmed(event.target.checked);
                    setActionStatus(null);
                  }}
                  type="checkbox"
                />
                <span>{t("documentDraft.reviewConfirmation")}</span>
              </label>
              <div aria-describedby="document-draft-notice" className="flex flex-wrap gap-3">
                <button
                  className={SECONDARY_ACTION_CLASS_NAME}
                  disabled={!reviewedDraftAvailable}
                  onClick={() => void copyDraft()}
                  type="button"
                >
                  {t("documentDraft.copy")}
                </button>
                <button
                  className={SECONDARY_ACTION_CLASS_NAME}
                  disabled={!reviewedDraftAvailable}
                  onClick={exportDraft}
                  type="button"
                >
                  {t("documentDraft.export")}
                </button>
              </div>
              {actionStatus === "copyError" ? <p role="alert">{t("documentDraft.copyError")}</p> : null}
              {actionStatus === "copied" || actionStatus === "exported"
                ? (
                    <p aria-live="polite" role="status">
                      {t(actionStatus === "copied" ? "documentDraft.copied" : "documentDraft.exported")}
                    </p>
                  )
                : null}
            </section>
          )
        : null}
    </section>
  );
};
