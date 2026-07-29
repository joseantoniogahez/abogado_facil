from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.repository_base import BaseRepository
from app.features.ai_assistance.models import AIAssistanceResult


class AIAssistanceRepository(BaseRepository[AIAssistanceResult]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, AIAssistanceResult)

    async def get_scoped(self, *, result_id: int, matter_id: int, firm_id: int) -> AIAssistanceResult | None:
        return (
            await self.session.execute(
                select(AIAssistanceResult).where(
                    AIAssistanceResult.id == result_id,
                    AIAssistanceResult.matter_id == matter_id,
                    AIAssistanceResult.firm_id == firm_id,
                )
            )
        ).scalar_one_or_none()

    async def list_scoped(self, *, matter_id: int, firm_id: int) -> list[AIAssistanceResult]:
        query = (
            select(AIAssistanceResult)
            .where(AIAssistanceResult.matter_id == matter_id, AIAssistanceResult.firm_id == firm_id)
            .order_by(AIAssistanceResult.created_at.desc(), AIAssistanceResult.id.desc())
        )
        return list((await self.session.execute(query)).scalars().all())

    async def count_scoped(self, *, matter_id: int, firm_id: int) -> int:
        query = select(func.count(AIAssistanceResult.id)).where(
            AIAssistanceResult.matter_id == matter_id, AIAssistanceResult.firm_id == firm_id
        )
        return int((await self.session.scalar(query)) or 0)

    async def update_result(self, item: AIAssistanceResult, **values: Any) -> AIAssistanceResult:
        for name, value in values.items():
            setattr(item, name, value)
        await self.session.flush()
        await self.session.refresh(item)
        return item
