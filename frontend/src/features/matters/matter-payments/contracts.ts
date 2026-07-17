import { expectNumberField, expectRecord, expectStringField } from "@/shared/api/contracts";

export interface MatterPayment {
  id: number;
  matter_id: number;
  amount: string;
  payment_type: "advance" | "partial";
  paid_on: string;
  note: string | null;
}
export interface MatterBilling {
  matter_id: number;
  currency: "MXN";
  agreed_fee: string;
  total_paid: string;
  balance: string;
  notes: string | null;
  payments: MatterPayment[];
}
const nullableString = (record: Record<string, unknown>, key: string, label: string) =>
  record[key] === null ? null : expectStringField(record, key, label);
const parsePayment = (payload: unknown): MatterPayment => {
  const record = expectRecord(payload, "MatterPayment");
  const paymentType = expectStringField(record, "payment_type", "MatterPayment");
  if (paymentType !== "advance" && paymentType !== "partial") throw new Error("MatterPayment: invalid payment_type");
  return {
    id: expectNumberField(record, "id", "MatterPayment"),
    matter_id: expectNumberField(record, "matter_id", "MatterPayment"),
    amount: expectStringField(record, "amount", "MatterPayment"),
    payment_type: paymentType,
    paid_on: expectStringField(record, "paid_on", "MatterPayment"),
    note: nullableString(record, "note", "MatterPayment"),
  };
};
export const parseMatterBilling = (payload: unknown): MatterBilling => {
  const record = expectRecord(payload, "MatterBilling");
  if (record.currency !== "MXN" || !Array.isArray(record.payments)) throw new Error("MatterBilling: invalid payload");
  return {
    matter_id: expectNumberField(record, "matter_id", "MatterBilling"),
    currency: "MXN",
    agreed_fee: expectStringField(record, "agreed_fee", "MatterBilling"),
    total_paid: expectStringField(record, "total_paid", "MatterBilling"),
    balance: expectStringField(record, "balance", "MatterBilling"),
    notes: nullableString(record, "notes", "MatterBilling"),
    payments: record.payments.map(parsePayment),
  };
};
