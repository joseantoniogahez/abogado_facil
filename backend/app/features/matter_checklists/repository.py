from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.repository_base import BaseRepository
from app.features.matter_checklists.models import MatterChecklistItem


class MatterChecklistsRepository(BaseRepository[MatterChecklistItem]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, MatterChecklistItem)

    async def list_for_matter(self, *, matter_id: int, firm_id: int) -> list[MatterChecklistItem]:
        query = (
            select(MatterChecklistItem)
            .where(MatterChecklistItem.matter_id == matter_id, MatterChecklistItem.firm_id == firm_id)
            .order_by(MatterChecklistItem.position, MatterChecklistItem.id)
        )
        return list((await self.session.execute(query)).scalars().all())

    async def get_for_matter(self, *, item_id: int, matter_id: int, firm_id: int) -> MatterChecklistItem | None:
        query = select(MatterChecklistItem).where(
            MatterChecklistItem.id == item_id,
            MatterChecklistItem.matter_id == matter_id,
            MatterChecklistItem.firm_id == firm_id,
        )
        return (await self.session.execute(query)).scalar_one_or_none()

    async def count_for_matter(self, *, matter_id: int, firm_id: int) -> int:
        return int(
            (
                await self.session.scalar(
                    select(func.count(MatterChecklistItem.id)).where(
                        MatterChecklistItem.matter_id == matter_id, MatterChecklistItem.firm_id == firm_id
                    )
                )
            )
            or 0
        )
