from pydantic import BaseModel

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

class ProfileCreate(ProfileBase):
    pass

class ProfileUpdate(ProfileBase):
    pass

class ProfileResponse(ProfileBase):
    id: int

    class Config:
        from_attributes = True
