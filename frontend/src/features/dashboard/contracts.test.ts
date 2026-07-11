import { ApiContractError } from "@/shared/api/contracts";
import { parseDashboardSummary } from "@/features/dashboard/contracts";

const validSummary = {
  firm_id: 1,
  firm_name: "Despacho Prueba",
  clients: { value: 0, available: false },
  active_matters: { value: 0, available: false },
  pending_tasks: { value: 0, available: false },
  upcoming_tasks: [],
  ai_status: "not_available",
  actions: [{ id: "create_client", available: false }],
};

describe("parseDashboardSummary", () => {
  it("parses the deterministic unavailable summary", () => {
    expect(parseDashboardSummary(validSummary)).toEqual(validSummary);
  });

  it("rejects unknown AI states", () => {
    expect(() => parseDashboardSummary({ ...validSummary, ai_status: "secret_ready" })).toThrow(ApiContractError);
  });

  it("rejects malformed availability", () => {
    expect(() => parseDashboardSummary({ ...validSummary, clients: { value: 0, available: "no" } })).toThrow(
      ApiContractError,
    );
  });
});
