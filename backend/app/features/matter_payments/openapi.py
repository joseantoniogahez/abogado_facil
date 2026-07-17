from typing import Any

GET_MATTER_PAYMENTS_DOC: dict[str, Any] = {
    "summary": "Get matter billing and payments",
    "description": "Returns firm-scoped agreed fees, payment history, paid total and calculated balance.",
}
UPDATE_MATTER_BILLING_DOC: dict[str, Any] = {
    "summary": "Update matter agreed fee and billing notes",
    "description": "Sets the agreed fee and optional financial notes for a firm-scoped matter.",
}
CREATE_MATTER_PAYMENT_DOC: dict[str, Any] = {
    "summary": "Record a matter payment",
    "description": "Records an immutable advance or partial payment for a firm-scoped matter.",
}
