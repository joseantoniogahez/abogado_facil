import { useMutation } from "@tanstack/react-query";
import { type SyntheticEvent, useState } from "react";
import { Link, Navigate } from "react-router";

import { ApiError, appendRequestIdDiagnostic, getApiErrorRequestId } from "@/shared/api/errors";
import { type AuthenticatedUser, registerUser, useSession } from "@/shared/auth/session";
import {
  composeDisplayName,
  getPasswordPolicyViolationKeys,
  isEmailValid,
  normalizeEmail,
} from "@/shared/auth/validation";
import { t } from "@/shared/i18n/ui-text";
import { AccountFormField } from "@/shared/ui/AccountFormField";
import { INLINE_ACTION_CLASS_NAME, PRIMARY_ACTION_CLASS_NAME } from "@/shared/ui/actionStyles";
import { CenteredMessage } from "@/shared/ui/CenteredMessage";

interface RegisterFormState {
  firstName: string;
  middleName: string;
  lastName: string;
  displayName: string;
  email: string;
  firmName: string;
  password: string;
}

const INITIAL_FORM_STATE: RegisterFormState = {
  firstName: "",
  middleName: "",
  lastName: "",
  displayName: "",
  email: "",
  firmName: "",
  password: "",
};

const getRegisterValidationMessage = (formState: RegisterFormState): string | null => {
  const normalizedEmail = normalizeEmail(formState.email);
  if (!formState.firstName.trim() || !formState.lastName.trim()) {
    return t("auth.validation.legalName.required");
  }
  if (!formState.displayName.trim()) {
    return t("auth.validation.displayName.required");
  }
  if (!isEmailValid(normalizedEmail)) {
    return t("auth.validation.email.format");
  }

  const [firstPasswordViolation] = getPasswordPolicyViolationKeys(
    formState.password,
    normalizedEmail,
  );
  return firstPasswordViolation ? t(firstPasswordViolation) : null;
};

