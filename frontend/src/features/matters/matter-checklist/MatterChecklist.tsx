import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { type FormEvent, useState } from "react";

import { t } from "@/shared/i18n/ui-text";
import { ACCENT_ACTION_CLASS_NAME } from "@/shared/ui/actionStyles";

import {
  createChecklistItem,
  matterChecklistQueryKey,
  matterChecklistQueryOptions,
  updateChecklistItem,
} from "./api";
import type { ChecklistStatus } from "./contracts";

export const MatterChecklist = ({ matterId }: { matterId: number }) => {
  const qc = useQueryClient();
  const [label, setLabel] = useState("");
  const query = useQuery(matterChecklistQueryOptions(matterId));
  const refresh = () => qc.invalidateQueries({ queryKey: matterChecklistQueryKey(matterId) });
  const create = useMutation({
    mutationFn: () => createChecklistItem(matterId, label.trim()),
    onSuccess: async () => {
      setLabel("");
      await refresh();
    },
  });
  const update = useMutation({
    mutationFn: ({ itemId, status }: { itemId: number; status: ChecklistStatus }) =>
      updateChecklistItem(matterId, itemId, status),
    onSuccess: refresh,
  });
  const submit = (event: FormEvent) => {
    event.preventDefault();
    if (label.trim()) create.mutate();
  };
  return (
    <section aria-labelledby="matter-checklist-title" className="mt-10">
      <h2 className="text-2xl font-semibold" id="matter-checklist-title">
        {t("matterChecklist.title")}
      </h2>
      {query.isPending ? <p>{t("matterChecklist.loading")}</p> : null}
      {query.isError ? <p role="alert">{t("matterChecklist.error")}</p> : null}
      {query.data?.items.length
        ? (
            <ul className="mt-4 grid gap-3">
              {query.data.items.map(item => (
                <li className="rounded-xl border p-4" key={item.id}>
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <span>
                      {item.label}
                      {item.is_custom ? ` · ${t("matterChecklist.custom")}` : ""}
                    </span>
                    <label>
                      {t("matterChecklist.statusLabel")}
                      <select
                        aria-label={`${t("matterChecklist.statusLabel")}: ${item.label}`}
                        className="mt-1 rounded-lg border p-2"
                        disabled={update.isPending}
                        value={item.status}
                        onChange={event =>
                          update.mutate({
                            itemId: item.id,
                            status: event.target.value as ChecklistStatus,
                          })}
                      >
                        <option value="pending">{t("matterChecklist.status.pending")}</option>
                        <option value="complete">{t("matterChecklist.status.complete")}</option>
                        <option value="not_applicable">
                          {t("matterChecklist.status.notApplicable")}
                        </option>
                      </select>
                    </label>
                  </div>
                </li>
              ))}
            </ul>
          )
        : query.data
          ? (
              <p>{t("matterChecklist.empty")}</p>
            )
          : null}
      <form className="mt-4 grid gap-3" onSubmit={submit}>
        <label>
          {t("matterChecklist.newLabel")}
          <input
            className="mt-1 w-full rounded-xl border p-3"
            maxLength={500}
            onChange={event => setLabel(event.target.value)}
            required
            value={label}
          />
        </label>
        <button
          className={`${ACCENT_ACTION_CLASS_NAME} w-fit`}
          disabled={create.isPending}
          type="submit"
        >
          {t("matterChecklist.add")}
        </button>
      </form>
      {create.isError || update.isError
        ? (
            <p role="alert">{t("matterChecklist.mutationError")}</p>
          )
        : null}
    </section>
  );
};
