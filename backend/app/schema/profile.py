from pydantic import BaseModel, field_validator
import re

class ProfileBase(BaseModel):
    name: str
    registration_no: str
    category: str
    department: str
    semester: int
    phone_no: str
    tenth_percentage: float
    twelfth_percentage: float
    family_income: float
    semester_result: float | None = None
    aadhaar_no: str | None = None

    @field_validator('phone_no')
    @classmethod
    def validate_phone_no(cls, v):
        if not re.fullmatch(r"[0-9]{10}", v):
            raise ValueError('Mobile number must be exactly 10 digits')
        return v

    @field_validator('registration_no')
    @classmethod
    def validate_registration_no(cls, v):
        if not re.fullmatch(r"[0-9]{4}UG[0-9]{4}", v):
            raise ValueError('Registration number must follow format 2024UG1035')
        return v

    @field_validator('aadhaar_no')
    @classmethod
    def validate_aadhaar_no(cls, v):
        if v is None or v == '':
            return v
        if not re.fullmatch(r"[0-9]{12}", v):
            raise ValueError('Aadhaar number must be exactly 12 digits')
        return v

class ProfileCreate(ProfileBase):
    pass

class ProfileUpdate(ProfileBase):
    pass

class ProfileResponse(ProfileBase):
    id: int

    class Config:
        from_attributes = True
