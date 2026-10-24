from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class DocumentBase(BaseModel):
    """
    Common document details.
    """

    category: str

    document_number: str | None = None
    issue_date: date | None = None
    expiry_date: date | None = None

    aadhaar_number: str | None = None

    tenth_roll_number: str | None = None
    tenth_board: str | None = None
    tenth_passing_year: int | None = None
    tenth_percentage: Decimal | None = None

    twelfth_roll_number: str | None = None
    twelfth_board: str | None = None
    twelfth_passing_year: int | None = None
    twelfth_percentage: Decimal | None = None

    total_income: Decimal | None = None

    certificate_category: str | None = None

    domicile_state: str | None = None

    bank_account_number: str | None = None
    bank_ifsc: str | None = None
    bank_name: str | None = None
    bank_branch: str | None = None

    ration_card_number: str | None = None


class DocumentCreate(DocumentBase):
    """
    Data required while creating a document.
    """

    pass


class DocumentUpdate(BaseModel):
    """
    Data that can be updated in an existing document.
    """

    document_number: str | None = None
    issue_date: date | None = None
    expiry_date: date | None = None

    aadhaar_number: str | None = None

    tenth_roll_number: str | None = None
    tenth_board: str | None = None
    tenth_passing_year: int | None = None
    tenth_percentage: Decimal | None = None

    twelfth_roll_number: str | None = None
    twelfth_board: str | None = None
    twelfth_passing_year: int | None = None
    twelfth_percentage: Decimal | None = None

    total_income: Decimal | None = None

    certificate_category: str | None = None

    domicile_state: str | None = None

    bank_account_number: str | None = None
    bank_ifsc: str | None = None
    bank_name: str | None = None
    bank_branch: str | None = None

    ration_card_number: str | None = None


class DocumentResponse(DocumentBase):
    """
    Document data returned by API.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int

    file_name: str
    file_type: str
    file_size: int
    file_path: str
    storage_provider: str

    status: str = "submitted"
    admin_remarks: str | None = None
    verified_at: datetime | None = None
    file_url: str | None = None

    uploaded_at: datetime
    updated_at: datetime


class DocumentReviewRequest(BaseModel):
    """
    Data payload for admin review / correction suggestion.
    """

    status: str  # "verified", "correction_required", "submitted"
    admin_remarks: str | None = None