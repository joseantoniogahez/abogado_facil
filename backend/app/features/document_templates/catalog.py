from dataclasses import dataclass
from typing import Literal

DocumentTemplateKey = Literal[
    "payment_demand",
    "payment_agreement",
    "document_request",
    "internal_matter_summary",
]
DocumentTemplateFieldType = Literal["text", "long_text", "date", "money"]


@dataclass(frozen=True)
class DocumentTemplateField:
    key: str
    label: str
    field_type: DocumentTemplateFieldType
    required: bool = True


@dataclass(frozen=True)
class DocumentTemplate:
    key: DocumentTemplateKey
    name: str
    description: str
    purpose: str
    fields: tuple[DocumentTemplateField, ...]


DOCUMENT_TEMPLATES: tuple[DocumentTemplate, ...] = (
    DocumentTemplate(
        key="payment_demand",
        name="Requerimiento de pago",
        description="Carta simple para solicitar el pago de una cantidad vencida.",
        purpose="Comunicar el adeudo, su fecha de vencimiento y un plazo para responder.",
        fields=(
            DocumentTemplateField("creditor_name", "Nombre de la persona acreedora", "text"),
            DocumentTemplateField("debtor_name", "Nombre de la persona deudora", "text"),
            DocumentTemplateField("amount", "Monto reclamado", "money"),
            DocumentTemplateField("due_date", "Fecha de vencimiento", "date"),
            DocumentTemplateField("payment_deadline", "Plazo propuesto para pagar", "date"),
            DocumentTemplateField("background", "Origen y antecedentes del adeudo", "long_text"),
        ),
    ),
    DocumentTemplate(
        key="payment_agreement",
        name="Convenio de pago simple",
        description="Acuerdo básico para documentar un reconocimiento y calendario de pago.",
        purpose="Dejar por escrito monto, participantes y forma de pago acordada.",
        fields=(
            DocumentTemplateField("creditor_name", "Nombre de la persona acreedora", "text"),
            DocumentTemplateField("debtor_name", "Nombre de la persona deudora", "text"),
            DocumentTemplateField("amount", "Monto acordado", "money"),
            DocumentTemplateField("payment_schedule", "Fechas y montos de pago", "long_text"),
            DocumentTemplateField("start_date", "Fecha de inicio", "date"),
            DocumentTemplateField("additional_terms", "Condiciones adicionales", "long_text", False),
        ),
    ),
    DocumentTemplate(
        key="document_request",
        name="Solicitud de documentos",
        description="Mensaje formal para pedir al cliente documentos pendientes.",
        purpose="Precisar qué información se necesita y cuándo debe entregarse.",
        fields=(
            DocumentTemplateField("recipient_name", "Nombre de la persona destinataria", "text"),
            DocumentTemplateField("matter_reference", "Referencia del asunto", "text"),
            DocumentTemplateField("requested_documents", "Documentos solicitados", "long_text"),
            DocumentTemplateField("delivery_deadline", "Fecha límite de entrega", "date"),
            DocumentTemplateField("delivery_method", "Medio de entrega", "text", False),
        ),
    ),
    DocumentTemplate(
        key="internal_matter_summary",
        name="Resumen interno del asunto",
        description="Ficha de trabajo para concentrar el estado actual de un expediente.",
        purpose="Facilitar la revisión interna sin producir un documento para terceros.",
        fields=(
            DocumentTemplateField("matter_title", "Nombre del asunto", "text"),
            DocumentTemplateField("parties", "Partes involucradas", "long_text"),
            DocumentTemplateField("background", "Antecedentes relevantes", "long_text"),
            DocumentTemplateField("current_status", "Estado actual", "long_text"),
            DocumentTemplateField("next_steps", "Próximos pasos", "long_text"),
            DocumentTemplateField("important_dates", "Fechas importantes", "long_text", False),
        ),
    ),
)


def document_template_for(key: str) -> DocumentTemplate | None:
    return next((template for template in DOCUMENT_TEMPLATES if template.key == key), None)
