"""Build provider adapters only after validating the caller's BYOK credential."""

from collections.abc import Callable
from typing import Protocol

from cryptography.exceptions import InvalidTag

from app.core.errors.services import InvalidInputError, NotFoundError
from app.integrations.ai_providers import AiProviderPort, GeminiProvider, OpenAIProvider


class AiCredentialReader(Protocol):
    async def get_secret(self, *, user_id: int, firm_id: int, provider: str) -> str: ...


ProviderConstructor = Callable[..., AiProviderPort]


class AiProviderFactory:
    """Resolve a real provider only when a scoped, decryptable BYOK key exists."""

    def __init__(self, credentials: AiCredentialReader, constructors: dict[str, ProviderConstructor] | None = None):
        self.credentials = credentials
        self.constructors = constructors or {"openai": OpenAIProvider, "gemini": GeminiProvider}

    async def build(self, *, user_id: int, firm_id: int, provider: str, model: str) -> AiProviderPort:
        constructor = self.constructors.get(provider)
        if constructor is None:
            raise InvalidInputError(message="Unsupported AI provider")
        try:
            api_key = await self.credentials.get_secret(user_id=user_id, firm_id=firm_id, provider=provider)
        except NotFoundError as exc:
            raise InvalidInputError(message="AI provider credential is not configured") from exc
        except (InvalidTag, TypeError, ValueError) as exc:
            raise InvalidInputError(message="AI provider credential is invalid") from exc
        if not api_key.strip():
            raise InvalidInputError(message="AI provider credential is invalid")
        return constructor(api_key=api_key, model=model)
