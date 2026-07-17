import asyncio
from decimal import Decimal

from app.features.matter_payments.repository import MatterPaymentsRepository


def test_payment_repository_empty_queries(mock_database) -> None:
    async def run() -> None:
        async with mock_database.Session() as session:
            repository = MatterPaymentsRepository(session)
            assert await repository.get_billing(matter_id=999, firm_id=999) is None
            assert await repository.list_for_matter(matter_id=999, firm_id=999) == []
            assert await repository.total_for_matter(matter_id=999, firm_id=999) == Decimal("0.00")
            billing = await repository.upsert_billing(matter_id=1, firm_id=1, agreed_fee=Decimal("10.00"), notes=None)
            updated = await repository.upsert_billing(matter_id=1, firm_id=1, agreed_fee=Decimal("20.00"), notes="nota")
            assert updated.id == billing.id
            assert updated.agreed_fee == Decimal("20.00")

    asyncio.run(run())
