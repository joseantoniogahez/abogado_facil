from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.repository_base import BaseRepository
from app.features.matters.models import Matter


class MattersRepository(BaseRepository[Matter]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Matter)

    async def get_for_firm(self, *, matter_id: int, firm_id: int) -> Matter | None:
        return (
            await self.session.execute(select(Matter).where(Matter.id == matter_id, Matter.firm_id == firm_id))
        ).scalar_one_or_none()

    async def list_for_firm(self, *, firm_id: int, client_id: int | None, limit: int, offset: int) -> list[Matter]:
        query = select(Matter).where(Matter.firm_id == firm_id)
        if client_id is not None:
            query = query.where(Matter.client_id == client_id)
        result = await self.session.execute(
            query.order_by(Matter.updated_at.desc(), Matter.id.desc()).offset(offset).limit(limit)
        )
        return list(result.scalars().all())

    async def count_for_firm(self, *, firm_id: int, client_id: int | None = None, status: str | None = None) -> int:
        query = select(func.count(Matter.id)).where(Matter.firm_id == firm_id)
        if client_id is not None:
            query = query.where(Matter.client_id == client_id)
        if status is not None:
            query = query.where(Matter.status == status)
        return int((await self.session.scalar(query)) or 0)
