import { parseMatterTask, parseMatterTasks } from "@/features/matters/matter-tasks/contracts";

const task = {
  id: 1, matter_id: 2, title: "Revisar expediente", due_date: "2026-06-01", completed: false,
  created_at: "2026-05-01T12:00:00Z", updated_at: "2026-05-01T12:00:00Z",
};

describe("matter task contracts", () => {
  it("parses task lists", () => {
    expect(parseMatterTask(task)).toEqual(task);
    expect(parseMatterTasks({ items: [task], total: 1 })).toEqual({ items: [task], total: 1 });
  });

  it("rejects malformed task lists and fields", () => {
    expect(() => parseMatterTasks({ items: null, total: 0 })).toThrow("invalid items");
    expect(() => parseMatterTask({ ...task, completed: "no" })).toThrow();
  });
});
