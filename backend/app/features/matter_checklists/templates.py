import re
import unicodedata

from app.core.common.matter_types import MATTER_TYPE_CHECKLISTS, MatterType


def normalize_matter_type(value: str) -> str:
    ascii_value = "".join(c for c in unicodedata.normalize("NFD", value.lower()) if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", ascii_value).strip()


def checklist_for(value: str) -> tuple[str, ...]:
    try:
        return MATTER_TYPE_CHECKLISTS[MatterType(value)]
    except ValueError:
        legacy_templates = {
            normalize_matter_type(matter_type.value): checklist
            for matter_type, checklist in MATTER_TYPE_CHECKLISTS.items()
        }
        return legacy_templates.get(normalize_matter_type(value), ())
