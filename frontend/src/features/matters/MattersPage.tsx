import { defaultQueryPolicy } from "@/app/query-policy";
import {
  expectNumberField,
  expectRecord,
  expectStringField,
} from "@/shared/api/contracts";
import { apiRequest } from "@/shared/api/http";
import { t } from "@/shared/i18n/ui-text";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { type FormEvent, useState } from "react";
import {
  Link,
  useNavigate,
  useParams,
  useSearchParams,
} from "react-router-dom";
import {
  createMatter,
  matterQueryOptions,
  MATTERS_QUERY_KEY,
  mattersQueryOptions,
  updateMatter,
} from "./api";
import type { MatterInput, MatterRecord, MatterStatus } from "./contracts";
import { MatterNotes } from "./matter-notes/MatterNotes";

const DASHBOARD_QUERY_KEY = ["dashboard"] as const;

interface MatterClientOption {
  id: number;
  full_name: string;
}
const parseMatterClientOptions = (payload: unknown): MatterClientOption[] => {
  const list = expectRecord(payload, "MatterClientList");
  if (!Array.isArray(list.items))
    throw new Error("MatterClientList: invalid items");
  return list.items.map((item) => {
    const client = expectRecord(item, "MatterClientOption");
    return {
      id: expectNumberField(client, "id", "MatterClientOption"),
      full_name: expectStringField(client, "full_name", "MatterClientOption", {
        minLength: 1,
      }),
    };
  });
};
const readMatterClientOptions = (
  search: string,
): Promise<MatterClientOption[]> =>
  apiRequest<MatterClientOption[]>(
    `/clients?limit=100${search ? `&search=${encodeURIComponent(search)}` : ""}`,
    { parse: parseMatterClientOptions },
  );

export const MatterList = ({ clientId }: { clientId?: number }) => {
  const query = useQuery(mattersQueryOptions(clientId));
  if (query.isPending) return <p>{t("matters.loading")}</p>;
  if (query.isError) return <p role="alert">{t("matters.error")}</p>;
  if (!query.data.items.length) return <p>{t("matters.empty")}</p>;
  return (
    <ul className="mt-4 grid gap-3">
      {query.data.items.map((matter) => (
        <li className="rounded-xl border p-4" key={matter.id}>
          <Link className="font-semibold" to={`/matters/${matter.id}`}>
            {matter.title}
          </Link>
          <p>
            {t(`matters.status.${matter.status}` as const)} ·{" "}
            {matter.matter_type}
          </p>
          {matter.next_action ? (
            <p>
              {t("matters.next")}: {matter.next_action}
            </p>
          ) : null}
        </li>
      ))}
    </ul>
  );
};

const empty: MatterInput = {
  client_id: 0,
  title: "",
  matter_type: "",
  status: "active",
  counterparty: null,
  description: null,
  next_action: null,
  next_action_date: null,
};

