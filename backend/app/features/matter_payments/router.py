from fastapi import APIRouter, status

from app.core.authorization.dependencies import AuthenticatedReadAccessDependency
from app.core.setup.dependencies import MatterPaymentsServiceDependency
from app.features.matter_payments.openapi import (
    CREATE_MATTER_PAYMENT_DOC,
    GET_MATTER_PAYMENTS_DOC,
    UPDATE_MATTER_BILLING_DOC,
)
from app.features.matter_payments.schemas.api import (
    CreateMatterPaymentRequest,
    MatterBillingResponse,
    UpdateMatterBillingRequest,
)

router = APIRouter(prefix="/matters/{matter_id}/payments", tags=["matter-payments"])


def _firm_id(user: AuthenticatedReadAccessDependency) -> int:
    if user.firm_id is None:
        raise ValueError("Authenticated matter payment users must belong to a firm")
    return user.firm_id


@router.get("", response_model=MatterBillingResponse, **GET_MATTER_PAYMENTS_DOC)
async def get_matter_payments(
    matter_id: int, user: AuthenticatedReadAccessDependency, service: MatterPaymentsServiceDependency
):
    return await service.get_summary(firm_id=_firm_id(user), matter_id=matter_id)


@router.put("", response_model=MatterBillingResponse, **UPDATE_MATTER_BILLING_DOC)
async def update_matter_billing(
    matter_id: int,
    payload: UpdateMatterBillingRequest,
    user: AuthenticatedReadAccessDependency,
    service: MatterPaymentsServiceDependency,
):
    return await service.update_billing(firm_id=_firm_id(user), matter_id=matter_id, payload=payload)


@router.post("", response_model=MatterBillingResponse, status_code=status.HTTP_201_CREATED, **CREATE_MATTER_PAYMENT_DOC)
async def create_matter_payment(
    matter_id: int,
    payload: CreateMatterPaymentRequest,
    user: AuthenticatedReadAccessDependency,
    service: MatterPaymentsServiceDependency,
):
    return await service.create_payment(firm_id=_firm_id(user), matter_id=matter_id, payload=payload)
