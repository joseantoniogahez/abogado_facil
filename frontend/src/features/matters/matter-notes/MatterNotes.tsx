import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { type FormEvent, useState } from "react";

import { t } from "@/shared/i18n/ui-text";
import {
  ACCENT_ACTION_CLASS_NAME,
  DANGER_ACTION_CLASS_NAME,
  SECONDARY_ACTION_CLASS_NAME,
} from "@/shared/ui/actionStyles";

import {
  createMatterNote,
  deleteMatterNote,
  matterNotesQueryKey,
  matterNotesQueryOptions,
  updateMatterNote,
} from "./api";
import type { MatterNoteRecord } from "./contracts";

const Note = ({ matterId, note }: { matterId: number; note: MatterNoteRecord }) => {
  const queryClient = useQueryClient();
  const [editing, setEditing] = useState(false);
  const [content, setContent] = useState(note.content);
  const refresh = () => queryClient.invalidateQueries({ queryKey: matterNotesQueryKey(matterId) });
  const update = useMutation({
    mutationFn: (payload: { content?: string; is_relevant?: boolean }) =>
      updateMatterNote(matterId, note.id, payload),
    onSuccess: async () => {
      await refresh();
      setEditing(false);
    },
  });
  const remove = useMutation({
    mutationFn: () => deleteMatterNote(matterId, note.id),
    onSuccess: async () => refresh(),
  });

  const submitEdit = (event: FormEvent) => {
    event.preventDefault();
    const normalized = content.trim();
    if (normalized) update.mutate({ content: normalized });
  };

  const confirmDelete = () => {
    if (window.confirm(t("matterNotes.deleteConfirm"))) remove.mutate();
  };

  return (
    <li className="rounded-xl border p-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <span className="font-semibold">
          {note.is_relevant ? t("matterNotes.relevant") : t("matterNotes.standard")}
        </span>
        <time dateTime={note.updated_at}>{new Date(note.updated_at).toLocaleString()}</time>
      </div>
      {editing
        ? (
            <form className="mt-3 grid gap-2" onSubmit={submitEdit}>
              <label>
                {t("matterNotes.content")}
                <textarea
                  className="mt-1 min-h-28 w-full rounded-xl border p-3"
                  maxLength={20000}
                  required
                  value={content}
                  onChange={event => setContent(event.target.value)}
                />
              </label>
              <div className="flex gap-2">
                <button className={ACCENT_ACTION_CLASS_NAME} disabled={update.isPending} type="submit">
                  {t("matterNotes.save")}
                </button>
                <button
                  className={SECONDARY_ACTION_CLASS_NAME}
                  onClick={() => {
                    setContent(note.content);
                    setEditing(false);
                  }}
                  type="button"
                >
                  {t("matterNotes.cancel")}
                </button>
              </div>
            </form>
          )
        : (
            <p className="mt-3 whitespace-pre-wrap break-words">{note.content}</p>
          )}
      <div className="mt-3 flex flex-wrap gap-3">
        <button
          className={SECONDARY_ACTION_CLASS_NAME}
          disabled={update.isPending}
          onClick={() => update.mutate({ is_relevant: !note.is_relevant })}
          type="button"
        >
          {note.is_relevant ? t("matterNotes.unmark") : t("matterNotes.mark")}
        </button>
        <button
          className={SECONDARY_ACTION_CLASS_NAME}
          onClick={() => setEditing(true)}
          type="button"
        >
          {t("matterNotes.edit")}
        </button>
        <button
          className={DANGER_ACTION_CLASS_NAME}
          disabled={remove.isPending}
          onClick={confirmDelete}
          type="button"
        >
          {t("matterNotes.delete")}
        </button>
      </div>
      {update.isError || remove.isError
        ? (
            <p role="alert">{t("matterNotes.mutationError")}</p>
          )
        : null}
    </li>
  );
};

export const MatterNotes = ({ matterId }: { matterId: number }) => {
  const queryClient = useQueryClient();
  const [content, setContent] = useState("");
  const query = useQuery(matterNotesQueryOptions(matterId));
  const create = useMutation({
    mutationFn: () => createMatterNote(matterId, content.trim()),
    onSuccess: async () => {
      setContent("");
      await queryClient.invalidateQueries({ queryKey: matterNotesQueryKey(matterId) });
    },
  });
  const submit = (event: FormEvent) => {
    event.preventDefault();
    if (content.trim()) create.mutate();
  };

  return (
    <section aria-labelledby="matter-notes-title" className="mt-10">
      <h2 className="text-2xl font-semibold" id="matter-notes-title">
        {t("matterNotes.title")}
      </h2>
      <form className="mt-4 grid gap-3" onSubmit={submit}>
        <label>
          {t("matterNotes.content")}
          <textarea
            className="mt-1 min-h-28 w-full rounded-xl border p-3"
            maxLength={20000}
            required
            value={content}
            onChange={event => setContent(event.target.value)}
          />
        </label>
        <button
          className={`${ACCENT_ACTION_CLASS_NAME} w-fit`}
          disabled={create.isPending}
          type="submit"
        >
          {create.isPending ? t("matterNotes.saving") : t("matterNotes.add")}
        </button>
        {create.isError ? <p role="alert">{t("matterNotes.mutationError")}</p> : null}
      </form>
      {query.isPending ? <p className="mt-4">{t("matterNotes.loading")}</p> : null}
      {query.isError
        ? (
            <div className="mt-4" role="alert">
              <p>{t("matterNotes.error")}</p>
              <button
                className={SECONDARY_ACTION_CLASS_NAME}
                onClick={() => void query.refetch()}
                type="button"
              >
                {t("matterNotes.retry")}
              </button>
            </div>
          )
        : null}
      {query.data && !query.data.items.length
        ? (
            <p className="mt-4">{t("matterNotes.empty")}</p>
          )
        : null}
      {query.data?.items.length
        ? (
            <ul className="mt-4 grid gap-3">
              {query.data.items.map(note => (
                <Note key={note.id} matterId={matterId} note={note} />
              ))}
            </ul>
          )
        : null}
    </section>
  );
};
