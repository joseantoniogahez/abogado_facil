import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { type FormEvent, useEffect, useState } from "react";

import { t } from "@/shared/i18n/ui-text";
import { ACCENT_ACTION_CLASS_NAME, SECONDARY_ACTION_CLASS_NAME } from "@/shared/ui/actionStyles";

import {
  createMatterPayment,
  matterPaymentsQueryKey,
  matterPaymentsQueryOptions,
  updateMatterBilling,
} from "./api";

const today = () => new Date().toISOString().slice(0, 10);
const money = (value: string) => new Intl.NumberFormat("es-MX", { style: "currency", currency: "MXN" }).format(Number(value));

export const MatterPayments = ({ matterId }: { matterId: number }) => {
  const qc = useQueryClient();
  const query = useQuery(matterPaymentsQueryOptions(matterId));
  const [fee, setFee] = useState("0.00");
  const [notes, setNotes] = useState("");
  const [amount, setAmount] = useState("");
  const [type, setType] = useState<"advance" | "partial">("advance");
  const [paidOn, setPaidOn] = useState(today());
  const [note, setNote] = useState("");
  useEffect(() => {
    if (query.data) {
      setFee(query.data.agreed_fee);
      setNotes(query.data.notes ?? "");
    }
  }, [query.data]);
  const refresh = () => qc.invalidateQueries({ queryKey: matterPaymentsQueryKey(matterId) });
  const billing = useMutation({ mutationFn: () => updateMatterBilling(matterId, fee, notes), onSuccess: refresh });
  const payment = useMutation({
    mutationFn: () => createMatterPayment(matterId, { amount, payment_type: type, paid_on: paidOn, note: note || null }),
    onSuccess: async () => { setAmount(""); setNote(""); await refresh(); },
  });
  const submitPayment = (event: FormEvent) => {
    event.preventDefault();
    if (Number(amount) > 0 && paidOn) payment.mutate();
  };
  return (
    <section aria-labelledby="matter-payments-title" className="mt-10">
      <h2 className="text-2xl font-semibold" id="matter-payments-title">{t("matterPayments.title")}</h2>
      {query.isPending ? <p>{t("matterPayments.loading")}</p> : null}
      {query.isError ? <p role="alert">{t("matterPayments.error")}</p> : null}
      {query.data
        ? (
            <>
              <dl className="mt-4 grid gap-3 sm:grid-cols-3">
                <div>
                  <dt>{t("matterPayments.fee")}</dt>
                  <dd className="font-semibold">{money(query.data.agreed_fee)}</dd>
                </div>
                <div>
                  <dt>{t("matterPayments.paid")}</dt>
                  <dd className="font-semibold">{money(query.data.total_paid)}</dd>
                </div>
                <div>
                  <dt>{t("matterPayments.balance")}</dt>
                  <dd className="font-semibold">{money(query.data.balance)}</dd>
                </div>
              </dl>
              <form className="mt-4 grid gap-3" onSubmit={(event) => { event.preventDefault(); billing.mutate(); }}>
                <label>
                  {t("matterPayments.fee")}
                  <input className="mt-1 w-full rounded-xl border p-3" min="0" step="0.01" type="number" value={fee} onChange={e => setFee(e.target.value)} />
                </label>
                <label>
                  {t("matterPayments.notes")}
                  <textarea className="mt-1 min-h-28 w-full rounded-xl border p-3" maxLength={4000} value={notes} onChange={e => setNotes(e.target.value)} />
                </label>
                <button className={`${SECONDARY_ACTION_CLASS_NAME} w-fit`} disabled={billing.isPending}>{t("matterPayments.save")}</button>
              </form>
              <h3 className="mt-6 text-xl font-semibold">{t("matterPayments.history")}</h3>
              {query.data.payments.length
                ? (
                    <ul className="mt-3 grid gap-2">
                      {query.data.payments.map(item => (
                        <li className="rounded-xl border p-3" key={item.id}>
                          <strong>{money(item.amount)}</strong>
                          {" "}
                          ·
                          {" "}
                          {t(`matterPayments.type.${item.payment_type}` as const)}
                          {" "}
                          ·
                          {" "}
                          {item.paid_on}
                          {item.note ? <p>{item.note}</p> : null}
                        </li>
                      ))}
                    </ul>
                  )
                : <p>{t("matterPayments.empty")}</p>}
              <form className="mt-5 grid gap-3" onSubmit={submitPayment}>
                <label>
                  {t("matterPayments.amount")}
                  <input className="mt-1 w-full rounded-xl border p-3" min="0.01" required step="0.01" type="number" value={amount} onChange={e => setAmount(e.target.value)} />
                </label>
                <label>
                  {t("matterPayments.type")}
                  <select className="mt-1 w-full rounded-xl border p-3" value={type} onChange={e => setType(e.target.value as typeof type)}>
                    <option value="advance">{t("matterPayments.type.advance")}</option>
                    <option value="partial">{t("matterPayments.type.partial")}</option>
                  </select>
                </label>
                <label>
                  {t("matterPayments.date")}
                  <input className="mt-1 w-full rounded-xl border p-3" required type="date" value={paidOn} onChange={e => setPaidOn(e.target.value)} />
                </label>
                <label>
                  {t("matterPayments.paymentNote")}
                  <input className="mt-1 w-full rounded-xl border p-3" maxLength={1000} value={note} onChange={e => setNote(e.target.value)} />
                </label>
                <button className={`${ACCENT_ACTION_CLASS_NAME} w-fit`} disabled={payment.isPending}>{t("matterPayments.add")}</button>
              </form>
              {billing.isError || payment.isError ? <p role="alert">{t("matterPayments.mutationError")}</p> : null}
            </>
          )
        : null}
    </section>
  );
};
