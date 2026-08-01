import { parseChecklist, parseChecklistItem } from "@/features/matters/matter-checklist/contracts";

const item = {
  id: 1, matter_id: 2, label: "Identificación", status: "pending", is_custom: false, is_ai_suggested: false, position: 0,
  created_at: "2026-05-01T12:00:00Z", updated_at: "2026-05-01T12:00:00Z",
} as const;

describe("checklist contracts", () => {
  it("parses each supported status and checklist payload", () => {
    expect(parseChecklistItem(item)).toEqual(item);
    expect(parseChecklistItem({ ...item, status: "complete" })).toMatchObject({ status: "complete" });
    expect(parseChecklistItem({ ...item, status: "not_applicable" })).toMatchObject({ status: "not_applicable" });
    expect(parseChecklist({ items: [item], total: 1 })).toEqual({ items: [item], total: 1 });
  });

  it("rejects invalid checklist payloads", () => {
    expect(() => parseChecklistItem({ ...item, status: "unknown" })).toThrow("invalid status");
    expect(() => parseChecklist({ items: null, total: 0 })).toThrow("invalid items");
  });
});
