from typing import Protocol

from app.core.errors.services import InvalidInputError, NotFoundError
from app.core.security.service.encryption import SecretEncryptionPort
from app.features.ai_credentials.schemas import AiCredentialListResponse, AiCredentialResponse


class AiCredentialsRepositoryPort(Protocol):
    async def get_for_user(self, *, user_id: int, firm_id: int, provider: str): ...
    async def list_for_user(self, *, user_id: int, firm_id: int): ...
    async def create(self, **values): ...
    async def delete(self, *, user_id: int, firm_id: int, provider: str) -> bool: ...


class AiCredentialsService:
    def __init__(self, repository: AiCredentialsRepositoryPort, unit_of_work, encryption: SecretEncryptionPort):
        self.repository = repository
        self.unit_of_work = unit_of_work
        self.encryption = encryption

    @staticmethod
    def _validate_provider(provider: str) -> None:
        if provider not in {"openai", "gemini"}:
            raise InvalidInputError(message="Unsupported AI provider")

    @staticmethod
    def _response(item) -> AiCredentialResponse:
        return AiCredentialResponse(
            provider=item.provider,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )

    async def list(self, *, user_id: int, firm_id: int) -> AiCredentialListResponse:
        return AiCredentialListResponse(
            items=[
                self._response(item) for item in await self.repository.list_for_user(user_id=user_id, firm_id=firm_id)
            ]
        )

    async def save(self, *, user_id: int, firm_id: int, provider: str, api_key: str) -> AiCredentialResponse:
        self._validate_provider(provider)
        encrypted, nonce = self.encryption.encrypt(api_key)
        async with self.unit_of_work:
            item = await self.repository.get_for_user(user_id=user_id, firm_id=firm_id, provider=provider)
            if item is None:
                item = await self.repository.create(
                    user_id=user_id, firm_id=firm_id, provider=provider, encrypted_api_key=encrypted, nonce=nonce
                )
            else:
                item = await self.repository.update(item, encrypted_api_key=encrypted, nonce=nonce)
        return self._response(item)

    async def delete(self, *, user_id: int, firm_id: int, provider: str) -> None:
        self._validate_provider(provider)
        async with self.unit_of_work:
            if not await self.repository.delete(user_id=user_id, firm_id=firm_id, provider=provider):
                raise NotFoundError("AI credential not found")

    async def get_secret(self, *, user_id: int, firm_id: int, provider: str) -> str:
        self._validate_provider(provider)
        item = await self.repository.get_for_user(user_id=user_id, firm_id=firm_id, provider=provider)
        if item is None:
            raise NotFoundError("AI credential not found")
        return self.encryption.decrypt(item.encrypted_api_key, item.nonce)
