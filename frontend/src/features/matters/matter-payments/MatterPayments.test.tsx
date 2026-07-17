import { QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { createQueryClient } from "@/app/query-client";
import { t } from "@/shared/i18n/ui-text";

import { parseMatterBilling } from "./contracts";
import { MatterPayments } from "./MatterPayments";

const billing = {
  matter_id: 3, currency: "MXN", agreed_fee: "10000.00", total_paid: "2500.00", balance: "7500.00",
  notes: "Mensual", payments: [{
    id: 1, matter_id: 3, amount: "2500.00", payment_type: "advance", paid_on: "2026-07-16",
    note: "Transferencia", created_at: "2026-07-16T10:00:00Z", updated_at: "2026-07-16T10:00:00Z",
  }],
};
const response = (payload: unknown, status = 200): Partial<Response> => ({
  ok: status < 400, status, statusText: "OK", headers: new Headers(), json: () => Promise.resolve(payload),
});

describe("MatterPayments", () => {
  it("parses, displays and records payments", async () => {
    expect(parseMatterBilling(billing).balance).toBe("7500.00");
    const fetchMock = vi.fn().mockImplementation((_url: string, options?: RequestInit) =>
      Promise.resolve(response(billing, options?.method === "POST" ? 201 : 200)));
    vi.stubGlobal("fetch", fetchMock);
    const client = createQueryClient();
    client.setQueryDefaults(["matter-payments"], { retry: false });
    render(<QueryClientProvider client={client}><MatterPayments matterId={3} /></QueryClientProvider>);
    expect(await screen.findByText("Transferencia")).toBeInTheDocument();
    const user = userEvent.setup();
    await user.clear(screen.getByLabelText(t("matterPayments.fee")));
    await user.type(screen.getByLabelText(t("matterPayments.fee")), "12000");
    await user.clear(screen.getByLabelText(t("matterPayments.notes")));
    await user.type(screen.getByLabelText(t("matterPayments.notes")), "Actualizada");
    await user.click(screen.getByRole("button", { name: t("matterPayments.save") }));
    await user.type(screen.getByLabelText(t("matterPayments.amount")), "500");
    await user.selectOptions(screen.getByLabelText(t("matterPayments.type")), "partial");
    await user.clear(screen.getByLabelText(t("matterPayments.date")));
    await user.type(screen.getByLabelText(t("matterPayments.date")), "2026-07-17");
    await user.type(screen.getByLabelText(t("matterPayments.paymentNote")), "Efectivo");
    await user.click(screen.getByRole("button", { name: t("matterPayments.add") }));
    expect(fetchMock).toHaveBeenCalled();
  });

  it("renders empty and error states and rejects invalid contracts", async () => {
    expect(() => parseMatterBilling({ ...billing, currency: "USD" })).toThrow();
    expect(() => parseMatterBilling({ ...billing, payments: [{ ...billing.payments[0], payment_type: "refund" }] }))
      .toThrow();
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(response({ ...billing, payments: [] })));
    const emptyClient = createQueryClient();
    const view = render(
      <QueryClientProvider client={emptyClient}>
        <MatterPayments matterId={4} />
      </QueryClientProvider>,
    );
    expect(await screen.findByText(t("matterPayments.empty"))).toBeInTheDocument();
    view.unmount();

    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(response({}, 400)));
    const errorClient = createQueryClient();
    errorClient.setQueryDefaults(["matter-payments"], { retry: false });
    render(
      <QueryClientProvider client={errorClient}>
        <MatterPayments matterId={5} />
      </QueryClientProvider>,
    );
    expect(await screen.findByRole("alert")).toHaveTextContent(t("matterPayments.error"));
  });
});
