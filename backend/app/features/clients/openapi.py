from typing import Any

from fastapi import status

from app.core.common.openapi import INTERNAL_ERROR_EXAMPLE, build_error_response

UNAUTHORIZED = build_error_response(
    description="Missing, expired, or invalid token.",
    example={"detail": "Could not validate credentials", "status": 401, "code": "unauthorized"},
    include_www_authenticate=True,
)
NOT_FOUND = build_error_response(
    description="Client does not exist in the authenticated firm.",
    example={"detail": "Client not found", "status": 404, "code": "not_found"},
)
VALIDATION = build_error_response(
    description="Request validation failed.",
    example={"detail": "Validation error", "status": 422, "code": "invalid_input"},
)
INTERNAL = build_error_response(description="Unhandled internal server error.", example=INTERNAL_ERROR_EXAMPLE)


def _doc(summary: str, description: str, *, include_not_found: bool = False) -> dict[str, Any]:
    responses = {
        status.HTTP_401_UNAUTHORIZED: UNAUTHORIZED,
        status.HTTP_400_BAD_REQUEST: VALIDATION,
        status.HTTP_500_INTERNAL_SERVER_ERROR: INTERNAL,
    }
    if include_not_found:
        responses[status.HTTP_404_NOT_FOUND] = NOT_FOUND
    return {"summary": summary, "description": description, "responses": responses}


CREATE_CLIENT_DOC = _doc("Create a client", "Creates a client in the firm resolved from the bearer session.")
LIST_CLIENTS_DOC = _doc("List clients", "Lists or searches only clients in the authenticated firm.")
GET_CLIENT_DOC = _doc("Get a client", "Gets one client in the authenticated firm.", include_not_found=True)
UPDATE_CLIENT_DOC = _doc(
    "Update a client", "Partially updates one client in the authenticated firm.", include_not_found=True
)
