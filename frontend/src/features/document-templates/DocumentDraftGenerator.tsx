import { useMutation } from "@tanstack/react-query";
import { useState } from "react";

import { t } from "@/shared/i18n/ui-text";
import { ACCENT_ACTION_CLASS_NAME, SECONDARY_ACTION_CLASS_NAME } from "@/shared/ui/actionStyles";
import { AiGeneratedContentNotice } from "@/shared/ui/AiGeneratedContentNotice";

import { generateDocumentDraft, previewDocumentDraft } from "./api";
import type { DocumentTemplate, DraftProvider } from "./contracts";

const MODEL_OPTIONS = {
  openai: [
    { value: "gpt-4.1-mini", label: "GPT-4.1 mini" },
    { value: "gpt-4.1", label: "GPT-4.1" },
  ],
  gemini: [
    { value: "gemini-3.5-flash-lite", label: "Gemini 3.5 Flash-Lite" },
    { value: "gemini-2.5-flash", label: "Gemini 2.5 Flash" },
  ],
} as const;

export const DocumentDraftGenerator = ({ template }: { template: DocumentTemplate }) => {
  const [fields, setFields] = useState<Record<string, string>>({});
  const [provider, setProvider] = useState<DraftProvider>("openai");
  const [model, setModel] = useState(MODEL_OPTIONS.openai[0].value);
  const [draft, setDraft] = useState<string | null>(null);
  const input = { template_key: template.key, fields, provider, model };
  const preview = useMutation({ mutationFn: () => previewDocumentDraft(input) });
  const generate = useMutation({
    mutationFn: () => {
      if (!preview.data) throw new Error("Document draft preview is required");
      return generateDocumentDraft(input, preview.data.confirmation_token);
    },
    onSuccess: result => setDraft(result.content),
  });
  const updateField = (key: string, value: string) => {
    setFields(previous => ({ ...previous, [key]: value }));
    preview.reset();
    setDraft(null);
  };
  const requiredComplete = template.fields
    .filter(field => field.required)
    .every(field => fields[field.key]?.trim());

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
                setModel(MODEL_OPTIONS[next][0].value);
                preview.reset();
                setDraft(null);
              }}
              value={provider}
            >
              <option value="openai">OpenAI</option>
              <option value="gemini">Gemini</option>
            </select>
          </label>
          <label>
            {t("documentDraft.model")}
            <select
              className="mt-1 w-full rounded-xl border p-3"
              onChange={(event) => {
                setModel(event.target.value);
                preview.reset();
                setDraft(null);
              }}
              value={model}
            >
              {MODEL_OPTIONS[provider].map(option => (
                <option key={option.value} value={option.value}>{option.label}</option>
              ))}
            </select>
          </label>
        </div>
        <button
          className={`${SECONDARY_ACTION_CLASS_NAME} w-fit`}
          disabled={!requiredComplete || preview.isPending}
          onClick={() => preview.mutate()}
          type="button"
        >
          {t("documentDraft.preview")}
        </button>
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
                  onChange={event => setDraft(event.target.value)}
                  value={draft}
                />
              </label>
              <p className="text-sm text-(--app-subtle)">{t("documentDraft.noAutomaticAction")}</p>
            </section>
          )
        : null}
    </section>
  );
};
