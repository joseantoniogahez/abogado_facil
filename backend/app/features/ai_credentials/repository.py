from typing import Any, cast

from sqlalchemy import delete, select
from sqlalchemy.engine import CursorResult
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.ai_credentials.models import AiCredential


class AiCredentialsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_for_user(self, *, user_id: int, firm_id: int, provider: str) -> AiCredential | None:
        query = select(AiCredential).where(
            AiCredential.user_id == user_id,
            AiCredential.firm_id == firm_id,
            AiCredential.provider == provider,
        )
        return (await self.session.execute(query)).scalar_one_or_none()

    async def list_for_user(self, *, user_id: int, firm_id: int) -> list[AiCredential]:
        query = select(AiCredential).where(AiCredential.user_id == user_id, AiCredential.firm_id == firm_id)
        return list((await self.session.execute(query)).scalars().all())

    async def create(self, **values) -> AiCredential:
        item = AiCredential(**values)
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def update(self, item: AiCredential, *, encrypted_api_key: str, nonce: str) -> AiCredential:
        item.encrypted_api_key = encrypted_api_key
        item.nonce = nonce
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def delete(self, *, user_id: int, firm_id: int, provider: str) -> bool:
        result = cast(
            CursorResult[Any],
            await self.session.execute(
                delete(AiCredential).where(
                    AiCredential.user_id == user_id,
                    AiCredential.firm_id == firm_id,
                    AiCredential.provider == provider,
                )
            ),
        )
        return bool(result.rowcount)