const ClientCombobox = ({
  value,
  onChange,
}: {
  value: number;
  onChange: (clientId: number) => void;
}) => {
  const [search, setSearch] = useState("");
  const [open, setOpen] = useState(false);
  const clients = useQuery({
    queryKey: ["matters", "client-options", search] as const,
    queryFn: () => readMatterClientOptions(search),
    ...defaultQueryPolicy,
  });
  const clientOptions = clients.data ?? [];
  const selected = clientOptions.find((client) => client.id === value);
  const choose = (client: MatterClientOption) => {
    onChange(client.id);
    setSearch(client.full_name);
    setOpen(false);
  };
  return (
    <div className="relative">
      <label className="font-medium" htmlFor="matter-client">
        {t("matters.fields.client")}
      </label>
      <input
        aria-autocomplete="list"
        aria-controls="matter-client-options"
        aria-expanded={open}
        className="mt-1 w-full rounded-xl border p-3"
        id="matter-client"
        onChange={(event) => {
          setSearch(event.target.value);
          onChange(0);
          setOpen(true);
        }}
        onFocus={() => setOpen(true)}
        placeholder={t("matters.fields.clientSearch")}
        role="combobox"
        value={search !== "" ? search : (selected?.full_name ?? "")}
      />
      {open ? (
        <ul
          className="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-xl border bg-white p-1 shadow-lg"
          id="matter-client-options"
          role="listbox"
        >
          {clients.isPending ? (
            <li className="p-3">{t("matters.fields.clientLoading")}</li>
          ) : null}
          {clients.isError ? (
            <li className="p-3" role="alert">
              {t("matters.fields.clientError")}
            </li>
          ) : null}
          {clients.data && !clientOptions.length ? (
            <li className="p-3">{t("matters.fields.clientEmpty")}</li>
          ) : null}
          {clientOptions.map((client) => (
            <li
              key={client.id}
              role="option"
              aria-selected={client.id === value}
            >
              <button
                className="w-full rounded-lg p-3 text-left hover:bg-slate-100"
                onMouseDown={(event) => event.preventDefault()}
                onClick={() => choose(client)}
                type="button"
              >
                {client.full_name}
              </button>
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  );
};

const MatterForm = ({ initial }: { initial?: MatterRecord }) => {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const qc = useQueryClient();
  const [form, setForm] = useState<MatterInput>(
    initial ?? { ...empty, client_id: Number(params.get("clientId")) || 0 },
  );
  const [validation, setValidation] = useState(false);
  const mutation = useMutation({
    mutationFn: (payload: MatterInput) =>
      initial ? updateMatter(initial.id, payload) : createMatter(payload),
    onSuccess: async (record) => {
      await Promise.all([
        qc.invalidateQueries({ queryKey: MATTERS_QUERY_KEY }),
        qc.invalidateQueries({ queryKey: DASHBOARD_QUERY_KEY }),
      ]);
      void navigate(`/matters/${record.id}`);
    },
  });
  const submit = (event: FormEvent) => {
    event.preventDefault();
    if (!form.client_id || !form.title.trim() || !form.matter_type.trim()) {
      setValidation(true);
      return;
    }
    if (
      initial &&
      form.client_id !== initial.client_id &&
      !window.confirm(t("matters.fields.clientChangeConfirm"))
    )
      return;
    setValidation(false);
    mutation.mutate(form);
  };
  const input = (key: keyof MatterInput, label: string, type = "text") => (
    <label className="font-medium">
      {label}
      <input
        className="mt-1 w-full rounded-xl border p-3"
        type={type}
        value={String(form[key] ?? "")}
        onChange={(e) => setForm({ ...form, [key]: e.target.value })}
      />
    </label>
  );
  return (
    <form className="mt-6 grid gap-4" onSubmit={submit}>
      <ClientCombobox
        value={form.client_id}
        onChange={(clientId) => setForm({ ...form, client_id: clientId })}
      />
      {input("title", t("matters.fields.title"))}
      {input("matter_type", t("matters.fields.type"))}
      <label>
        {t("matters.fields.status")}
        <select
          className="mt-1 w-full rounded-xl border p-3"
          value={form.status}
          onChange={(e) =>
            setForm({ ...form, status: e.target.value as MatterStatus })
          }
        >
          <option value="active">{t("matters.status.active")}</option>
          <option value="pending">{t("matters.status.pending")}</option>
          <option value="closed">{t("matters.status.closed")}</option>
        </select>
      </label>
      {input("counterparty", t("matters.fields.counterparty"))}
      {input("next_action", t("matters.fields.next"))}
      {input("next_action_date", t("matters.fields.nextDate"), "date")}
      <label>
        {t("matters.fields.description")}
        <textarea
          className="mt-1 min-h-28 w-full rounded-xl border p-3"
          value={form.description ?? ""}
          onChange={(e) => setForm({ ...form, description: e.target.value })}
        />
      </label>
      {validation ? <p role="alert">{t("matters.validation")}</p> : null}
      {mutation.isError ? <p role="alert">{t("matters.error")}</p> : null}
      <button
        className="rounded-full bg-[var(--app-accent)] px-5 py-3 text-white"
        disabled={mutation.isPending}
      >
        {t("matters.save")}
      </button>
    </form>
  );
};
export const MattersPage = () => {
  const [params] = useSearchParams();
  const clientId = Number(params.get("clientId")) || undefined;
  return (
    <main className="mx-auto max-w-5xl p-6 sm:p-10">
      <div className="flex justify-between">
        <h1 className="text-4xl font-semibold">{t("matters.title")}</h1>
        <Link
          to={clientId ? `/matters/new?clientId=${clientId}` : "/matters/new"}
        >
          {t("matters.new")}
        </Link>
      </div>
      <MatterList clientId={clientId} />
    </main>
  );
};
export const NewMatterPage = () => (
  <main className="mx-auto max-w-2xl p-6 sm:p-10">
    <h1 className="text-4xl font-semibold">{t("matters.create.title")}</h1>
    <MatterForm />
  </main>
);
export const MatterDetailPage = ({ edit = false }: { edit?: boolean }) => {
  const id = Number(useParams().matterId);
  const query = useQuery(matterQueryOptions(id));
  if (query.isPending)
    return <main className="p-8">{t("matters.loading")}</main>;
  if (query.isError)
    return (
      <main className="p-8" role="alert">
        {t("matters.error")}
      </main>
    );
  if (edit)
    return (
      <main className="mx-auto max-w-2xl p-6 sm:p-10">
        <h1>{t("matters.edit")}</h1>
        <MatterForm initial={query.data} />
      </main>
    );
  const m = query.data;
  return (
    <main className="mx-auto max-w-4xl p-6 sm:p-10">
      <Link to="/matters">{t("matters.back")}</Link>
      <h1 className="mt-5 text-4xl font-semibold">{m.title}</h1>
      <p>
        {m.matter_type} · {t(`matters.status.${m.status}` as const)}
      </p>
      {m.counterparty ? (
        <p>
          {t("matters.fields.counterparty")}: {m.counterparty}
        </p>
      ) : null}
      {m.next_action ? (
        <p>
          {t("matters.next")}: {m.next_action}
          {m.next_action_date ? ` · ${m.next_action_date}` : ""}
        </p>
      ) : null}
      {m.description ? (
        <p className="whitespace-pre-wrap">{m.description}</p>
      ) : null}
      <Link to={`/matters/${id}/edit`}>{t("matters.edit")}</Link>
      <MatterNotes matterId={id} />
    </main>
  );
};
