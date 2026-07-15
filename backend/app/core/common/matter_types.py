from enum import StrEnum


class MatterType(StrEnum):
    PENSION_ALIMENTICIA = "Pensión alimenticia"
    DIVORCIO_BASICO = "Divorcio básico"
    DESPIDO_LABORAL_INICIAL = "Despido / asunto laboral inicial"
    COBRO_DE_DEUDA = "Cobro de deuda"
    CONVENIO_DE_PAGO = "Convenio de pago"
    ARRENDAMIENTO = "Arrendamiento"
    SUCESORIO_BASICO = "Sucesorio básico"
    OTRO = "Otro"


MATTER_TYPE_CHECKLISTS: dict[MatterType, tuple[str, ...]] = {
    MatterType.PENSION_ALIMENTICIA: (
        "Actas de nacimiento",
        "Comprobantes de ingresos",
        "Comprobantes de gastos",
        "Domicilio de la contraparte",
    ),
    MatterType.DIVORCIO_BASICO: (
        "Acta de matrimonio",
        "Actas de nacimiento de hijos",
        "Identificaciones oficiales",
        "Comprobantes de domicilio",
    ),
    MatterType.DESPIDO_LABORAL_INICIAL: (
        "Contrato de trabajo",
        "Recibos de nómina",
        "Aviso de despido",
        "Identificación oficial",
    ),
    MatterType.COBRO_DE_DEUDA: (
        "Contrato o pagaré",
        "Comprobantes de entrega",
        "Estado de cuenta",
        "Datos de localización del deudor",
    ),
    MatterType.CONVENIO_DE_PAGO: (
        "Documento que acredita la deuda",
        "Identificaciones oficiales",
        "Propuesta de pagos",
        "Datos de contacto",
    ),
    MatterType.ARRENDAMIENTO: (
        "Contrato de arrendamiento",
        "Recibos de renta",
        "Inventario del inmueble",
        "Comunicaciones entre las partes",
    ),
    MatterType.SUCESORIO_BASICO: (
        "Acta de defunción",
        "Testamento, si existe",
        "Actas de nacimiento y matrimonio",
        "Documentos de bienes",
    ),
    MatterType.OTRO: (),
}
