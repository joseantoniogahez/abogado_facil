from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.repository_base import BaseRepository
from app.features.matter_notes.models import MatterNote


class MatterNotesRepository(BaseRepository[MatterNote]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, MatterNote)

    async def get_for_matter(self, *, note_id: int, matter_id: int, firm_id: int) -> MatterNote | None:
        query = select(MatterNote).where(
            MatterNote.id == note_id, MatterNote.matter_id == matter_id, MatterNote.firm_id == firm_id
        )
        return (await self.session.execute(query)).scalar_one_or_none()

    async def list_for_matter(self, *, matter_id: int, firm_id: int) -> list[MatterNote]:
        query = (
            select(MatterNote)
            .where(MatterNote.matter_id == matter_id, MatterNote.firm_id == firm_id)
            .order_by(MatterNote.created_at.desc(), MatterNote.id.desc())
        )
        return list((await self.session.execute(query)).scalars().all())

    async def count_for_matter(self, *, matter_id: int, firm_id: int) -> int:
        query = select(func.count(MatterNote.id)).where(
            MatterNote.matter_id == matter_id, MatterNote.firm_id == firm_id
        )
        return int((await self.session.scalar(query)) or 0)
