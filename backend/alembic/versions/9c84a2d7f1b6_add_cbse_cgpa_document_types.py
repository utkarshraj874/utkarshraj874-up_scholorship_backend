"""Add CGPA marksheet fields and merge existing migration heads.

Revision ID: 9c84a2d7f1b6
Revises: d91e7a3c4b20, add_aadhaar_no_to_profiles
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9c84a2d7f1b6"
down_revision: Union[str, Sequence[str], None] = (
    "d91e7a3c4b20",
    "add_aadhaar_no_to_profiles",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("documents")}
    if "tenth_cgpa" not in columns:
        op.add_column("documents", sa.Column("tenth_cgpa", sa.Numeric(4, 2), nullable=True))
    if "twelfth_cgpa" not in columns:
        op.add_column("documents", sa.Column("twelfth_cgpa", sa.Numeric(4, 2), nullable=True))


def downgrade() -> None:
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("documents")}
    if "twelfth_cgpa" in columns:
        op.drop_column("documents", "twelfth_cgpa")
    if "tenth_cgpa" in columns:
        op.drop_column("documents", "tenth_cgpa")
