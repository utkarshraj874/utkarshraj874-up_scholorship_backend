from datetime import datetime, date

from sqlalchemy import (
    String,
    ForeignKey,
    Date,
    DateTime,
    Boolean,
    BigInteger,
    Text,
    Numeric,
)

from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.base import Base


class Document(Base):

    __tablename__ = "documents"

    # =========================================================
    # PRIMARY KEY
    # =========================================================

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    # =========================================================
    # USER
    # =========================================================

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    # =========================================================
    # DOCUMENT TYPE
    # =========================================================

    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )

    # =========================================================
    # COMMON CERTIFICATE INFORMATION
    # =========================================================

    document_number: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    issue_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    expiry_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    # =========================================================
    # AADHAAR CARD
    # =========================================================

    aadhaar_number: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    # =========================================================
    # 10th MARKSHEET
    # =========================================================

    tenth_roll_number: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    tenth_board: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    tenth_passing_year: Mapped[int | None] = mapped_column(
        nullable=True
    )

    tenth_percentage: Mapped[float | None] = mapped_column(
        Numeric(5, 2),
        nullable=True
    )

    # =========================================================
    # 12th MARKSHEET
    # =========================================================

    twelfth_roll_number: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    twelfth_board: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    twelfth_passing_year: Mapped[int | None] = mapped_column(
        nullable=True
    )

    twelfth_percentage: Mapped[float | None] = mapped_column(
        Numeric(5, 2),
        nullable=True
    )

    # =========================================================
    # INCOME CERTIFICATE
    # =========================================================

    total_income: Mapped[float | None] = mapped_column(
        Numeric(12, 2),
        nullable=True
    )

    # =========================================================
    # CATEGORY / CASTE CERTIFICATE
    # =========================================================

    certificate_category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    # =========================================================
    # DOMICILE CERTIFICATE
    # =========================================================

    domicile_state: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    # =========================================================
    # BANK PASSBOOK
    # =========================================================

    bank_account_number: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    bank_ifsc: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    bank_name: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    bank_branch: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    # =========================================================
    # RATION CARD
    # =========================================================

    ration_card_number: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    # =========================================================
    # DOCUMENT STATUS & ADMIN REVIEW
    # =========================================================

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="submitted"  # "submitted", "verified", "correction_required"
    )

    admin_remarks: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    verified_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    is_current: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )


    # =========================================================
    # FILE INFORMATION
    # =========================================================

    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    file_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    file_size: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False
    )

    # =========================================================
    # OBJECT STORAGE
    # =========================================================

    file_path: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    storage_provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="supabase"
    )

    # =========================================================
    # TIMESTAMPS
    # =========================================================

    uploaded_at: Mapped[datetime] = mapped_column(
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

    # =========================================================
    # RELATIONSHIP
    # =========================================================

    user = relationship(
        "User",
        back_populates="documents"
    )