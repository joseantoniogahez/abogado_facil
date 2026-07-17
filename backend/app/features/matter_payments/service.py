from decimal import Decimal
from typing import Protocol

from app.core.db.ports import UnitOfWorkPort
from app.core.errors.services import NotFoundError
from app.features.matter_payments.repository import MatterPaymentsRepository
from app.features.matter_payments.schemas.api import (
    CreateMatterPaymentRequest,
    MatterBillingResponse,
    UpdateMatterBillingRequest,
)


class MatterLookupPort(Protocol):
    async def get_for_firm(self, *, matter_id: int, firm_id: int): ...


class MatterPaymentsServicePort(Protocol):
    async def get_summary(self, *, firm_id: int, matter_id: int) -> MatterBillingResponse: ...
    async def update_billing(
        self, *, firm_id: int, matter_id: int, payload: UpdateMatterBillingRequest
    ) -> MatterBillingResponse: ...
    async def create_payment(
        self, *, firm_id: int, matter_id: int, payload: CreateMatterPaymentRequest
    ) -> MatterBillingResponse: ...


class MatterPaymentsService:
    def __init__(
        self, repository: MatterPaymentsRepository, matters_repository: MatterLookupPort, unit_of_work: UnitOfWorkPort
    ):
        self.repository = repository
        self.matters_repository = matters_repository
        self.unit_of_work = unit_of_work

    async def _require_matter(self, *, firm_id: int, matter_id: int) -> None:
        if await self.matters_repository.get_for_firm(matter_id=matter_id, firm_id=firm_id) is None:
            raise NotFoundError("Matter not found")

    async def get_summary(self, *, firm_id: int, matter_id: int) -> MatterBillingResponse:
        await self._require_matter(firm_id=firm_id, matter_id=matter_id)
        billing = await self.repository.get_billing(matter_id=matter_id, firm_id=firm_id)
        payments = await self.repository.list_for_matter(matter_id=matter_id, firm_id=firm_id)
        total = await self.repository.total_for_matter(matter_id=matter_id, firm_id=firm_id)
        fee = billing.agreed_fee if billing else Decimal("0.00")
        return MatterBillingResponse(
            matter_id=matter_id,
            agreed_fee=fee,
            total_paid=total,
            balance=fee - total,
            notes=billing.notes if billing else None,
            payments=payments,
        )

    async def update_billing(
        self, *, firm_id: int, matter_id: int, payload: UpdateMatterBillingRequest
    ) -> MatterBillingResponse:
        async with self.unit_of_work:
            await self._require_matter(firm_id=firm_id, matter_id=matter_id)
            await self.repository.upsert_billing(
                matter_id=matter_id, firm_id=firm_id, agreed_fee=payload.agreed_fee, notes=payload.notes
            )
        return await self.get_summary(firm_id=firm_id, matter_id=matter_id)

    async def create_payment(
        self, *, firm_id: int, matter_id: int, payload: CreateMatterPaymentRequest
    ) -> MatterBillingResponse:
        async with self.unit_of_work:
            await self._require_matter(firm_id=firm_id, matter_id=matter_id)
            await self.repository.create(firm_id=firm_id, matter_id=matter_id, **payload.model_dump())
        return await self.get_summary(firm_id=firm_id, matter_id=matter_id)
