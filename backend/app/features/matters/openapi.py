from typing import Any

CREATE_MATTER_DOC: dict[str, Any] = {
    "summary": "Create matter",
    "description": "Creates a matter for a client in the authenticated firm.",
}
LIST_MATTERS_DOC: dict[str, Any] = {
    "summary": "List matters",
    "description": "Lists matters in the authenticated firm, optionally filtered by client.",
}
GET_MATTER_DOC: dict[str, Any] = {"summary": "Get matter", "description": "Returns a firm-scoped matter."}
UPDATE_MATTER_DOC: dict[str, Any] = {
    "summary": "Update matter",
    "description": "Partially updates a firm-scoped matter.",
}
