"""Schema-validated structured output boundary for AI provider text."""

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, ValidationError

from app.integrations.ai_providers import AiProviderError, AiProviderErrorCode


@dataclass(frozen=True)
class ValidatedAIOutput:
    """JSON-safe output proven against a named schema version."""

    data: dict[str, Any]
    schema_version: str

    def __post_init__(self) -> None:
        if not self.schema_version.strip() or len(self.schema_version) > 50:
            raise ValueError("schema_version must be between 1 and 50 characters")
        object.__setattr__(self, "data", deepcopy(self.data))


def validate_ai_output(
    raw_output: str,
    *,
    schema: type[BaseModel],
    schema_version: str,
) -> ValidatedAIOutput:
    """Parse provider text and return only JSON-safe, schema-validated data."""

    try:
        parsed = schema.model_validate_json(raw_output)
        data = parsed.model_dump(mode="json")
    except (ValidationError, ValueError, TypeError) as exc:
        raise AiProviderError(AiProviderErrorCode.INVALID_RESPONSE) from exc
    if not isinstance(data, dict):
        raise AiProviderError(AiProviderErrorCode.INVALID_RESPONSE)
    return ValidatedAIOutput(data=data, schema_version=schema_version)
