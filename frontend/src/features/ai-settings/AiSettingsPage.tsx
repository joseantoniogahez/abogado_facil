import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

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

const PROVIDERS: readonly AiProvider[] = ["openai", "gemini"];

export const AiSettingsPage = () => {
  const queryClient = useQueryClient();
  const credentials = useQuery({ queryKey: AI_CREDENTIALS_QUERY_KEY, queryFn: readAiCredentials });
  const [keys, setKeys] = useState<Record<AiProvider, string>>({ openai: "", gemini: "" });
  const [message, setMessage] = useState<string | null>(null);
  const [actionError, setActionError] = useState<unknown>(null);
  const saveMutation = useMutation({
    retry: false,
    mutationFn: saveAiCredential,
    onMutate: () => {
      setMessage(null);
      setActionError(null);
    },
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
    onMutate: () => {
      setMessage(null);
      setActionError(null);
    },
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

  return (
    <main className="mx-auto max-w-4xl p-6 sm:p-10">
      <p className="mono-label text-(--app-subtle)">{t("aiSettings.badge")}</p>
      <h1 className="mt-3 text-4xl font-semibold">{t("aiSettings.title")}</h1>
      <p className="mt-3 max-w-2xl text-(--app-subtle)">{t("aiSettings.subtitle")}</p>
      <p className="mt-4 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900" role="note">
        {t("aiSettings.notice")}
      </p>
      {credentials.isPending ? <p className="mt-8">{t("aiSettings.loading")}</p> : null}
      {credentials.isError
        ? (
            <div className="mt-8">
              <p role="alert">{loadErrorMessage}</p>
              <button
                className={`${SECONDARY_ACTION_CLASS_NAME} mt-4`}
                onClick={() => void credentials.refetch()}
                type="button"
              >
                {t("aiSettings.retry")}
              </button>
            </div>
          )
        : null}
      {message ? <p className="mt-6 rounded-2xl bg-emerald-50 p-4 text-sm text-emerald-800" role="status">{message}</p> : null}
      {errorMessage ? <p className="mt-6 rounded-2xl bg-red-50 p-4 text-sm text-red-700" role="alert">{errorMessage}</p> : null}
      {credentials.isSuccess
        ? (
            <section aria-label={t("aiSettings.providers")} className="mt-8 grid gap-5 md:grid-cols-2">
              {PROVIDERS.map((provider) => {
                const configured = credentials.data.some(item => item.provider === provider && item.configured);
                return (
                  <article className="rounded-2xl border border-(--app-border) bg-(--app-surface) p-5" key={provider}>
                    <h2 className="text-xl font-semibold">{t(`aiSettings.provider.${provider}`)}</h2>
                    <p className="mt-2 text-sm text-(--app-subtle)">{configured ? t("aiSettings.configured") : t("aiSettings.notConfigured")}</p>
                    <label className="mt-5 block text-sm font-medium" htmlFor={`${provider}-key`}>{t("aiSettings.key")}</label>
                    <input className="mt-2 w-full rounded-xl border border-(--app-border) px-3 py-3" id={`${provider}-key`} onChange={event => setKeys(previous => ({ ...previous, [provider]: event.target.value }))} type="password" value={keys[provider]} />
                    <div className="mt-4 flex flex-wrap gap-3">
                      <button className={PRIMARY_ACTION_CLASS_NAME} disabled={!keys[provider].trim() || isActionPending} onClick={() => saveMutation.mutate({ provider, apiKey: keys[provider].trim() })} type="button">{t("aiSettings.save")}</button>
                      <button className={SECONDARY_ACTION_CLASS_NAME} disabled={!configured || isActionPending} onClick={() => deleteMutation.mutate(provider)} type="button">{t("aiSettings.delete")}</button>
                    </div>
                  </article>
                );
              })}
            </section>
          )
        : null}
    </main>
  );
};
