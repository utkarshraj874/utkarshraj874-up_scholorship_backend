from datetime import datetime
from sqlalchemy import (
    String,
    ForeignKey,
    DateTime,
    Boolean,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.core.base import Base


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    is_read: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="notifications"
    )
