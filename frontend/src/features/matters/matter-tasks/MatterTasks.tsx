import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { type FormEvent, useState } from "react";

import { t } from "@/shared/i18n/ui-text";
import { ACCENT_ACTION_CLASS_NAME, SECONDARY_ACTION_CLASS_NAME } from "@/shared/ui/actionStyles";

import { createMatterTask, matterTasksQueryKey, matterTasksQueryOptions, updateMatterTask } from "./api";
import type { MatterTask } from "./contracts";

const today = () => new Date().toISOString().slice(0, 10);

export const MatterTasks = ({ matterId }: { matterId: number }) => {
  const qc = useQueryClient();
  const query = useQuery(matterTasksQueryOptions(matterId));
  const [title, setTitle] = useState("");
  const [dueDate, setDueDate] = useState(today());
  const [editing, setEditing] = useState<MatterTask | null>(null);
  const refresh = () => Promise.all([
    qc.invalidateQueries({ queryKey: matterTasksQueryKey(matterId) }),
    qc.invalidateQueries({ queryKey: ["dashboard"] }),
  ]);
  const create = useMutation({
    mutationFn: () => createMatterTask(matterId, title.trim(), dueDate),
    onSuccess: async () => {
      setTitle("");
      await refresh();
    },
  });
  const update = useMutation({
    mutationFn: ({ taskId, payload }: { taskId: number; payload: Parameters<typeof updateMatterTask>[2] }) =>
      updateMatterTask(matterId, taskId, payload),
    onSuccess: async () => {
      setEditing(null);
      await refresh();
    },
  });
  const submit = (event: FormEvent) => {
    event.preventDefault();
    if (title.trim() && dueDate) create.mutate();
  };
  return (
    <section aria-labelledby="matter-tasks-title" className="mt-10">
      <h2 className="text-2xl font-semibold" id="matter-tasks-title">{t("matterTasks.title")}</h2>
      {query.isPending ? <p>{t("matterTasks.loading")}</p> : null}
      {query.isError ? <p role="alert">{t("matterTasks.error")}</p> : null}
      {query.data?.items.length
        ? (
            <ul className="mt-4 grid gap-3">
              {query.data.items.map(task => (
                <li className="rounded-xl border p-4" key={task.id}>
                  {editing?.id === task.id
                    ? (
                        <form
                          className="grid gap-3"
                          onSubmit={(event) => {
                            event.preventDefault();
                            update.mutate({
                              taskId: task.id,
                              payload: { title: editing.title.trim(), due_date: editing.due_date },
                            });
                          }}
                        >
                          <label>
                            {t("matterTasks.task")}
                            <input className="mt-1 w-full rounded-xl border p-3" value={editing.title} onChange={event => setEditing({ ...editing, title: event.target.value })} />
                          </label>
                          <label>
                            {t("matterTasks.dueDate")}
                            <input className="mt-1 rounded-xl border p-3" type="date" value={editing.due_date} onChange={event => setEditing({ ...editing, due_date: event.target.value })} />
                          </label>
                          <div className="flex gap-2">
                            <button className={ACCENT_ACTION_CLASS_NAME}>{t("matterTasks.save")}</button>
                            <button className={SECONDARY_ACTION_CLASS_NAME} onClick={() => setEditing(null)} type="button">{t("matterTasks.cancel")}</button>
                          </div>
                        </form>
                      )
                    : (
                        <div className="flex flex-wrap items-center justify-between gap-3">
                          <div>
                            <p className={task.completed ? "line-through" : "font-medium"}>{task.title}</p>
                            <p>
                              {t("matterTasks.dueDate")}
                              :
                              {" "}
                              {task.due_date}
                            </p>
                            {!task.completed && task.due_date < today() ? <p>{t("matterTasks.overdue")}</p> : null}
                          </div>
                          <div className="flex flex-wrap gap-2">
                            <button className={SECONDARY_ACTION_CLASS_NAME} onClick={() => setEditing(task)} type="button">{t("matterTasks.edit")}</button>
                            <button
                              className={task.completed ? SECONDARY_ACTION_CLASS_NAME : ACCENT_ACTION_CLASS_NAME}
                              disabled={update.isPending}
                              onClick={() => update.mutate({ taskId: task.id, payload: { completed: !task.completed } })}
                              type="button"
                            >
                              {task.completed ? t("matterTasks.reopen") : t("matterTasks.complete")}
                            </button>
                          </div>
                        </div>
                      )}
                </li>
              ))}
            </ul>
          )
        : query.data ? <p>{t("matterTasks.empty")}</p> : null}
      <form className="mt-4 grid gap-3" onSubmit={submit}>
        <label>
          {t("matterTasks.task")}
          <input className="mt-1 w-full rounded-xl border p-3" maxLength={500} required value={title} onChange={event => setTitle(event.target.value)} />
        </label>
        <label>
          {t("matterTasks.dueDate")}
          <input className="mt-1 rounded-xl border p-3" required type="date" value={dueDate} onChange={event => setDueDate(event.target.value)} />
        </label>
        <button className={`${ACCENT_ACTION_CLASS_NAME} w-fit`} disabled={create.isPending}>{t("matterTasks.add")}</button>
      </form>
      {create.isError || update.isError ? <p role="alert">{t("matterTasks.mutationError")}</p> : null}
    </section>
  );
};
