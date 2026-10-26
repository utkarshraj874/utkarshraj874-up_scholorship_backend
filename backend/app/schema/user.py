from typing import Literal

from pydantic import BaseModel, ConfigDict

class Usercreate(BaseModel):
    name: str
    email: str
    password: str
    role: Literal["student", "admin"] = "student"
    admin_passkey: str | None = None

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str
    role: str = "student"

class Userlogin(BaseModel):
    email: str
    password: str

