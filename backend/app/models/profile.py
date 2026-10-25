from sqlalchemy import Column, Integer, String, Float,ForeignKey
from backend.app.core.base import Base
from sqlalchemy.orm import relationship


class Profile(Base):
    __tablename__ = "profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    name = Column(String, nullable=False)
    registration_no = Column(String, unique=True, nullable=False)
    category = Column(String, nullable=False)
    department = Column(String, nullable=False)
    semester = Column(Integer, nullable=False)
    phone_no = Column(String, nullable=False)
    aadhaar_no = Column(String(12), nullable=True)
    tenth_percentage = Column(Float, nullable=False)
    twelfth_percentage = Column(Float, nullable=False)
    family_income = Column(Float, nullable=False)
    semester_result = Column(Float, nullable=True)
    user = relationship("User", back_populates="profile")