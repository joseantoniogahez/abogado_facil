from datetime import datetime
from typing import Literal

from pydantic import Field

from app.core.common.schema import ApiSchema

AiProvider = Literal["openai", "gemini"]


class SaveAiCredentialRequest(ApiSchema):
    api_key: str = Field(min_length=10, max_length=4096)


class AiCredentialResponse(ApiSchema):
    provider: AiProvider
    configured: bool = True
    created_at: datetime
    updated_at: datetime


class AiCredentialListResponse(ApiSchema):
    items: list[AiCredentialResponse]
