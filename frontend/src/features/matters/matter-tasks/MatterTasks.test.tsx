import { QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { createQueryClient } from "@/app/query-client";
import { t } from "@/shared/i18n/ui-text";

import { parseMatterTask } from "./contracts";
import { MatterTasks } from "./MatterTasks";

const task = {
  id: 1,
  matter_id: 3,
  title: "Presentar escrito",
  due_date: "2026-07-20",
  completed: false,
  created_at: "2026-07-16T10:00:00Z",
  updated_at: "2026-07-16T10:00:00Z",
};
const response = (payload: unknown, status = 200): Partial<Response> => ({
  ok: status < 400,
  status,
  statusText: "OK",
  headers: new Headers(),
  json: () => Promise.resolve(payload),
});

describe("MatterTasks", () => {
  it("parses and manages tasks", async () => {
    expect(parseMatterTask(task).completed).toBe(false);
    const fetchMock = vi.fn().mockImplementation((_url: string, options?: RequestInit) => {
      if (options?.method === "PATCH") return Promise.resolve(response({ ...task, completed: true }));
      if (options?.method === "POST") return Promise.resolve(response({ ...task, id: 2 }, 201));
      return Promise.resolve(response({ items: [task], total: 1 }));
    });
    vi.stubGlobal("fetch", fetchMock);
    const client = createQueryClient();
    client.setQueryDefaults(["matter-tasks"], { retry: false });
    render(<QueryClientProvider client={client}><MatterTasks matterId={3} /></QueryClientProvider>);
    const user = userEvent.setup();
    expect(await screen.findByText(task.title)).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: t("matterTasks.complete") }));
    await user.type(screen.getByLabelText(t("matterTasks.task")), "Nueva tarea");
    await user.click(screen.getByRole("button", { name: t("matterTasks.add") }));
    await waitFor(() => expect(fetchMock).toHaveBeenCalled());
  });

  it("edits, reopens, and renders empty and error states", async () => {
    const completedTask = { ...task, due_date: "2020-01-01", completed: true };
    const fetchMock = vi.fn().mockImplementation((_url: string, options?: RequestInit) => {
      if (options?.method === "PATCH") return Promise.resolve(response(completedTask));
      return Promise.resolve(response({ items: [completedTask], total: 1 }));
    });
    vi.stubGlobal("fetch", fetchMock);
    const client = createQueryClient();
    client.setQueryDefaults(["matter-tasks"], { retry: false });
    const view = render(
      <QueryClientProvider client={client}>
        <MatterTasks matterId={3} />
      </QueryClientProvider>,
    );
    const user = userEvent.setup();
    expect(await screen.findByText(completedTask.title)).toHaveClass("line-through");
    await user.click(screen.getByRole("button", { name: t("matterTasks.edit") }));
    const editTitle = screen.getAllByLabelText(t("matterTasks.task"))[0];
    await user.clear(editTitle);
    await user.type(editTitle, "Escrito corregido");
    await user.click(screen.getByRole("button", { name: t("matterTasks.cancel") }));
    await user.click(screen.getByRole("button", { name: t("matterTasks.reopen") }));
    view.unmount();

    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(response({ items: [], total: 0 })));
    const emptyClient = createQueryClient();
    const emptyView = render(
      <QueryClientProvider client={emptyClient}>
        <MatterTasks matterId={4} />
      </QueryClientProvider>,
    );
    expect(await screen.findByText(t("matterTasks.empty"))).toBeInTheDocument();
    emptyView.unmount();

    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(response({}, 400)));
    const errorClient = createQueryClient();
    errorClient.setQueryDefaults(["matter-tasks"], { retry: false });
    render(
      <QueryClientProvider client={errorClient}>
        <MatterTasks matterId={5} />
      </QueryClientProvider>,
    );
    expect(await screen.findByRole("alert")).toHaveTextContent(t("matterTasks.error"));
  });
});
