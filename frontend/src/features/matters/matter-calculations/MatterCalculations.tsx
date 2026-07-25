import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { type SyntheticEvent, useState } from "react";

import { apiRequest } from "@/shared/api/http";
import { t } from "@/shared/i18n/ui-text";
import { ACCENT_ACTION_CLASS_NAME, SECONDARY_ACTION_CLASS_NAME } from "@/shared/ui/actionStyles";

type Kind = "debt_balance" | "overdue_rent" | "simple_interest";
interface Result { id: number | null; calculation_type: Kind; result_amount: string; summary: string; disclaimer: string }
const key = (id: number) => ["matter-calculations", id] as const;
const parseResult = (value: unknown): Result => value as Result;

export const MatterCalculations = ({ matterId }: { matterId: number }) => {
  const client = useQueryClient();
  const [kind, setKind] = useState<Kind>("debt_balance");
  const [principal, setPrincipal] = useState("0");
  const [payments, setPayments] = useState("0");
  const [rent, setRent] = useState("0");
  const [months, setMonths] = useState("0");
  const [rate, setRate] = useState("0");
  const [days, setDays] = useState("0");
  const payload = { calculation_type: kind, principal, payments, monthly_rent: rent, overdue_months: Number(months), annual_rate: rate, days: Number(days) };
  const history = useQuery({ queryKey: key(matterId), queryFn: () => apiRequest(`/matters/${matterId}/calculations`, { parse: value => value as { items: Result[] } }) });
  const preview = useMutation({ mutationFn: () => apiRequest(`/matters/${matterId}/calculations/preview`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload), parse: parseResult }) });
  const save = useMutation({ mutationFn: () => apiRequest(`/matters/${matterId}/calculations`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload), parse: parseResult }), onSuccess: () => client.invalidateQueries({ queryKey: key(matterId) }) });
  const submit = (event: SyntheticEvent<HTMLFormElement>) => { event.preventDefault(); preview.mutate(); };
  const field = "mt-1 w-full rounded-xl border p-3";
  return (
    <section aria-labelledby="calculations-title" className="mt-10">
      <h2 className="text-2xl font-semibold" id="calculations-title">{t("matterCalculations.title")}</h2>
      <p>{t("matterCalculations.disclaimer")}</p>
      <form className="mt-4 grid gap-3" onSubmit={submit}>
        <label>
          {t("matterCalculations.kind")}
          <select className={field} value={kind} onChange={e => setKind(e.target.value as Kind)}>
            <option value="debt_balance">{t("matterCalculations.debt")}</option>
            <option value="overdue_rent">{t("matterCalculations.rent")}</option>
            <option value="simple_interest">{t("matterCalculations.interest")}</option>
          </select>
        </label>
        {kind !== "overdue_rent"
          ? (
              <label>
                {t("matterCalculations.principal")}
                <input className={field} min="0" step="0.01" type="number" value={principal} onChange={e => setPrincipal(e.target.value)} />
              </label>
            )
          : null}
        {kind !== "simple_interest"
          ? (
              <label>
                {t("matterCalculations.payments")}
                <input className={field} min="0" step="0.01" type="number" value={payments} onChange={e => setPayments(e.target.value)} />
              </label>
            )
          : null}
        {kind === "overdue_rent"
          ? (
              <>
                <label>
                  {t("matterCalculations.monthlyRent")}
                  <input className={field} min="0" step="0.01" type="number" value={rent} onChange={e => setRent(e.target.value)} />
                </label>
                <label>
                  {t("matterCalculations.months")}
                  <input className={field} min="1" type="number" value={months} onChange={e => setMonths(e.target.value)} />
                </label>
              </>
            )
          : null}
        {kind === "simple_interest"
          ? (
              <>
                <label>
                  {t("matterCalculations.rate")}
                  <input className={field} min="0" step="0.01" type="number" value={rate} onChange={e => setRate(e.target.value)} />
                </label>
                <label>
                  {t("matterCalculations.days")}
                  <input className={field} min="1" type="number" value={days} onChange={e => setDays(e.target.value)} />
                </label>
              </>
            )
          : null}
        <button className={`${ACCENT_ACTION_CLASS_NAME} w-fit`}>{t("matterCalculations.calculate")}</button>
      </form>
      {preview.data
        ? (
            <div aria-live="polite" className="mt-4 rounded-xl border p-4">
              <strong>{preview.data.summary}</strong>
              <p>{preview.data.disclaimer}</p>
              <div className="mt-3 flex gap-2">
                <button className={SECONDARY_ACTION_CLASS_NAME} onClick={() => { void navigator.clipboard.writeText(`${preview.data.summary} ${preview.data.disclaimer}`); }} type="button">{t("matterCalculations.copy")}</button>
                <button className={SECONDARY_ACTION_CLASS_NAME} disabled={save.isPending} onClick={() => save.mutate()} type="button">{t("matterCalculations.save")}</button>
              </div>
            </div>
          )
        : null}
      {preview.isError || save.isError || history.isError ? <p role="alert">{t("matterCalculations.error")}</p> : null}
      <h3 className="mt-6 text-xl font-semibold">{t("matterCalculations.history")}</h3>
      {history.data?.items.length
        ? (
            <ul className="mt-3 grid gap-2">
              {history.data.items.map(item => (
                <li className="rounded-xl border p-3" key={item.id}>
                  {item.summary}
                  <p>{item.disclaimer}</p>
                </li>
              ))}
            </ul>
          )
        : <p>{t("matterCalculations.empty")}</p>}
    </section>
  );
};
