import { expectBooleanField, expectRecord, expectStringField } from "@/shared/api/contracts";

export type DocumentTemplateKey
  = | "payment_demand"
    | "payment_agreement"
    | "document_request"
    | "internal_matter_summary";
export type DocumentTemplateFieldType = "text" | "long_text" | "date" | "money";

export interface DocumentTemplateField {
  key: string;
  label: string;
  field_type: DocumentTemplateFieldType;
  required: boolean;
}

export interface DocumentTemplate {
  key: DocumentTemplateKey;
  name: string;
  description: string;
  purpose: string;
  fields: DocumentTemplateField[];
}

export interface DocumentTemplateCatalog {
  items: DocumentTemplate[];
  generation_available: false;
}

const TEMPLATE_KEYS: readonly DocumentTemplateKey[] = [
  "payment_demand",
  "payment_agreement",
  "document_request",
  "internal_matter_summary",
];
const FIELD_TYPES: readonly DocumentTemplateFieldType[] = ["text", "long_text", "date", "money"];

const parseLiteral = <Value extends string>(value: string, allowed: readonly Value[], context: string): Value => {
  if (!allowed.includes(value as Value)) throw new Error(`${context}: unsupported value`);
  return value as Value;
};

const parseField = (payload: unknown): DocumentTemplateField => {
  const record = expectRecord(payload, "DocumentTemplateField");
  return {
    key: expectStringField(record, "key", "DocumentTemplateField", { minLength: 1 }),
    label: expectStringField(record, "label", "DocumentTemplateField", { minLength: 1 }),
    field_type: parseLiteral(
      expectStringField(record, "field_type", "DocumentTemplateField"),
      FIELD_TYPES,
      "DocumentTemplateField.field_type",
    ),
    required: expectBooleanField(record, "required", "DocumentTemplateField"),
  };
};

const parseTemplate = (payload: unknown): DocumentTemplate => {
  const record = expectRecord(payload, "DocumentTemplate");
  if (!Array.isArray(record.fields)) throw new Error("DocumentTemplate: fields must be an array");
  return {
    key: parseLiteral(
      expectStringField(record, "key", "DocumentTemplate"),
      TEMPLATE_KEYS,
      "DocumentTemplate.key",
    ),
    name: expectStringField(record, "name", "DocumentTemplate", { minLength: 1 }),
    description: expectStringField(record, "description", "DocumentTemplate", { minLength: 1 }),
    purpose: expectStringField(record, "purpose", "DocumentTemplate", { minLength: 1 }),
    fields: record.fields.map(parseField),
  };
};

export const parseDocumentTemplateCatalog = (payload: unknown): DocumentTemplateCatalog => {
  const record = expectRecord(payload, "DocumentTemplateCatalog");
  if (!Array.isArray(record.items)) throw new Error("DocumentTemplateCatalog: items must be an array");
  if (expectBooleanField(record, "generation_available", "DocumentTemplateCatalog")) {
    throw new Error("DocumentTemplateCatalog: generation is not available in this release");
  }
  return { items: record.items.map(parseTemplate), generation_available: false };
};
