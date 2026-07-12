import { expectNumberField, expectRecord, expectStringField } from "@/shared/api/contracts";

export interface ClientRecord {
  id: number;
  full_name: string;
  phone: string;
  email: string | null;
  address: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

const optionalString = (record: Record<string, unknown>, key: string, context: string) =>
  record[key] === null ? null : expectStringField(record, key, context);

export const parseClient = (payload: unknown): ClientRecord => {
  const record = expectRecord(payload, "Client");
  const phone = expectStringField(record, "phone", "Client", { minLength: 10 });
  if (!/^\d{10}$/.test(phone)) throw new Error("Client: phone must contain 10 digits");
  return {
    id: expectNumberField(record, "id", "Client"),
    full_name: expectStringField(record, "full_name", "Client", { minLength: 1 }),
    phone,
    email: optionalString(record, "email", "Client"),
    address: optionalString(record, "address", "Client"),
    notes: optionalString(record, "notes", "Client"),
    created_at: expectStringField(record, "created_at", "Client"),
    updated_at: expectStringField(record, "updated_at", "Client"),
  };
};

export interface ClientList {
  items: ClientRecord[];
  total: number;
  limit: number;
  offset: number;
}

export const parseClientList = (payload: unknown): ClientList => {
  const record = expectRecord(payload, "ClientList");
  if (!Array.isArray(record.items)) throw new Error("ClientList: invalid items");
  return { items: record.items.map(parseClient), total: expectNumberField(record, "total", "ClientList"), limit: expectNumberField(record, "limit", "ClientList"), offset: expectNumberField(record, "offset", "ClientList") };
};

export interface ClientInput { full_name: string; phone: string; email?: string | null; address?: string | null; notes?: string | null }
