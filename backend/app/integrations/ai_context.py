"""Allowlist-based construction of minimized AI provider context."""

import re
from collections.abc import Collection, Mapping
from dataclasses import dataclass

from app.core.errors.services import InvalidInputError

MAX_AI_INSTRUCTION_CHARS = 4_000
MAX_AI_CONTEXT_FIELD_CHARS = 20_000
MAX_AI_CONTEXT_CHARS = 60_000
MAX_AI_CONTEXT_FIELDS = 20
_FIELD_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]{0,49}$")
_CONTEXT_FACTORY_TOKEN = object()


@dataclass(frozen=True, init=False, repr=False)
class MinimizedAIContext:
    """Factory-sealed instruction and exact authorized fields selected for a call."""

    instruction: str
    fields: tuple[tuple[str, str], ...]

    def __init__(
        self,
        *,
        instruction: str,
        fields: tuple[tuple[str, str], ...],
        _factory_token: object,
    ) -> None:
        if _factory_token is not _CONTEXT_FACTORY_TOKEN:
            raise TypeError("MinimizedAIContext must be built with build_minimized_ai_context")
        object.__setattr__(self, "instruction", instruction)
        object.__setattr__(self, "fields", fields)

    def render(self) -> str:
        parts = [self.instruction, "", "<authorized_context>"]
        parts.extend(f"<{name}>\n{value}\n</{name}>" for name, value in self.fields)
        parts.append("</authorized_context>")
        return "\n".join(parts)


def _clean_text(value: str, *, label: str, max_chars: int) -> str:
    if not isinstance(value, str):
        raise InvalidInputError(f"{label} must be text")
    cleaned = value.strip()
    if not cleaned:
        raise InvalidInputError(f"{label} cannot be empty")
    if len(cleaned) > max_chars:
        raise InvalidInputError(f"{label} exceeds the allowed size")
    return cleaned


def _validate_field_names(names: Collection[str], *, label: str) -> set[str]:
    if len(names) > MAX_AI_CONTEXT_FIELDS:
        raise InvalidInputError(f"{label} contains too many fields")
    normalized = set(names)
    if len(normalized) != len(names):
        raise InvalidInputError(f"{label} contains duplicate fields")
    if any(not isinstance(name, str) or _FIELD_NAME_PATTERN.fullmatch(name) is None for name in normalized):
        raise InvalidInputError(f"{label} contains an invalid field name")
    return normalized


def build_minimized_ai_context(
    *,
    instruction: str,
    source_context: Mapping[str, str],
    authorized_fields: Collection[str],
    necessary_fields: Collection[str],
) -> MinimizedAIContext:
    """Select only explicitly necessary fields after verifying their authorization."""
    clean_instruction = _clean_text(
        instruction,
        label="AI instruction",
        max_chars=MAX_AI_INSTRUCTION_CHARS,
    )
    authorized = _validate_field_names(authorized_fields, label="authorized_fields")
    necessary = _validate_field_names(necessary_fields, label="necessary_fields")
    if not necessary:
        raise InvalidInputError("necessary_fields cannot be empty")
    if not necessary <= authorized:
        raise InvalidInputError("necessary_fields contains unauthorized fields")
    if not necessary <= source_context.keys():
        raise InvalidInputError("source_context is missing necessary fields")

    selected = tuple(
        (
            name,
            _clean_text(
                source_context[name],
                label=f"AI context field {name}",
                max_chars=MAX_AI_CONTEXT_FIELD_CHARS,
            ),
        )
        for name in sorted(necessary)
    )
    context = MinimizedAIContext(
        instruction=clean_instruction,
        fields=selected,
        _factory_token=_CONTEXT_FACTORY_TOKEN,
    )
    if len(context.render()) > MAX_AI_CONTEXT_CHARS:
        raise InvalidInputError("AI context exceeds the allowed size")
    return context
