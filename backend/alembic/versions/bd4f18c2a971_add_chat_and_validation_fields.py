"""Add chat history tables and profile/reset validation fields.

Revision ID: bd4f18c2a971
Revises: 65bf9c4859c2
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "bd4f18c2a971"
down_revision: Union[str, Sequence[str], None] = "65bf9c4859c2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "profiles" in tables:
        profile_columns = {column["name"] for column in inspector.get_columns("profiles")}
        if "aadhaar_no" not in profile_columns:
            op.add_column("profiles", sa.Column("aadhaar_no", sa.String(length=12), nullable=True))

    if "password_resets" in tables:
        reset_columns = {column["name"]: column for column in inspector.get_columns("password_resets")}
        otp_column = reset_columns.get("otp")
        if otp_column and getattr(otp_column["type"], "length", None) != 64:
            with op.batch_alter_table("password_resets") as batch_op:
                batch_op.alter_column(
                    "otp",
                    existing_type=otp_column["type"],
                    type_=sa.String(length=64),
                    existing_nullable=False,
                )
        if "attempts" not in reset_columns:
            op.add_column(
                "password_resets",
                sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
            )

    if "chat_conversations" not in tables:
        op.create_table(
            "chat_conversations",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=120), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            op.f("ix_chat_conversations_user_id"),
            "chat_conversations",
            ["user_id"],
            unique=False,
        )

    if "chat_messages" not in tables:
        op.create_table(
            "chat_messages",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("conversation_id", sa.Integer(), nullable=False),
            sa.Column("role", sa.String(length=20), nullable=False),
            sa.Column("content", sa.Text(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(
                ["conversation_id"],
                ["chat_conversations.id"],
                ondelete="CASCADE",
            ),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            op.f("ix_chat_messages_conversation_id"),
            "chat_messages",
            ["conversation_id"],
            unique=False,
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "chat_messages" in tables:
        indexes = {index["name"] for index in inspector.get_indexes("chat_messages")}
        if "ix_chat_messages_conversation_id" in indexes:
            op.drop_index("ix_chat_messages_conversation_id", table_name="chat_messages")
        op.drop_table("chat_messages")

    if "chat_conversations" in tables:
        indexes = {index["name"] for index in inspector.get_indexes("chat_conversations")}
        if "ix_chat_conversations_user_id" in indexes:
            op.drop_index("ix_chat_conversations_user_id", table_name="chat_conversations")
        op.drop_table("chat_conversations")

    if "profiles" in tables:
        profile_columns = {column["name"] for column in inspector.get_columns("profiles")}
        if "aadhaar_no" in profile_columns:
            op.drop_column("profiles", "aadhaar_no")

    if "password_resets" in tables:
        reset_columns = {column["name"] for column in inspector.get_columns("password_resets")}
        if "attempts" in reset_columns:
            op.drop_column("password_resets", "attempts")
