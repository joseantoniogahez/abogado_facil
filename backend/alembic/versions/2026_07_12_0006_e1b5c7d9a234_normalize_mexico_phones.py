"""Normalize Mexico client phone storage.

Revision ID: e1b5c7d9a234
Revises: d0a4f6b8c123
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "e1b5c7d9a234"
down_revision: str | None = "d0a4f6b8c123"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("clients", sa.Column("phone_country_code", sa.String(length=3), server_default="52", nullable=False))
    op.execute("UPDATE clients SET phone = regexp_replace(phone, '[^0-9]', '', 'g')")
    op.execute("UPDATE clients SET phone = substring(phone from 3) WHERE length(phone) = 12 AND phone LIKE '52%'")
    op.alter_column(
        "clients", "phone", existing_type=sa.String(length=32), type_=sa.String(length=10), existing_nullable=False
    )
    op.create_check_constraint("ck_clients_mexico_country_code", "clients", "phone_country_code = '52'")
    op.create_check_constraint("ck_clients_phone_length", "clients", "length(phone) = 10")


def downgrade() -> None:
    op.drop_constraint("ck_clients_phone_length", "clients", type_="check")
    op.drop_constraint("ck_clients_mexico_country_code", "clients", type_="check")
    op.alter_column(
        "clients", "phone", existing_type=sa.String(length=10), type_=sa.String(length=32), existing_nullable=False
    )
    op.drop_column("clients", "phone_country_code")
