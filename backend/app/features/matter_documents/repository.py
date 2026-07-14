from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.repository_base import BaseRepository
from app.features.matter_documents.models import MatterDocument


class MatterDocumentsRepository(BaseRepository[MatterDocument]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, MatterDocument)

    async def lock_quota(self, *, firm_id: int, matter_id: int) -> None:
        bind = self.session.get_bind()
        if bind.dialect.name == "postgresql":
            lock_key = (firm_id << 32) | matter_id
            await self.session.execute(text("SELECT pg_advisory_xact_lock(:lock_key)"), {"lock_key": lock_key})

    async def get_for_matter(self, *, document_id: str, matter_id: int, firm_id: int) -> MatterDocument | None:
        query = select(MatterDocument).where(
            MatterDocument.id == document_id,
            MatterDocument.matter_id == matter_id,
            MatterDocument.firm_id == firm_id,
        )
        return (await self.session.execute(query)).scalar_one_or_none()

    async def list_for_matter(self, *, matter_id: int, firm_id: int) -> list[MatterDocument]:
        query = (
            select(MatterDocument)
            .where(MatterDocument.matter_id == matter_id, MatterDocument.firm_id == firm_id)
            .order_by(MatterDocument.created_at.desc(), MatterDocument.id.desc())
        )
        return list((await self.session.execute(query)).scalars().all())

    async def count_for_matter(self, *, matter_id: int, firm_id: int) -> int:
        query = select(func.count(MatterDocument.id)).where(
            MatterDocument.matter_id == matter_id, MatterDocument.firm_id == firm_id
        )
        return int((await self.session.scalar(query)) or 0)
