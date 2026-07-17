from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.repository_base import BaseRepository
from app.features.matter_payments.models import MatterBilling, MatterPayment


class MatterPaymentsRepository(BaseRepository[MatterPayment]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, MatterPayment)

    async def get_billing(self, *, matter_id: int, firm_id: int) -> MatterBilling | None:
        query = select(MatterBilling).where(MatterBilling.matter_id == matter_id, MatterBilling.firm_id == firm_id)
        return (await self.session.execute(query)).scalar_one_or_none()

    async def upsert_billing(
        self, *, matter_id: int, firm_id: int, agreed_fee: Decimal, notes: str | None
    ) -> MatterBilling:
        billing = await self.get_billing(matter_id=matter_id, firm_id=firm_id)
        if billing is None:
            billing = MatterBilling(matter_id=matter_id, firm_id=firm_id, agreed_fee=agreed_fee, notes=notes)
            self.session.add(billing)
            await self.session.flush()
            await self.session.refresh(billing)
            return billing
        billing.agreed_fee = agreed_fee
        billing.notes = notes
        await self.session.flush()
        await self.session.refresh(billing)
        return billing

    async def list_for_matter(self, *, matter_id: int, firm_id: int) -> list[MatterPayment]:
        query = (
            select(MatterPayment)
            .where(MatterPayment.matter_id == matter_id, MatterPayment.firm_id == firm_id)
            .order_by(MatterPayment.paid_on.desc(), MatterPayment.id.desc())
        )
        return list((await self.session.execute(query)).scalars().all())

    async def total_for_matter(self, *, matter_id: int, firm_id: int) -> Decimal:
        query = select(func.coalesce(func.sum(MatterPayment.amount), 0)).where(
            MatterPayment.matter_id == matter_id, MatterPayment.firm_id == firm_id
        )
        return Decimal(await self.session.scalar(query) or 0).quantize(Decimal("0.01"))
