import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { type SyntheticEvent, useRef, useState } from "react";

import { t } from "@/shared/i18n/ui-text";
import {
  ACCENT_ACTION_CLASS_NAME,
  DANGER_ACTION_CLASS_NAME,
  SECONDARY_ACTION_CLASS_NAME,
} from "@/shared/ui/actionStyles";

import {
  deleteMatterDocument,
  downloadMatterDocument,
  matterDocumentsQueryKey,
  matterDocumentsQueryOptions,
  uploadMatterDocument,
} from "./api";
import { DOCUMENT_TYPES, type DocumentType, type MatterDocumentRecord } from "./contracts";

const MAX_SIZE_BYTES = 10 * 1024 * 1024;
const ACCEPTED_EXTENSIONS = [".pdf", ".docx", ".txt"];
const formatSize = (bytes: number) =>
  new Intl.NumberFormat("es-MX", {
    style: "unit",
    unit: "megabyte",
    maximumFractionDigits: 2,
  }).format(bytes / 1024 / 1024);
const filenameFromDisposition = (value: string | null, fallback: string) => {
  const encoded = value?.match(/filename\*=UTF-8''([^;]+)/i)?.[1];
  if (!encoded) return fallback;
  try {
    return decodeURIComponent(encoded);
  }
  catch {
    return fallback;
  }
};

const DocumentRow = ({
  matterId,
  document,
}: {
  matterId: number;
  document: MatterDocumentRecord;
}) => {
  const queryClient = useQueryClient();
  const [actionError, setActionError] = useState(false);
  const download = useMutation({
    mutationFn: () => downloadMatterDocument(matterId, document.id),
    onSuccess: ({ blob, contentDisposition }) => {
      const url = URL.createObjectURL(blob);
      const anchor = window.document.createElement("a");
      anchor.href = url;
      anchor.download = filenameFromDisposition(contentDisposition, document.original_filename);
      anchor.click();
      URL.revokeObjectURL(url);
      setActionError(false);
    },
    onError: () => setActionError(true),
  });
  const remove = useMutation({
    mutationFn: () => deleteMatterDocument(matterId, document.id),
    onSuccess: async () => {
      setActionError(false);
      await queryClient.invalidateQueries({ queryKey: matterDocumentsQueryKey(matterId) });
    },
    onError: () => setActionError(true),
  });
  return (
    <li className="rounded-xl border p-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="break-all font-semibold">{document.original_filename}</p>
          <p>
            {t(`matterDocuments.type.${document.document_type}` as const)}
            {" "}
            ·
            {" "}
            {formatSize(document.size_bytes)}
          </p>
          <time dateTime={document.created_at}>
            {new Date(document.created_at).toLocaleString("es-MX")}
          </time>
        </div>
        <div className="flex flex-wrap gap-3">
          <button
            className={SECONDARY_ACTION_CLASS_NAME}
            disabled={download.isPending}
            onClick={() => download.mutate()}
            type="button"
          >
            {download.isPending ? t("matterDocuments.downloading") : t("matterDocuments.download")}
          </button>
          <button
            className={DANGER_ACTION_CLASS_NAME}
            disabled={remove.isPending}
            onClick={() => {
              if (window.confirm(t("matterDocuments.deleteConfirm"))) remove.mutate();
            }}
            type="button"
          >
            {remove.isPending ? t("matterDocuments.deleting") : t("matterDocuments.delete")}
          </button>
        </div>
      </div>
      {actionError ? <p role="alert">{t("matterDocuments.actionError")}</p> : null}
    </li>
  );
};

export const MatterDocuments = ({ matterId }: { matterId: number }) => {
  const queryClient = useQueryClient();
  const fileRef = useRef<HTMLInputElement>(null);
  const [documentType, setDocumentType] = useState<DocumentType>("other");
  const [file, setFile] = useState<File | null>(null);
  const [validation, setValidation] = useState<string | null>(null);
  const query = useQuery(matterDocumentsQueryOptions(matterId));
  const upload = useMutation({
    mutationFn: () => uploadMatterDocument(matterId, documentType, file!),
    onSuccess: async () => {
      setFile(null);
      setValidation(null);
      if (fileRef.current) fileRef.current.value = "";
      await queryClient.invalidateQueries({ queryKey: matterDocumentsQueryKey(matterId) });
    },
  });
  const submit = (event: SyntheticEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!file) {
      setValidation(t("matterDocuments.validation.required"));
      return;
    }
    const extension = file.name.slice(file.name.lastIndexOf(".")).toLowerCase();
    if (!ACCEPTED_EXTENSIONS.includes(extension)) {
      setValidation(t("matterDocuments.validation.format"));
      return;
    }
    if (file.size > MAX_SIZE_BYTES) {
      setValidation(t("matterDocuments.validation.size"));
      return;
    }
    setValidation(null);
    upload.mutate();
  };
  return (
    <section aria-labelledby="matter-documents-title" className="mt-10">
      <h2 className="text-2xl font-semibold" id="matter-documents-title">
        {t("matterDocuments.title")}
      </h2>
      <p className="mt-1">{t("matterDocuments.help")}</p>
      <form className="mt-4 grid gap-3 rounded-xl border p-4" onSubmit={submit}>
        <label>
          {t("matterDocuments.type")}
          <select
            className="mt-1 w-full rounded-xl border p-3"
            onChange={event => setDocumentType(event.target.value as DocumentType)}
            required
            value={documentType}
          >
            {DOCUMENT_TYPES.map(type => (
              <option key={type} value={type}>
                {t(`matterDocuments.type.${type}` as const)}
              </option>
            ))}
          </select>
        </label>
        <label>
          {t("matterDocuments.file")}
          <input
            accept=".pdf,.docx,.txt"
            className="mt-1 block w-full rounded-xl border p-3"
            onChange={event => setFile(event.target.files?.[0] ?? null)}
            ref={fileRef}
            type="file"
          />
        </label>
        {validation ? <p role="alert">{validation}</p> : null}
        {upload.isError ? <p role="alert">{t("matterDocuments.uploadError")}</p> : null}
        <button
          className={`${ACCENT_ACTION_CLASS_NAME} w-fit`}
          disabled={upload.isPending}
          type="submit"
        >
          {upload.isPending ? t("matterDocuments.uploading") : t("matterDocuments.upload")}
        </button>
      </form>
      {query.isPending ? <p className="mt-4">{t("matterDocuments.loading")}</p> : null}
      {query.isError
        ? (
            <div className="mt-4" role="alert">
              <p>{t("matterDocuments.error")}</p>
              <button
                className={`${SECONDARY_ACTION_CLASS_NAME} mt-3`}
                onClick={() => void query.refetch()}
                type="button"
              >
                {t("matterDocuments.retry")}
              </button>
            </div>
          )
        : null}
      {query.data && !query.data.items.length
        ? (
            <p className="mt-4">{t("matterDocuments.empty")}</p>
          )
        : null}
      {query.data?.items.length
        ? (
            <ul className="mt-4 grid gap-3">
              {query.data.items.map(document => (
                <DocumentRow document={document} key={document.id} matterId={matterId} />
              ))}
            </ul>
          )
        : null}
    </section>
  );
};
