import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { FormEvent, useState } from "react";
import { Link, useNavigate, useParams } from "react-router";

import { defaultMutationPolicy } from "@/app/mutation-policy";
import {
  clientQueryOptions,
  CLIENTS_QUERY_KEY,
  clientsQueryOptions,
  createClient,
  updateClient,
} from "@/features/clients/api";
import type { ClientInput, ClientRecord } from "@/features/clients/contracts";
import { appendRequestIdDiagnostic, getApiErrorRequestId } from "@/shared/api/errors";
import { t } from "@/shared/i18n/ui-text";
import {
  ACCENT_ACTION_CLASS_NAME,
  INLINE_ACTION_CLASS_NAME,
  QUIET_ACTION_CLASS_NAME,
  SECONDARY_ACTION_CLASS_NAME,
} from "@/shared/ui/actionStyles";

export const ClientsPage = () => {
  const [search, setSearch] = useState("");
  const clients = useQuery(clientsQueryOptions(search.trim()));
  return (
    <main className="mx-auto max-w-5xl p-6 sm:p-10">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="mono-label">{t("clients.badge")}</p>
          <h1 className="text-4xl font-semibold">{t("clients.title")}</h1>
        </div>
        <Link className={ACCENT_ACTION_CLASS_NAME} to="/clients/new">
          {t("clients.new")}
        </Link>
      </div>
      <label className="mt-8 block font-medium">
        {t("clients.search")}
        <input
          className="mt-2 w-full rounded-xl border p-3"
          onChange={event => setSearch(event.target.value)}
          value={search}
        />
      </label>
      {clients.isPending
        ? (
            <p className="mt-8">{t("clients.loading")}</p>
          )
        : clients.isError
          ? (
              <div className="mt-8">
                <p>
                  {appendRequestIdDiagnostic(t("clients.error"), getApiErrorRequestId(clients.error))}
                </p>
                <button
                  className={`${SECONDARY_ACTION_CLASS_NAME} mt-4`}
                  onClick={() => void clients.refetch()}
                  type="button"
                >
                  {t("dashboard.retry")}
                </button>
              </div>
            )
          : clients.data.items.length === 0
            ? (
                <p className="mt-8">{search ? t("clients.noResults") : t("clients.empty")}</p>
              )
            : (
                <ul className="mt-8 grid gap-3">
                  {clients.data.items.map(client => (
                    <li className="rounded-2xl border p-5" key={client.id}>
                      <Link className={INLINE_ACTION_CLASS_NAME} to={`/clients/${client.id}`}>
                        {client.full_name}
                      </Link>
                      <p>
                        {client.phone}
                        {client.email ? ` · ${client.email}` : ""}
                      </p>
                    </li>
                  ))}
                </ul>
              )}
    </main>
  );
};

const emptyInput: ClientInput = {
  full_name: "",
  phone: "",
  email: null,
  address: null,
  notes: null,
};
const normalizePhoneInput = (value: string) =>
  value
    .replace(/\D/g, "")
    .replace(/^52(?=\d{10}$)/, "")
    .slice(0, 10);

