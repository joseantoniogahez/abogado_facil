from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.repository_base import BaseRepository
from app.features.matter_calculations.models import MatterCalculation


class MatterCalculationsRepository(BaseRepository[MatterCalculation]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, MatterCalculation)

    async def list_for_matter(self, *, matter_id: int, firm_id: int):
        query = (
            select(MatterCalculation)
            .where(MatterCalculation.matter_id == matter_id, MatterCalculation.firm_id == firm_id)
            .order_by(MatterCalculation.created_at.desc())
        )
        return list((await self.session.execute(query)).scalars().all())
