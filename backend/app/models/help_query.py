from datetime import datetime
from sqlalchemy import (
    String,
    ForeignKey,
    DateTime,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.core.base import Base


class HelpQuery(Base):
    __tablename__ = "help_queries"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    student_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    subject: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="open"  # "open", "resolved"
    )

    admin_reply: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    replied_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    student = relationship(
        "User",
        back_populates="help_queries"
    )
