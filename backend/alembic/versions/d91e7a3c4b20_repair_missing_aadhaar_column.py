"""Repair profiles missing the optional Aadhaar column.

Revision ID: d91e7a3c4b20
Revises: bd4f18c2a971
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d91e7a3c4b20"
down_revision: Union[str, Sequence[str], None] = "bd4f18c2a971"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "profiles" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("profiles")}
    if "aadhaar_no" not in columns:
        op.add_column(
            "profiles",
            sa.Column("aadhaar_no", sa.String(length=12), nullable=True),
        )


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "profiles" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("profiles")}
    if "aadhaar_no" in columns:
        op.drop_column("profiles", "aadhaar_no")