export const RegisterPage = () => {
  const [formState, setFormState] = useState<RegisterFormState>(INITIAL_FORM_STATE);
  const [displayNameCustomized, setDisplayNameCustomized] = useState(false);
  const [clientError, setClientError] = useState<string | null>(null);
  const [registeredUser, setRegisteredUser] = useState<AuthenticatedUser | null>(null);
  const session = useSession();

  const registerMutation = useMutation({
    retry: false,
    mutationFn: registerUser,
    onSuccess: (user) => {
      setRegisteredUser(user);
      setClientError(null);
      setFormState(INITIAL_FORM_STATE);
      setDisplayNameCustomized(false);
    },
  });

  if (session.isPending) {
    return <CenteredMessage title={t("auth.login.validating.title")} />;
  }

  if (session.data) {
    return <Navigate replace to="/dashboard" />;
  }

  const submit = (event: SyntheticEvent<HTMLFormElement>) => {
    event.preventDefault();
    registerMutation.reset();
    setRegisteredUser(null);

    const validationMessage = getRegisterValidationMessage(formState);
    if (validationMessage) {
      setClientError(validationMessage);
      return;
    }

    setClientError(null);
    registerMutation.mutate({
      first_name: formState.firstName.trim(),
      ...(formState.middleName.trim() ? { middle_name: formState.middleName.trim() } : {}),
      last_name: formState.lastName.trim(),
      display_name: formState.displayName.trim(),
      email: normalizeEmail(formState.email),
      ...(formState.firmName.trim() ? { firm_name: formState.firmName.trim() } : {}),
      password: formState.password,
    });
  };

  const updateNamePart = (field: "firstName" | "middleName" | "lastName", value: string) => {
    setFormState((previous) => {
      const next = { ...previous, [field]: value };
      if (!displayNameCustomized) {
        next.displayName = composeDisplayName(next.firstName, next.middleName, next.lastName);
      }
      return next;
    });
  };

  const mutationError
    = clientError
      ?? (registerMutation.error instanceof ApiError
        ? appendRequestIdDiagnostic(
            registerMutation.error.message,
            getApiErrorRequestId(registerMutation.error),
          )
        : registerMutation.isError
          ? t("auth.register.error.generic")
          : null);

  if (registeredUser) {
    return (
      <main className="flex min-h-screen items-center justify-center px-6 py-12">
        <section className="w-full max-w-md rounded-(--radius-card) border border-(--app-border) bg-(--app-surface) p-8 shadow-[0_16px_40px_rgba(23,33,43,0.08)] sm:p-10">
          <p className="mono-label fade-rise text-(--app-subtle)">
            {t("auth.register.badge")}
          </p>
          <h1 className="fade-rise-delay mt-4 text-3xl font-semibold tracking-tight sm:text-4xl">
            {t("auth.register.success.title")}
          </h1>
          <p className="fade-rise-delay-2 mt-4 text-sm text-(--app-subtle)">
            {t("auth.register.success.body", { email: registeredUser.email })}
          </p>
          <div className="mt-8">
            <Link className={`${PRIMARY_ACTION_CLASS_NAME} w-full`} to="/login">
              {t("auth.register.footer.signIn")}
            </Link>
          </div>
        </section>
      </main>
    );
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-6 py-12">
      <section className="w-full max-w-md rounded-(--radius-card) border border-(--app-border) bg-(--app-surface) p-8 shadow-[0_16px_40px_rgba(23,33,43,0.08)] sm:p-10">
        <p className="mono-label fade-rise text-(--app-subtle)">{t("auth.register.badge")}</p>
        <h1 className="fade-rise-delay mt-4 text-3xl font-semibold tracking-tight sm:text-4xl">
          {t("auth.register.title")}
        </h1>
        <p className="fade-rise-delay-2 mt-4 text-sm text-(--app-subtle)">
          {t("auth.register.subtitle")}
        </p>

        <form className="mt-8 space-y-4" onSubmit={submit}>
          <AccountFormField
            autoComplete="given-name"
            label={t("auth.register.fields.firstName")}
            name="firstName"
            onChange={event => updateNamePart("firstName", event.target.value)}
            required
            value={formState.firstName}
          />
          <AccountFormField
            autoComplete="additional-name"
            label={t("auth.register.fields.middleName")}
            name="middleName"
            onChange={event => updateNamePart("middleName", event.target.value)}
            value={formState.middleName}
          />
          <AccountFormField
            autoComplete="family-name"
            label={t("auth.register.fields.lastName")}
            name="lastName"
            onChange={event => updateNamePart("lastName", event.target.value)}
            required
            value={formState.lastName}
          />
          <AccountFormField
            autoComplete="nickname"
            label={t("auth.register.fields.displayName")}
            name="displayName"
            onChange={(event) => {
              setDisplayNameCustomized(true);
              setFormState(previous => ({ ...previous, displayName: event.target.value }));
            }}
            required
            value={formState.displayName}
          />
          <AccountFormField
            autoComplete="email"
            label={t("auth.login.fields.email")}
            name="email"
            onChange={event =>
              setFormState(previous => ({ ...previous, email: event.target.value }))}
            required
            type="email"
            value={formState.email}
          />
          <AccountFormField
            autoComplete="organization"
            label={t("auth.register.fields.firmName")}
            name="firmName"
            onChange={event =>
              setFormState(previous => ({ ...previous, firmName: event.target.value }))}
            value={formState.firmName}
          />
          <AccountFormField
            autoComplete="new-password"
            label={t("auth.login.fields.password")}
            minLength={8}
            name="password"
            onChange={event =>
              setFormState(previous => ({ ...previous, password: event.target.value }))}
            required
            type="password"
            value={formState.password}
          />

          <ul className="space-y-1 rounded-2xl border border-(--app-border) bg-(--app-bg) px-4 py-3 text-sm text-(--app-subtle)">
            <li>{t("auth.shared.email.hint")}</li>
            <li>{t("auth.shared.password.hint")}</li>
          </ul>

          {mutationError
            ? (
                <p
                  className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
                  role="alert"
                >
                  {mutationError}
                </p>
              )
            : null}

          <button
            className={`${PRIMARY_ACTION_CLASS_NAME} w-full`}
            disabled={registerMutation.isPending}
            type="submit"
          >
            {registerMutation.isPending
              ? t("auth.register.submit.pending")
              : t("auth.register.submit.default")}
          </button>
        </form>

        <p className="mt-6 text-sm text-(--app-subtle)">
          {t("auth.register.footer.haveAccount")}
          {" "}
          <Link className={INLINE_ACTION_CLASS_NAME} to="/login">
            {t("auth.register.footer.signIn")}
          </Link>
          .
        </p>
      </section>
    </main>
  );
};
