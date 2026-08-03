import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { aiModelsQueryOptions } from "@/shared/ai-models/api";
import { ApiError, appendRequestIdDiagnostic, getApiErrorRequestId } from "@/shared/api/errors";
import { t } from "@/shared/i18n/ui-text";
import { PRIMARY_ACTION_CLASS_NAME, SECONDARY_ACTION_CLASS_NAME } from "@/shared/ui/actionStyles";

import {
  AI_CREDENTIALS_QUERY_KEY,
  AI_MODELS_QUERY_KEY,
  deleteAiCredential,
  readAiCredentials,
  saveAiCredential,
} from "./api";
import type { AiProvider } from "./contracts";

type OnboardingChoice = AiProvider | "demo";

export const AiSettingsPage = () => {
  const queryClient = useQueryClient();
  const credentials = useQuery({ queryKey: AI_CREDENTIALS_QUERY_KEY, queryFn: readAiCredentials });
  const hasCredential = credentials.data?.some(item => item.configured) ?? false;
  const models = useQuery({ ...aiModelsQueryOptions, enabled: credentials.isSuccess && hasCredential, retry: false });
  const [choice, setChoice] = useState<OnboardingChoice>("openai");
  const [keys, setKeys] = useState<Record<AiProvider, string>>({ openai: "", gemini: "" });
  const [message, setMessage] = useState<string | null>(null);
  const [actionError, setActionError] = useState<unknown>(null);
  const saveMutation = useMutation({
    retry: false,
    mutationFn: saveAiCredential,
    onMutate: () => { setMessage(null); setActionError(null); },
    onSuccess: async () => {
      setMessage(t("aiSettings.success.save"));
      setKeys({ openai: "", gemini: "" });
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: AI_CREDENTIALS_QUERY_KEY }),
        queryClient.invalidateQueries({ queryKey: AI_MODELS_QUERY_KEY }),
      ]);
    },
    onError: setActionError,
  });
  const deleteMutation = useMutation({
    retry: false,
    mutationFn: deleteAiCredential,
    onMutate: () => { setMessage(null); setActionError(null); },
    onSuccess: async () => {
      setMessage(t("aiSettings.success.delete"));
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: AI_CREDENTIALS_QUERY_KEY }),
        queryClient.invalidateQueries({ queryKey: AI_MODELS_QUERY_KEY }),
      ]);
    },
    onError: setActionError,
  });
  const errorMessage = actionError instanceof ApiError
    ? appendRequestIdDiagnostic(actionError.message, getApiErrorRequestId(actionError))
    : actionError ? t("aiSettings.error.generic") : null;
  const loadErrorMessage = credentials.error instanceof ApiError
    ? appendRequestIdDiagnostic(t("aiSettings.error.load"), getApiErrorRequestId(credentials.error))
    : t("aiSettings.error.load");
  const isActionPending = saveMutation.isPending || deleteMutation.isPending;
  const selectedProvider = choice === "demo" ? null : choice;
  const selectedConfigured = selectedProvider
    ? credentials.data?.some(item => item.provider === selectedProvider && item.configured) ?? false
    : false;
  const selectedCatalog = selectedProvider
    ? models.data?.find(item => item.provider === selectedProvider)
    : undefined;

  return (
    <main className="mx-auto max-w-4xl p-6 sm:p-10">
      <p className="mono-label text-(--app-subtle)">{t("aiSettings.badge")}</p>
      <h1 className="mt-3 text-4xl font-semibold">{t("aiSettings.title")}</h1>
      <p className="mt-3 max-w-2xl text-(--app-subtle)">{t("aiSettings.subtitle")}</p>
      <p className="mt-4 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900" role="note">{t("aiSettings.notice")}</p>

      {credentials.isPending ? <p className="mt-8">{t("aiSettings.loading")}</p> : null}
      {credentials.isError
        ? (
            <div className="mt-8">
              <p role="alert">{loadErrorMessage}</p>
              <button className={`${SECONDARY_ACTION_CLASS_NAME} mt-4`} onClick={() => void credentials.refetch()} type="button">{t("aiSettings.retry")}</button>
            </div>
          )
        : null}
      {message ? <p className="mt-6 rounded-2xl bg-emerald-50 p-4 text-sm text-emerald-800" role="status">{message}</p> : null}
      {errorMessage ? <p className="mt-6 rounded-2xl bg-red-50 p-4 text-sm text-red-700" role="alert">{errorMessage}</p> : null}

      {credentials.isSuccess
        ? (
            <section aria-labelledby="onboarding-title" className="mt-8 rounded-3xl border border-(--app-border) bg-(--app-surface) p-6">
              <p className="mono-label text-(--app-subtle)">{t("aiSettings.step", { step: 1 })}</p>
              <h2 className="mt-2 text-2xl font-semibold" id="onboarding-title">{t("aiSettings.choose.title")}</h2>
              <p className="mt-2 text-sm text-(--app-subtle)">{t("aiSettings.choose.body")}</p>
              <fieldset className="mt-5 grid gap-3 sm:grid-cols-3">
                <legend className="sr-only">{t("aiSettings.choose.title")}</legend>
                {(["openai", "gemini", "demo"] as const).map(option => (
                  <label className="flex cursor-pointer gap-3 rounded-2xl border border-(--app-border) p-4" key={option}>
                    <input checked={choice === option} name="ai-onboarding-choice" onChange={() => setChoice(option)} type="radio" />
                    <span>
                      <strong className="block">{t(`aiSettings.provider.${option}`)}</strong>
                      <span className="mt-1 block text-xs text-(--app-subtle)">{t(`aiSettings.provider.${option}.hint`)}</span>
                    </span>
                  </label>
                ))}
              </fieldset>

              {choice === "demo"
                ? (
                    <div className="mt-6 rounded-2xl border border-sky-200 bg-sky-50 p-5" role="status">
                      <p className="mono-label text-sky-800">{t("aiSettings.demo.badge")}</p>
                      <h3 className="mt-2 text-xl font-semibold">{t("aiSettings.demo.title")}</h3>
                      <p className="mt-2 text-sm text-sky-900">{t("aiSettings.demo.body")}</p>
                      <ol className="mt-4 list-decimal space-y-2 pl-5 text-sm">
                        <li>{t("aiSettings.demo.step.context")}</li>
                        <li>{t("aiSettings.demo.step.preview")}</li>
                        <li>{t("aiSettings.demo.step.review")}</li>
                      </ol>
                    </div>
                  )
                : (
                    <div className="mt-6 grid gap-6 lg:grid-cols-[1fr_1.2fr]">
                      <div>
                        <p className="mono-label text-(--app-subtle)">{t("aiSettings.step", { step: 2 })}</p>
                        <h3 className="mt-2 text-xl font-semibold">{t(`aiSettings.guide.${choice}.title`)}</h3>
                        <ol className="mt-3 list-decimal space-y-2 pl-5 text-sm text-(--app-subtle)">
                          <li>{t(`aiSettings.guide.${choice}.account`)}</li>
                          <li>{t(`aiSettings.guide.${choice}.key`)}</li>
                          <li>{t("aiSettings.guide.copy")}</li>
                        </ol>
                        <p className="mt-4 text-sm font-medium text-amber-800">{t("aiSettings.cost")}</p>
                      </div>
                      <div>
                        <p className="mono-label text-(--app-subtle)">{t("aiSettings.step", { step: 3 })}</p>
                        <h3 className="mt-2 text-xl font-semibold">{t("aiSettings.connect.title")}</h3>
                        <p className="mt-2 text-sm text-(--app-subtle)">{selectedConfigured ? t("aiSettings.replace.hint") : t("aiSettings.connect.hint")}</p>
                        <label className="mt-4 block text-sm font-medium" htmlFor={`${choice}-key`}>{t("aiSettings.key")}</label>
                        <input autoComplete="off" className="mt-2 w-full rounded-xl border border-(--app-border) px-3 py-3" id={`${choice}-key`} onChange={event => setKeys(previous => ({ ...previous, [choice]: event.target.value }))} type="password" value={keys[choice]} />
                        <div className="mt-4 flex flex-wrap gap-3">
                          <button className={PRIMARY_ACTION_CLASS_NAME} disabled={!keys[choice].trim() || isActionPending} onClick={() => saveMutation.mutate({ provider: choice, apiKey: keys[choice].trim() })} type="button">{selectedConfigured ? t("aiSettings.replace") : t("aiSettings.save")}</button>
                          <button className={SECONDARY_ACTION_CLASS_NAME} disabled={!selectedConfigured || isActionPending} onClick={() => deleteMutation.mutate(choice)} type="button">{t("aiSettings.delete")}</button>
                        </div>
                        {selectedConfigured
                          ? (
                              <div className="mt-5 rounded-xl border border-(--app-border) p-4">
                                <p className="font-medium">{t("aiSettings.verify.title")}</p>
                                {models.isPending ? <p className="mt-2 text-sm" role="status">{t("aiSettings.verify.loading")}</p> : null}
                                {models.isError ? <p className="mt-2 text-sm text-red-700" role="alert">{t("aiSettings.verify.error")}</p> : null}
                                {models.isError ? <button className={`${SECONDARY_ACTION_CLASS_NAME} mt-3`} onClick={() => void models.refetch()} type="button">{t("aiSettings.verify.retry")}</button> : null}
                                {models.isSuccess && selectedCatalog?.models.length ? <p className="mt-2 text-sm text-emerald-800" role="status">{t("aiSettings.verify.success", { count: selectedCatalog.models.length })}</p> : null}
                                {models.isSuccess && !selectedCatalog?.models.length ? <p className="mt-2 text-sm text-amber-800" role="alert">{t("aiSettings.verify.noModels")}</p> : null}
                              </div>
                            )
                          : null}
                      </div>
                    </div>
                  )}
            </section>
          )
        : null}
    </main>
  );
};
