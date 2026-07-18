import { parseClient, parseClientList } from "@/features/clients/contracts";

const client = {
  id: 1, full_name: "Ana Pérez", phone: "5512345678", email: null, address: null, notes: null,
  created_at: "2026-05-01T12:00:00Z", updated_at: "2026-05-01T12:00:00Z",
};

describe("client contracts", () => {
  it("parses nullable and populated optional fields", () => {
    expect(parseClient(client)).toEqual(client);
    expect(parseClient({ ...client, email: "ana@example.com", address: "Centro", notes: "VIP" })).toMatchObject({
      email: "ana@example.com", address: "Centro", notes: "VIP",
    });
  });

  it("rejects invalid phone and list payloads", () => {
    expect(() => parseClient({ ...client, phone: "551234567a" })).toThrow("phone must contain 10 digits");
    expect(() => parseClient({ ...client, email: 42 })).toThrow();
    expect(() => parseClientList({ ...client })).toThrow("ClientList: invalid items");
    expect(parseClientList({ items: [client], total: 1, limit: 20, offset: 0 })).toMatchObject({ total: 1 });
  });
});
