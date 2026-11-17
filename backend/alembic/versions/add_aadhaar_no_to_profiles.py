"""add_aadhaar_no_to_profiles

Revision ID: add_aadhaar_no_to_profiles
Revises: e546d418c95e
Create Date: 2026-10-26 20:35:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "add_aadhaar_no_to_profiles"
down_revision: Union[str, Sequence[str], None] = "e546d418c95e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Add aadhaar_no column to profiles table."""
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("profiles")}
    if "aadhaar_no" not in columns:
        op.add_column('profiles', sa.Column('aadhaar_no', sa.String(length=12), nullable=True))

def downgrade() -> None:
    """Remove aadhaar_no column from profiles table."""
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("profiles")}
    if "aadhaar_no" in columns:
        op.drop_column('profiles', 'aadhaar_no')
