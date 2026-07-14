"""add document text extraction

Revision ID: c5f9a1b3e678
Revises: b4e8f0a2d567
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c5f9a1b3e678"
down_revision: str | None = "b4e8f0a2d567"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "matter_documents",
        sa.Column("text_extraction_status", sa.String(length=32), server_default="unprocessed", nullable=False),
    )
    op.add_column("matter_documents", sa.Column("extracted_text", sa.Text(), nullable=True))
    op.create_check_constraint(
        "ck_matter_documents_text_extraction_status",
        "matter_documents",
        "text_extraction_status IN ('unprocessed', 'not_applicable', 'available', 'empty', 'failed')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_matter_documents_text_extraction_status", "matter_documents", type_="check")
    op.drop_column("matter_documents", "extracted_text")
    op.drop_column("matter_documents", "text_extraction_status")
