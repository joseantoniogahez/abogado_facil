"""Schema-validated structured output boundary for AI provider text."""

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, ValidationError

from app.integrations.ai_providers import AiProviderError, AiProviderErrorCode

_VALIDATED_OUTPUT_FACTORY_TOKEN = object()


@dataclass(frozen=True, init=False, repr=False)
class ValidatedAIOutput:
    """Factory-sealed JSON-safe output proven against a named schema version."""

    _data: dict[str, Any]
    schema_version: str

    def __init__(
        self,
        *,
        data: dict[str, Any],
        schema_version: str,
        _factory_token: object,
    ) -> None:
        if _factory_token is not _VALIDATED_OUTPUT_FACTORY_TOKEN:
            raise TypeError("ValidatedAIOutput must be built with validate_ai_output")
        if not schema_version.strip() or len(schema_version) > 50:
            raise ValueError("schema_version must be between 1 and 50 characters")
        object.__setattr__(self, "_data", deepcopy(data))
        object.__setattr__(self, "schema_version", schema_version)

    @property
    def data(self) -> dict[str, Any]:
        """Return a defensive copy so validated state cannot be mutated in place."""
        return deepcopy(self._data)


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
    return ValidatedAIOutput(
        data=data,
        schema_version=schema_version,
        _factory_token=_VALIDATED_OUTPUT_FACTORY_TOKEN,
    )
