from typing import Any

from fastapi import status

from app.core.common.openapi import INTERNAL_ERROR_EXAMPLE, build_error_response

GET_DASHBOARD_DOC: dict[str, Any] = {
    "summary": "Get the authenticated firm's dashboard summary",
    "description": "Returns one bounded summary for the firm resolved from the bearer session.",
    "response_description": "Dashboard summary returned.",
    "responses": {
        status.HTTP_401_UNAUTHORIZED: build_error_response(
            description="Missing, expired, or invalid token.",
            example={"detail": "Could not validate credentials", "status": 401, "code": "unauthorized"},
            include_www_authenticate=True,
        ),
        status.HTTP_500_INTERNAL_SERVER_ERROR: build_error_response(
            description="Unhandled internal server error.", example=INTERNAL_ERROR_EXAMPLE
        ),
    },
}
