import { FormEvent, useEffect, useRef, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import {
  ApiError,
  appendRequestIdDiagnostic,
  getApiErrorRequestId,
  isUnauthorizedError,
} from "@/shared/api/errors";
import { SESSION_QUERY_KEY, updateCurrentUser, useSession } from "@/shared/auth/session";
import {
  getPasswordPolicyViolationKeys,
  isEmailValid,
  normalizeEmail,
} from "@/shared/auth/validation";
import { t } from "@/shared/i18n/ui-text";
import { CenteredMessage } from "@/shared/ui/CenteredMessage";
import { AccountFormField } from "@/shared/ui/AccountFormField";

interface ProfileFormState {
  firstName: string;
  middleName: string;
  lastName: string;
  displayName: string;
  email: string;
  firmName: string;
  currentPassword: string;
  newPassword: string;
}

const buildInitialProfileState = (user?: { first_name: string; middle_name: string | null; last_name: string; display_name: string; email: string; firm_name: string }): ProfileFormState => ({
  firstName: user?.first_name ?? "",
  middleName: user?.middle_name ?? "",
  lastName: user?.last_name ?? "",
  displayName: user?.display_name ?? "",
  email: user?.email ?? "",
  firmName: user?.firm_name ?? "",
  currentPassword: "",
  newPassword: "",
});

const getProfileValidationMessage = (formState: ProfileFormState, currentUser: { first_name: string; middle_name: string | null; last_name: string; display_name: string; email: string; firm_name: string }): string | null => {
  const normalizedEmail = normalizeEmail(formState.email);
  if (!formState.firstName.trim() || !formState.lastName.trim() || !formState.displayName.trim() || !formState.firmName.trim()) {
    return t("profile.validation.names.required");
  }
  if (!isEmailValid(normalizedEmail)) {
    return t("auth.validation.email.format");
  }
  if (formState.newPassword && !formState.currentPassword) {
    return t("profile.validation.currentPassword.required");
  }
  if (formState.currentPassword && !formState.newPassword) {
    return t("profile.validation.newPassword.required");
  }
  if (formState.newPassword && formState.currentPassword === formState.newPassword) {
    return t("profile.validation.newPassword.different");
  }

  const [firstPasswordViolation] = getPasswordPolicyViolationKeys(formState.newPassword, normalizedEmail);
  if (formState.newPassword && firstPasswordViolation) {
    return t(firstPasswordViolation);
  }

  const profileChanged = normalizedEmail !== normalizeEmail(currentUser.email) || formState.firstName.trim() !== currentUser.first_name || (formState.middleName.trim() || null) !== currentUser.middle_name || formState.lastName.trim() !== currentUser.last_name || formState.displayName.trim() !== currentUser.display_name || formState.firmName.trim() !== currentUser.firm_name;
  const passwordChanged = formState.newPassword.length > 0;
  if (!profileChanged && !passwordChanged) {
    return t("profile.validation.noChanges");
  }

  return null;
};

export const ProfilePage = () => {
  const { data: user } = useSession();
  const queryClient = useQueryClient();
  const [formState, setFormState] = useState<ProfileFormState>(() => buildInitialProfileState(user));
  const [clientError, setClientError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const lastSyncedUserId = useRef<number | null>(null);

  useEffect(() => {
    if (!user) {
      return;
    }

    if (lastSyncedUserId.current === user.id) {
      return;
    }

    lastSyncedUserId.current = user.id;
    setFormState(buildInitialProfileState(user));
  }, [user]);

  const updateMutation = useMutation({
    retry: false,
    mutationFn: updateCurrentUser,
    onSuccess: (updatedUser) => {
      queryClient.setQueryData(SESSION_QUERY_KEY, updatedUser);
      setClientError(null);
      setSuccessMessage(t("profile.success.body", { email: updatedUser.email }));
      setFormState(buildInitialProfileState(updatedUser));
    },
    onError: (error) => {
      if (isUnauthorizedError(error)) {
        queryClient.setQueryData(SESSION_QUERY_KEY, null);
      }
    },
  });

  if (!user) {
    return <CenteredMessage title={t("welcome.noSession.title")} body={t("welcome.noSession.body")} />;
  }

  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    updateMutation.reset();

    const validationMessage = getProfileValidationMessage(formState, user);
    if (validationMessage) {
      setClientError(validationMessage);
      setSuccessMessage(null);
      return;
    }

    const payload: {
      first_name?: string;
      middle_name?: string;
      last_name?: string;
      display_name?: string;
      email?: string;
      firm_name?: string;
      current_password?: string;
      new_password?: string;
    } = {};

    if (formState.firstName.trim() !== user.first_name) payload.first_name = formState.firstName.trim();
    if ((formState.middleName.trim() || null) !== user.middle_name) payload.middle_name = formState.middleName.trim();
    if (formState.lastName.trim() !== user.last_name) payload.last_name = formState.lastName.trim();
    if (formState.displayName.trim() !== user.display_name) payload.display_name = formState.displayName.trim();
    if (normalizeEmail(formState.email) !== normalizeEmail(user.email)) payload.email = normalizeEmail(formState.email);
    if (formState.firmName.trim() !== user.firm_name) payload.firm_name = formState.firmName.trim();
    if (formState.currentPassword) {
      payload.current_password = formState.currentPassword;
    }
    if (formState.newPassword) {
      payload.new_password = formState.newPassword;
    }

    setClientError(null);
    setSuccessMessage(null);
    updateMutation.mutate(payload);
  };

  const mutationError =
    clientError ??
    (updateMutation.error instanceof ApiError
      ? appendRequestIdDiagnostic(updateMutation.error.message, getApiErrorRequestId(updateMutation.error))
      : updateMutation.isError
        ? t("profile.error.generic")
        : null);

  return (
    <main className="flex min-h-screen items-center justify-center px-6 py-12">
      <section className="w-full max-w-2xl rounded-[var(--radius-card)] border border-[var(--app-border)] bg-[var(--app-surface)] p-8 shadow-[0_16px_40px_rgba(23,33,43,0.08)] sm:p-10">
        <p className="mono-label fade-rise text-[var(--app-subtle)]">{t("profile.badge")}</p>
        <h1 className="fade-rise-delay mt-4 text-3xl font-semibold tracking-tight sm:text-4xl">
          {t("profile.title")}
        </h1>
        <p className="fade-rise-delay-2 mt-4 text-sm text-[var(--app-subtle)]">{t("profile.subtitle")}</p>
        <p className="mt-2 text-sm font-medium text-[var(--app-ink)]">{t("profile.currentUser", { email: user.email })}</p>

        <form className="mt-8 space-y-4" onSubmit={submit}>
          <AccountFormField autoComplete="given-name" label={t("profile.fields.firstName")} name="firstName" onChange={(event) => setFormState((previous) => ({ ...previous, firstName: event.target.value }))} required value={formState.firstName} />
          <AccountFormField autoComplete="additional-name" label={t("profile.fields.middleName")} name="middleName" onChange={(event) => setFormState((previous) => ({ ...previous, middleName: event.target.value }))} value={formState.middleName} />
          <AccountFormField autoComplete="family-name" label={t("profile.fields.lastName")} name="lastName" onChange={(event) => setFormState((previous) => ({ ...previous, lastName: event.target.value }))} required value={formState.lastName} />
          <AccountFormField autoComplete="nickname" label={t("profile.fields.displayName")} name="displayName" onChange={(event) => setFormState((previous) => ({ ...previous, displayName: event.target.value }))} required value={formState.displayName} />
          <AccountFormField autoComplete="email" label={t("profile.fields.email")} name="email" onChange={(event) => setFormState((previous) => ({ ...previous, email: event.target.value }))} required type="email" value={formState.email} />
          <AccountFormField autoComplete="organization" label={t("profile.fields.firmName")} name="firmName" onChange={(event) => setFormState((previous) => ({ ...previous, firmName: event.target.value }))} required value={formState.firmName} />
          <AccountFormField autoComplete="current-password" label={t("profile.fields.currentPassword")} name="currentPassword" onChange={(event) => setFormState((previous) => ({ ...previous, currentPassword: event.target.value }))} type="password" value={formState.currentPassword} />
          <AccountFormField autoComplete="new-password" label={t("profile.fields.newPassword")} minLength={8} name="newPassword" onChange={(event) => setFormState((previous) => ({ ...previous, newPassword: event.target.value }))} type="password" value={formState.newPassword} />

          <ul className="space-y-1 rounded-2xl border border-[var(--app-border)] bg-[var(--app-bg)] px-4 py-3 text-sm text-[var(--app-subtle)]">
            <li>{t("auth.shared.email.hint")}</li>
            <li>{t("auth.shared.password.hint")}</li>
            <li>{t("profile.password.optional")}</li>
          </ul>

          {successMessage ? (
            <p
              className="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800"
              role="status"
            >
              {successMessage}
            </p>
          ) : null}

          {mutationError ? (
            <p
              className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
              role="alert"
            >
              {mutationError}
            </p>
          ) : null}

          <div className="flex flex-col gap-3 sm:flex-row">
            <button
              className="inline-flex flex-1 items-center justify-center rounded-full bg-[var(--app-ink)] px-5 py-3 text-sm font-semibold text-[var(--app-surface)] transition hover:bg-[var(--app-accent)] disabled:cursor-not-allowed disabled:opacity-70"
              disabled={updateMutation.isPending}
              type="submit"
            >
              {updateMutation.isPending ? t("profile.submit.pending") : t("profile.submit.default")}
            </button>
            <Link
              className="inline-flex flex-1 items-center justify-center rounded-full border border-[var(--app-border)] px-5 py-3 text-sm font-semibold text-[var(--app-ink)] transition hover:border-[var(--app-accent)] hover:text-[var(--app-accent)]"
              to="/dashboard"
            >
              {t("profile.actions.cancel")}
            </Link>
          </div>
        </form>
      </section>
    </main>
  );
};
