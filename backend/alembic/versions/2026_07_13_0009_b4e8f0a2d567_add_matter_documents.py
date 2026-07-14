"""add matter documents

Revision ID: b4e8f0a2d567
Revises: a3d7e9f1c456
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b4e8f0a2d567"
down_revision: str | None = "a3d7e9f1c456"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "matter_documents",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("firm_id", sa.Integer(), nullable=False),
        sa.Column("matter_id", sa.Integer(), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("document_type", sa.String(length=32), nullable=False),
        sa.Column("media_type", sa.String(length=100), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("storage_key", sa.String(length=512), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("size_bytes > 0", name="ck_matter_documents_size_positive"),
        sa.ForeignKeyConstraint(["firm_id"], ["firms.id"]),
        sa.ForeignKeyConstraint(["matter_id"], ["matters.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("storage_key"),
    )
    op.create_index("ix_matter_documents_firm_id", "matter_documents", ["firm_id"])
    op.create_index("ix_matter_documents_matter_id", "matter_documents", ["matter_id"])
    op.create_index(
        "ix_matter_documents_firm_matter_created", "matter_documents", ["firm_id", "matter_id", "created_at", "id"]
    )


def downgrade() -> None:
    op.drop_index("ix_matter_documents_firm_matter_created", table_name="matter_documents")
    op.drop_index("ix_matter_documents_matter_id", table_name="matter_documents")
    op.drop_index("ix_matter_documents_firm_id", table_name="matter_documents")
    op.drop_table("matter_documents")