const ClientForm = ({ initial, clientId }: { initial?: ClientRecord; clientId?: number }) => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [form, setForm] = useState<ClientInput>(initial ?? emptyInput);
  const [validation, setValidation] = useState<string | null>(null);
  const mutation = useMutation({
    ...defaultMutationPolicy,
    mutationFn: (payload: ClientInput) =>
      clientId ? updateClient(clientId, payload) : createClient(payload),
    onSuccess: async (client) => {
      await queryClient.invalidateQueries({ queryKey: CLIENTS_QUERY_KEY });
      await queryClient.invalidateQueries({
        queryKey: ["dashboard", "summary"],
      });
      void navigate(`/clients/${client.id}`);
    },
  });
  const optionalValue = (value: string | null | undefined) => {
    const trimmed = value?.trim();
    return trimmed === "" || trimmed === undefined ? null : trimmed;
  };
  const submit = (event: FormEvent) => {
    event.preventDefault();
    if (!form.full_name.trim() || !form.phone.trim()) {
      setValidation(t("clients.validation.required"));
      return;
    }
    if (!/^\d{10}$/.test(form.phone)) {
      setValidation(t("clients.validation.phone"));
      return;
    }
    setValidation(null);
    mutation.mutate({
      ...form,
      phone: normalizePhoneInput(form.phone),
      email: optionalValue(form.email),
      address: optionalValue(form.address),
      notes: optionalValue(form.notes),
    });
  };
  const field = (name: keyof ClientInput, label: string, required = false) => (
    <label className="block font-medium">
      {label}
      <input
        className="mt-1 w-full rounded-xl border p-3"
        required={required}
        value={form[name] ?? ""}
        onChange={event => setForm({ ...form, [name]: event.target.value })}
      />
    </label>
  );
  return (
    <form className="mt-8 grid gap-4" onSubmit={submit}>
      {field("full_name", t("clients.fields.name"), true)}
      <label className="block font-medium">
        {t("clients.fields.phone")}
        <input
          className="mt-1 w-full rounded-xl border p-3"
          inputMode="numeric"
          maxLength={10}
          required
          value={form.phone}
          onChange={event => setForm({ ...form, phone: normalizePhoneInput(event.target.value) })}
        />
        <span className="mt-1 block text-sm text-[var(--app-subtle)]">
          {t("clients.fields.phone.help")}
        </span>
      </label>
      {field("email", t("clients.fields.email"))}
      {field("address", t("clients.fields.address"))}
      <label className="font-medium">
        {t("clients.fields.notes")}
        <textarea
          className="mt-1 min-h-28 w-full rounded-xl border p-3"
          value={form.notes ?? ""}
          onChange={event => setForm({ ...form, notes: event.target.value })}
        />
      </label>
      {validation ? <p role="alert">{validation}</p> : null}
      {mutation.isError ? <p role="alert">{t("clients.error")}</p> : null}
      <button className={ACCENT_ACTION_CLASS_NAME} disabled={mutation.isPending} type="submit">
        {mutation.isPending ? t("clients.saving") : t("clients.save")}
      </button>
    </form>
  );
};

export const NewClientPage = () => (
  <main className="mx-auto max-w-2xl p-6 sm:p-10">
    <h1 className="text-4xl font-semibold">{t("clients.create.title")}</h1>
    <ClientForm />
  </main>
);

export const ClientDetailPage = ({ edit = false }: { edit?: boolean }) => {
  const clientId = Number(useParams().clientId);
  const client = useQuery(clientQueryOptions(clientId));
  if (client.isPending) return <main className="p-8">{t("clients.loading")}</main>;
  if (client.isError) return <main className="p-8">{t("clients.error")}</main>;
  if (edit)
    return (
      <main className="mx-auto max-w-2xl p-6 sm:p-10">
        <h1 className="text-4xl font-semibold">{t("clients.edit.title")}</h1>
        <ClientForm clientId={clientId} initial={client.data} />
      </main>
    );
  return (
    <main className="mx-auto max-w-4xl p-6 sm:p-10">
      <Link className={QUIET_ACTION_CLASS_NAME} to="/clients">
        {t("clients.back")}
      </Link>
      <h1 className="mt-5 text-4xl font-semibold">{client.data.full_name}</h1>
      <p className="mt-3">{client.data.phone}</p>
      {client.data.email ? <p>{client.data.email}</p> : null}
      {client.data.address ? <p className="mt-4">{client.data.address}</p> : null}
      {client.data.notes ? <p className="mt-4 whitespace-pre-wrap">{client.data.notes}</p> : null}
      <Link className={`${SECONDARY_ACTION_CLASS_NAME} mt-6`} to={`/clients/${clientId}/edit`}>
        {t("clients.edit")}
      </Link>
      <section className="mt-10 rounded-2xl border p-5">
        <h2 className="text-xl font-semibold">{t("clients.matters.title")}</h2>
        <div className="mt-3 flex flex-wrap gap-4">
          <Link className={SECONDARY_ACTION_CLASS_NAME} to={`/matters?clientId=${clientId}`}>
            {t("matters.viewForClient")}
          </Link>
          <Link className={ACCENT_ACTION_CLASS_NAME} to={`/matters/new?clientId=${clientId}`}>
            {t("matters.new")}
          </Link>
        </div>
      </section>
    </main>
  );
};
