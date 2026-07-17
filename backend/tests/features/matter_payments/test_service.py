from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.features.auth.principal import CurrentPrincipal
from app.features.matter_payments.router import _firm_id
from app.features.matter_payments.schemas.api import CreateMatterPaymentRequest, UpdateMatterBillingRequest


def test_payment_schemas_normalize_optional_notes() -> None:
    billing = UpdateMatterBillingRequest(agreed_fee=Decimal("10.00"), notes="  nota  ")
    payment = CreateMatterPaymentRequest(amount=Decimal("1.25"), payment_type="partial", paid_on="2026-07-16", note=" ")
    assert billing.notes == "nota"
    assert payment.note is None
    with pytest.raises(ValidationError):
        UpdateMatterBillingRequest(agreed_fee=Decimal("1000000000000"), notes=None)
    principal = CurrentPrincipal(
        id=1, email="none@example.com", first_name="N", last_name="O", display_name="N O", disabled=False, firm_id=None
    )
    with pytest.raises(ValueError, match="must belong to a firm"):
        _firm_id(principal)
