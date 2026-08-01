from typing import Any

LIST_DOCUMENT_TEMPLATES_DOC: dict[str, Any] = {
    "summary": "List simple document templates",
    "description": (
        "Returns the immutable catalog and field definitions available for future draft generation. "
        "This endpoint does not generate, save, send, or file a legal document."
    ),
}
PREVIEW_DOCUMENT_DRAFT_DOC: dict[str, Any] = {
    "summary": "Preview document draft context",
    "description": "Validates template fields and returns the exact BYOK context summary and a signed confirmation token.",
}
GENERATE_DOCUMENT_DRAFT_DOC: dict[str, Any] = {
    "summary": "Generate editable document draft",
    "description": "Generates a schema-validated editable draft after a current signed preview; it never sends or files it.",
}
