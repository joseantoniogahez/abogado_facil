import re
import unicodedata

CHECKLIST_TEMPLATES: dict[str, tuple[str, ...]] = {
    "pension alimenticia": (
        "Actas de nacimiento",
        "Comprobantes de ingresos",
        "Comprobantes de gastos",
        "Domicilio de la contraparte",
    ),
    "divorcio basico": (
        "Acta de matrimonio",
        "Actas de nacimiento de hijos",
        "Identificaciones oficiales",
        "Comprobantes de domicilio",
    ),
    "despido asunto laboral inicial": (
        "Contrato de trabajo",
        "Recibos de nómina",
        "Aviso de despido",
        "Identificación oficial",
    ),
    "cobro de deuda": (
        "Contrato o pagaré",
        "Comprobantes de entrega",
        "Estado de cuenta",
        "Datos de localización del deudor",
    ),
    "convenio de pago": (
        "Documento que acredita la deuda",
        "Identificaciones oficiales",
        "Propuesta de pagos",
        "Datos de contacto",
    ),
    "arrendamiento": (
        "Contrato de arrendamiento",
        "Recibos de renta",
        "Inventario del inmueble",
        "Comunicaciones entre las partes",
    ),
    "sucesorio basico": (
        "Acta de defunción",
        "Testamento, si existe",
        "Actas de nacimiento y matrimonio",
        "Documentos de bienes",
    ),
}


def normalize_matter_type(value: str) -> str:
    ascii_value = "".join(c for c in unicodedata.normalize("NFD", value.lower()) if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", ascii_value).strip()


def checklist_for(value: str) -> tuple[str, ...]:
    return CHECKLIST_TEMPLATES.get(normalize_matter_type(value), ())
