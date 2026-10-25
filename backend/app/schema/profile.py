from pydantic import BaseModel, validator
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

    @validator('phone_no')
    def validate_phone_no(cls, v):
        if not re.fullmatch(r"\d{10}", v):
            raise ValueError('Mobile number must be exactly 10 digits')
        return v

    @validator('registration_no')
    def validate_registration_no(cls, v):
        if not re.fullmatch(r"\d{4}UG\d{4}", v):
            raise ValueError('Registration number must follow format YYYYUGNNNN e.g., 2024UG1035')
        return v

    @validator('aadhaar_no')
    def validate_aadhaar_no(cls, v):
        if v is None:
            return v
        if not re.fullmatch(r"\d{12}", v):
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
