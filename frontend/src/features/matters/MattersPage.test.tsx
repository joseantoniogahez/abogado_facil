import { describe, expect, it } from "vitest";
import { parseMatter, parseMatterList } from "./contracts";

const matter = { id: 1, client_id: 2, title: "Pensión", matter_type: "Familiar", status: "active", counterparty: null, description: null, next_action: "Pedir actas", next_action_date: null, created_at: "2026-07-12T00:00:00Z", updated_at: "2026-07-12T00:00:00Z" };

describe("matter contracts", () => {
  it("parses records and lists", () => {
    expect(parseMatter(matter).title).toBe("Pensión");
    expect(parseMatterList({ items: [matter], total: 1, limit: 50, offset: 0 }).items).toHaveLength(1);
  });

  it("rejects malformed records", () => {
    expect(() => parseMatter({ ...matter, status: "unknown" })).toThrow();
    expect(() => parseMatterList({ items: null, total: 0, limit: 50, offset: 0 })).toThrow();
  });
});
