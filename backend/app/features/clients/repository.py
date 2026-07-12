from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.repository_base import BaseRepository
from app.features.clients.models import Client
from app.features.clients.schemas.api import MEXICO_COUNTRY_CODE


class ClientsRepository(BaseRepository[Client]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Client)

    async def get_for_firm(self, *, client_id: int, firm_id: int) -> Client | None:
        result = await self.session.execute(select(Client).where(Client.id == client_id, Client.firm_id == firm_id))
        return result.scalar_one_or_none()

    def _search_filter(self, *, firm_id: int, search: str | None):
        conditions = [Client.firm_id == firm_id]
        if search:
            stripped_search = search.strip()
            digits = "".join(character for character in stripped_search if character in "0123456789")
            if len(digits) == 12 and digits.startswith(MEXICO_COUNTRY_CODE):
                digits = digits[2:]
            name_term = f"%{stripped_search}%"
            phone_term = f"%{digits}%" if digits else name_term
            conditions.append(or_(Client.full_name.ilike(name_term), Client.phone.ilike(phone_term)))
        return conditions

    async def list_for_firm(self, *, firm_id: int, search: str | None, limit: int, offset: int) -> list[Client]:
        query = (
            select(Client)
            .where(*self._search_filter(firm_id=firm_id, search=search))
            .order_by(Client.full_name, Client.id)
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_for_firm(self, *, firm_id: int, search: str | None = None) -> int:
        query = select(func.count(Client.id)).where(*self._search_filter(firm_id=firm_id, search=search))
        return int((await self.session.scalar(query)) or 0)
