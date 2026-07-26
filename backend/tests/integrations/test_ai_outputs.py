from typing import Any, cast

import pytest
from pydantic import BaseModel, ConfigDict, RootModel

from app.integrations.ai_outputs import ValidatedAIOutput, validate_ai_output
from app.integrations.ai_providers import AiProviderError, AiProviderErrorCode


class QuestionsOutput(BaseModel):
    questions: list[str]
    confidence: float

    model_config = ConfigDict(extra="forbid")


class ListOutput(RootModel[list[str]]):
    pass


def test_valid_output_is_normalized_versioned_and_copied() -> None:
    output = validate_ai_output(
        '{"questions":["First"],"confidence":1}',
        schema=QuestionsOutput,
        schema_version="questions-v1",
    )

    assert output.data == {"questions": ["First"], "confidence": 1.0}
    returned_data = output.data
    returned_data["questions"].append("Mutated")
    returned_data["unvalidated"] = object()
    assert output.data == {"questions": ["First"], "confidence": 1.0}
    assert "First" not in repr(output)


def test_validated_output_cannot_be_constructed_directly() -> None:
    with pytest.raises(TypeError, match="factory_token"):
        cast(Any, ValidatedAIOutput)(
            data={"questions": ["Bypass"], "confidence": 0.5},
            schema_version="questions-v1",
        )

    with pytest.raises(TypeError, match="validate_ai_output"):
        ValidatedAIOutput(
            data={"questions": ["Bypass"], "confidence": 0.5},
            schema_version="questions-v1",
            _factory_token=object(),
        )


@pytest.mark.parametrize(
    "raw_output",
    (
        "not-json private response",
        '{"questions":"wrong","confidence":1}',
        '{"questions":[],"confidence":1,"prompt":"private"}',
        "[]",
    ),
)
def test_invalid_output_uses_safe_non_retryable_error(raw_output: str) -> None:
    with pytest.raises(AiProviderError) as captured:
        validate_ai_output(
            raw_output,
            schema=QuestionsOutput,
            schema_version="questions-v1",
        )

    assert captured.value.code is AiProviderErrorCode.INVALID_RESPONSE
    assert captured.value.retryable is False
    assert raw_output not in str(captured.value)


def test_root_list_is_rejected_even_when_its_schema_accepts_it() -> None:
    with pytest.raises(AiProviderError) as captured:
        validate_ai_output('["not","an","object"]', schema=ListOutput, schema_version="list-v1")

    assert captured.value.code is AiProviderErrorCode.INVALID_RESPONSE


@pytest.mark.parametrize("schema_version", ("", " ", "v" * 51))
def test_validated_output_rejects_invalid_schema_version(schema_version: str) -> None:
    with pytest.raises(ValueError, match="schema_version"):
        validate_ai_output(
            '{"questions":[],"confidence":1}',
            schema=QuestionsOutput,
            schema_version=schema_version,
        )
