import pytest

from app.core.errors.services import InvalidInputError
from app.integrations.ai_context import (
    MAX_AI_CONTEXT_FIELD_CHARS,
    MinimizedAIContext,
    build_minimized_ai_context,
)


def test_context_contains_only_authorized_necessary_fields() -> None:
    context = build_minimized_ai_context(
        instruction="Create the requested summary",
        source_context={
            "matter_summary": "  Authorized facts  ",
            "private_notes": "must never be sent",
        },
        authorized_fields={"matter_summary", "private_notes"},
        necessary_fields={"matter_summary"},
    )

    rendered = context.render()
    assert context.fields == (("matter_summary", "Authorized facts"),)
    assert "Authorized facts" in rendered
    assert "private_notes" not in rendered
    assert "must never be sent" not in rendered
    assert "Authorized facts" not in repr(context)


@pytest.mark.parametrize(
    "changes",
    [
        {"necessary_fields": {"private_notes"}},
        {"necessary_fields": set()},
        {"authorized_fields": {"missing"}, "necessary_fields": {"missing"}},
        {"authorized_fields": {"Bad-Field"}, "necessary_fields": {"Bad-Field"}},
        {"source_context": {"matter_summary": 123}},
        {"source_context": {"matter_summary": " "}},
        {"source_context": {"matter_summary": "x" * (MAX_AI_CONTEXT_FIELD_CHARS + 1)}},
    ],
)
def test_context_rejects_unauthorized_missing_invalid_or_oversized_data(changes) -> None:
    values = {
        "instruction": "Summarize",
        "source_context": {"matter_summary": "Authorized facts"},
        "authorized_fields": {"matter_summary"},
        "necessary_fields": {"matter_summary"},
    }
    values.update(changes)

    with pytest.raises(InvalidInputError):
        build_minimized_ai_context(**values)


def test_context_rejects_invalid_instruction_and_duplicate_or_excess_fields() -> None:
    with pytest.raises(InvalidInputError):
        build_minimized_ai_context(
            instruction=" ",
            source_context={"matter_summary": "facts"},
            authorized_fields={"matter_summary"},
            necessary_fields={"matter_summary"},
        )

    with pytest.raises(InvalidInputError):
        build_minimized_ai_context(
            instruction="Summarize",
            source_context={"matter_summary": "facts"},
            authorized_fields=["matter_summary", "matter_summary"],
            necessary_fields={"matter_summary"},
        )

    fields = {f"field_{index}": "value" for index in range(21)}
    with pytest.raises(InvalidInputError):
        build_minimized_ai_context(
            instruction="Summarize",
            source_context=fields,
            authorized_fields=set(fields),
            necessary_fields=set(fields),
        )

    large_fields = {f"field_{index}": "x" * MAX_AI_CONTEXT_FIELD_CHARS for index in range(4)}
    with pytest.raises(InvalidInputError, match="exceeds the allowed size"):
        build_minimized_ai_context(
            instruction="Summarize",
            source_context=large_fields,
            authorized_fields=set(large_fields),
            necessary_fields=set(large_fields),
        )


def test_context_cannot_be_constructed_directly() -> None:
    with pytest.raises(TypeError, match="factory_token"):
        MinimizedAIContext(  # type: ignore[call-arg]
            instruction="Bypass",
            fields=(("document", "x" * 100_000),),
        )

    with pytest.raises(TypeError, match="build_minimized_ai_context"):
        MinimizedAIContext(
            instruction="Bypass",
            fields=(("document", "x" * 100_000),),
            _factory_token=object(),
        )
