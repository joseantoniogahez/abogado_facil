import { QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { createQueryClient } from "@/app/query-client";
import { t } from "@/shared/i18n/ui-text";

import { MatterCalculations } from "./MatterCalculations";

const result = { id: 1, calculation_type: "debt_balance", result_amount: "7500.00", summary: "Adeudo estimado: $7500.00 MXN.", disclaimer: "Estimación informativa." };
const response = (payload: unknown, status = 200): Partial<Response> => ({ ok: status < 400, status, statusText: "OK", headers: new Headers(), json: () => Promise.resolve(payload) });

describe("MatterCalculations", () => {
  it("calculates, copies, saves and changes calculator inputs", async () => {
    const fetchMock = vi.fn().mockImplementation((url: string) => Promise.resolve(response(url.endsWith("/calculations") ? { items: [result] } : result)));
    vi.stubGlobal("fetch", fetchMock);
    Object.assign(navigator, { clipboard: { writeText: vi.fn().mockResolvedValue(undefined) } });
    render(<QueryClientProvider client={createQueryClient()}><MatterCalculations matterId={7} /></QueryClientProvider>);
    expect(await screen.findByText(result.summary)).toBeInTheDocument();
    const user = userEvent.setup();
    await user.clear(screen.getByLabelText(t("matterCalculations.principal")));
    await user.type(screen.getByLabelText(t("matterCalculations.principal")), "10000");
    await user.click(screen.getByRole("button", { name: t("matterCalculations.calculate") }));
    expect((await screen.findAllByText(result.disclaimer)).length).toBeGreaterThan(0);
    await user.click(screen.getByRole("button", { name: t("matterCalculations.copy") }));
    await user.click(screen.getByRole("button", { name: t("matterCalculations.save") }));
    await user.selectOptions(screen.getByLabelText(t("matterCalculations.kind")), "overdue_rent");
    await user.type(screen.getByLabelText(t("matterCalculations.monthlyRent")), "4000");
    await user.type(screen.getByLabelText(t("matterCalculations.months")), "3");
    await user.selectOptions(screen.getByLabelText(t("matterCalculations.kind")), "simple_interest");
    await user.type(screen.getByLabelText(t("matterCalculations.rate")), "12");
    await user.type(screen.getByLabelText(t("matterCalculations.days")), "30");
    expect(fetchMock).toHaveBeenCalled();
  });

  it("shows empty and error states", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(response({ items: [] })));
    const view = render(<QueryClientProvider client={createQueryClient()}><MatterCalculations matterId={8} /></QueryClientProvider>);
    expect(await screen.findByText(t("matterCalculations.empty"))).toBeInTheDocument();
    view.unmount();
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(response({}, 400)));
    const client = createQueryClient();
    client.setQueryDefaults(["matter-calculations"], { retry: false });
    render(<QueryClientProvider client={client}><MatterCalculations matterId={9} /></QueryClientProvider>);
    expect(await screen.findByRole("alert")).toBeInTheDocument();
  });
});
