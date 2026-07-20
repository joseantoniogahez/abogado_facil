from typing import Any

from fastapi import status

HEALTH_DOC: dict[str, Any] = {
    "summary": "Liveness check",
    "description": "Verify that the API process is available without checking dependencies.",
    "response_description": "Current service status.",
    "responses": {
        status.HTTP_200_OK: {
            "description": "Service is available.",
            "content": {"application/json": {"example": {"status": "ok"}}},
        }
    },
}

READINESS_DOC: dict[str, Any] = {
    "summary": "Readiness check",
    "description": "Verify that critical runtime dependencies are available.",
    "response_description": "Dependency readiness status.",
    "responses": {
        status.HTTP_200_OK: {"description": "All critical dependencies are available."},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"description": "One or more critical dependencies are unavailable."},
    },
}
