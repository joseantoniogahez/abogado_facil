import { expectNumberField, expectRecord, expectStringField } from "@/shared/api/contracts";

export const DOCUMENT_TYPES = [
  "identification", "record", "contract", "receipt", "proof", "filing", "notification", "evidence", "other",
] as const;
export type DocumentType = (typeof DOCUMENT_TYPES)[number];

export interface MatterDocumentRecord {
  id: string;
  matter_id: number;
  original_filename: string;
  document_type: DocumentType;
  media_type: string;
  size_bytes: number;
  created_at: string;
}

export const parseMatterDocument = (payload: unknown): MatterDocumentRecord => {
  const record = expectRecord(payload, "MatterDocument");
  const documentType = expectStringField(record, "document_type", "MatterDocument");
  if (!DOCUMENT_TYPES.includes(documentType as DocumentType)) throw new Error("MatterDocument: invalid document_type");
  return {
    id: expectStringField(record, "id", "MatterDocument", { minLength: 1 }),
    matter_id: expectNumberField(record, "matter_id", "MatterDocument"),
    original_filename: expectStringField(record, "original_filename", "MatterDocument", { minLength: 1 }),
    document_type: documentType as DocumentType,
    media_type: expectStringField(record, "media_type", "MatterDocument", { minLength: 1 }),
    size_bytes: expectNumberField(record, "size_bytes", "MatterDocument"),
    created_at: expectStringField(record, "created_at", "MatterDocument", { minLength: 1 }),
  };
};

export const parseMatterDocumentList = (payload: unknown) => {
  const record = expectRecord(payload, "MatterDocumentList");
  if (!Array.isArray(record.items)) throw new Error("MatterDocumentList: invalid items");
  return { items: record.items.map(parseMatterDocument), total: expectNumberField(record, "total", "MatterDocumentList") };
};
