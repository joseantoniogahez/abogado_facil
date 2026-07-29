from typing import Any

PREVIEW_DOC: dict[str, Any] = {
    "summary": "Preview minimized AI context",
    "description": "Returns the reviewed context metadata and a signed confirmation token bound to the exact inputs.",
}
EXECUTE_DOC: dict[str, Any] = {
    "summary": "Run a controlled matter AI function",
    "responses": {
        400: {
            "description": "The configured provider rejected the request or its credential is invalid.",
        },
        409: {
            "description": "The signed context preview no longer matches the execution inputs.",
        },
        429: {
            "description": "The configured AI provider temporarily reached its request quota.",
            "headers": {
                "Retry-After": {
                    "description": "Seconds clients should wait before retrying.",
                    "schema": {"type": "integer"},
                }
            },
        },
        502: {"description": "The configured AI provider returned an invalid response."},
        503: {"description": "The configured AI provider is temporarily unavailable."},
        504: {"description": "The configured AI provider timed out."},
    },
}
LIST_DOC: dict[str, Any] = {"summary": "List matter AI results"}
REVIEW_DOC: dict[str, Any] = {"summary": "Persist human review of an AI result"}
CONVERT_DOC: dict[str, Any] = {"summary": "Convert an accepted AI result into an explicit action"}
