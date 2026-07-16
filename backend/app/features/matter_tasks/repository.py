from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.repository_base import BaseRepository
from app.features.matter_tasks.models import MatterTask


class MatterTasksRepository(BaseRepository[MatterTask]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, MatterTask)

    async def get_for_matter(self, *, task_id: int, matter_id: int, firm_id: int) -> MatterTask | None:
        query = select(MatterTask).where(
            MatterTask.id == task_id, MatterTask.matter_id == matter_id, MatterTask.firm_id == firm_id
        )
        return (await self.session.execute(query)).scalar_one_or_none()

    async def list_for_matter(self, *, matter_id: int, firm_id: int) -> list[MatterTask]:
        query = (
            select(MatterTask)
            .where(MatterTask.matter_id == matter_id, MatterTask.firm_id == firm_id)
            .order_by(case((MatterTask.completed.is_(False), 0), else_=1), MatterTask.due_date, MatterTask.id)
        )
        return list((await self.session.execute(query)).scalars().all())

    async def count_for_matter(self, *, matter_id: int, firm_id: int) -> int:
        query = select(func.count(MatterTask.id)).where(
            MatterTask.matter_id == matter_id, MatterTask.firm_id == firm_id
        )
        return int((await self.session.scalar(query)) or 0)

    async def count_pending_for_firm(self, *, firm_id: int) -> int:
        query = select(func.count(MatterTask.id)).where(MatterTask.firm_id == firm_id, MatterTask.completed.is_(False))
        return int((await self.session.scalar(query)) or 0)

    async def list_upcoming_for_firm(self, *, firm_id: int, limit: int = 5):
        query = (
            select(MatterTask)
            .where(MatterTask.firm_id == firm_id, MatterTask.completed.is_(False))
            .order_by(MatterTask.due_date, MatterTask.id)
            .limit(limit)
        )
        return list((await self.session.execute(query)).scalars().all())
