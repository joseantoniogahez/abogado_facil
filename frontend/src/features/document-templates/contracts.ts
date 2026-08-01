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
  generation_available: true;
}

export type DraftProvider = "openai" | "gemini";

export interface DocumentDraftInput {
  template_key: DocumentTemplateKey;
  fields: Record<string, string>;
  provider: DraftProvider;
  model: string;
}

export interface DocumentDraftPreview {
  template_key: DocumentTemplateKey;
  provider: DraftProvider;
  model: string;
  included_fields: string[];
  character_count: number;
  estimated_max_output_tokens: number;
  cost_notice: string;
  confirmation_token: string;
}

export interface DocumentDraft {
  template_key: DocumentTemplateKey;
  content: string;
  provider: DraftProvider;
  model: string;
  execution_id: string;
  status: "draft";
  requires_professional_review: true;
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
  if (!expectBooleanField(record, "generation_available", "DocumentTemplateCatalog")) {
    throw new Error("DocumentTemplateCatalog: generation must be available");
  }
  return { items: record.items.map(parseTemplate), generation_available: true };
};

const parseProvider = (value: string): DraftProvider =>
  parseLiteral(value, ["openai", "gemini"] as const, "DocumentDraft.provider");

const parseStringArray = (value: unknown, context: string): string[] => {
  if (!Array.isArray(value) || value.some(item => typeof item !== "string")) {
    throw new Error(`${context}: expected string array`);
  }
  return value as string[];
};

export const parseDocumentDraftPreview = (payload: unknown): DocumentDraftPreview => {
  const record = expectRecord(payload, "DocumentDraftPreview");
  return {
    template_key: parseLiteral(expectStringField(record, "template_key", "DocumentDraftPreview"), TEMPLATE_KEYS, "DocumentDraftPreview.template_key"),
    provider: parseProvider(expectStringField(record, "provider", "DocumentDraftPreview")),
    model: expectStringField(record, "model", "DocumentDraftPreview"),
    included_fields: parseStringArray(record.included_fields, "DocumentDraftPreview.included_fields"),
    character_count: Number(record.character_count),
    estimated_max_output_tokens: Number(record.estimated_max_output_tokens),
    cost_notice: expectStringField(record, "cost_notice", "DocumentDraftPreview"),
    confirmation_token: expectStringField(record, "confirmation_token", "DocumentDraftPreview"),
  };
};

export const parseDocumentDraft = (payload: unknown): DocumentDraft => {
  const record = expectRecord(payload, "DocumentDraft");
  if (record.status !== "draft" || record.requires_professional_review !== true) {
    throw new Error("DocumentDraft: invalid review status");
  }
  return {
    template_key: parseLiteral(expectStringField(record, "template_key", "DocumentDraft"), TEMPLATE_KEYS, "DocumentDraft.template_key"),
    content: expectStringField(record, "content", "DocumentDraft", { minLength: 1 }),
    provider: parseProvider(expectStringField(record, "provider", "DocumentDraft")),
    model: expectStringField(record, "model", "DocumentDraft"),
    execution_id: expectStringField(record, "execution_id", "DocumentDraft"),
    status: "draft",
    requires_professional_review: true,
  };
};
