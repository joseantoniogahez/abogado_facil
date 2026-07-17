import json
from decimal import ROUND_HALF_UP, Decimal

from app.core.errors.services import NotFoundError
from app.features.matter_calculations.schemas.api import MatterCalculationListResponse, MatterCalculationResponse

DISCLAIMER = "Estimación informativa. Revisa los datos y valida el resultado antes de utilizarlo."


class MatterCalculationsService:
    def __init__(self, repository, matters_repository, unit_of_work):
        self.repository, self.matters_repository, self.unit_of_work = repository, matters_repository, unit_of_work

    async def _require(self, firm_id, matter_id):
        if await self.matters_repository.get_for_firm(matter_id=matter_id, firm_id=firm_id) is None:
            raise NotFoundError("Matter not found")

    def _value(self, payload):
        def money(value):
            return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        if payload.calculation_type == "debt_balance":
            amount = max(payload.principal - payload.payments, Decimal(0))
            inputs = {"principal": str(money(payload.principal)), "payments": str(money(payload.payments))}
            summary = f"Adeudo estimado: ${money(amount)} MXN."
        elif payload.calculation_type == "overdue_rent":
            amount = max(payload.monthly_rent * payload.overdue_months - payload.payments, Decimal(0))
            inputs = {
                "monthly_rent": str(money(payload.monthly_rent)),
                "overdue_months": payload.overdue_months,
                "payments": str(money(payload.payments)),
            }
            summary = f"Rentas vencidas estimadas: ${money(amount)} MXN."
        else:
            amount = payload.principal * payload.annual_rate / 100 * Decimal(payload.days) / 365
            inputs = {
                "principal": str(money(payload.principal)),
                "annual_rate": str(payload.annual_rate),
                "days": payload.days,
            }
            summary = f"Interés simple estimado: ${money(amount)} MXN (base anual de 365 días)."
        return inputs, money(amount), summary

    async def calculate(self, firm_id, matter_id, payload):
        await self._require(firm_id, matter_id)
        inputs, amount, summary = self._value(payload)
        return MatterCalculationResponse(
            matter_id=matter_id,
            calculation_type=payload.calculation_type,
            inputs=inputs,
            result_amount=amount,
            summary=summary,
            disclaimer=DISCLAIMER,
        )

    async def save(self, firm_id, matter_id, payload):
        async with self.unit_of_work:
            await self._require(firm_id, matter_id)
            inputs, amount, summary = self._value(payload)
            item = await self.repository.create(
                firm_id=firm_id,
                matter_id=matter_id,
                calculation_type=payload.calculation_type,
                inputs_json=json.dumps(inputs),
                result_amount=amount,
                summary=summary,
                disclaimer=DISCLAIMER,
            )
        return MatterCalculationResponse(
            id=item.id,
            matter_id=matter_id,
            calculation_type=payload.calculation_type,
            inputs=inputs,
            result_amount=amount,
            summary=summary,
            disclaimer=DISCLAIMER,
            created_at=item.created_at,
        )

    async def list_saved(self, firm_id, matter_id):
        await self._require(firm_id, matter_id)
        items = await self.repository.list_for_matter(matter_id=matter_id, firm_id=firm_id)
        return MatterCalculationListResponse(
            items=[
                MatterCalculationResponse(
                    id=x.id,
                    matter_id=x.matter_id,
                    calculation_type=x.calculation_type,
                    inputs=json.loads(x.inputs_json),
                    result_amount=x.result_amount,
                    summary=x.summary,
                    disclaimer=x.disclaimer,
                    created_at=x.created_at,
                )
                for x in items
            ]
        )
