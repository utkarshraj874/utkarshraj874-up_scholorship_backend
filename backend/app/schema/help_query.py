from datetime import datetime
from pydantic import BaseModel, ConfigDict


class HelpQueryCreate(BaseModel):
    subject: str
    message: str


class HelpQueryReply(BaseModel):
    admin_reply: str


class HelpQueryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    student_name: str | None = None
    student_email: str | None = None
    subject: str
    message: str
    status: str
    admin_reply: str | None = None
    replied_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
