from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.orm import relationship
from backend.app.core.base import Base
from sqlalchemy import String
from backend.app.models.documents import Document

# Relationship string ka matlab
# "User" aur "Profile" yaha class names hain, table names nahi.

# SQLAlchemy ORM internally ek mapper registry maintain karta hai.
#  Jab tum apne models define karte ho (jo Base se inherit karte hain), wo registry me register ho jaate hain.

# Is registry ke basis pe SQLAlchemy ko pata hota hai ki "User" 
# string ka matlab hai User class jo users table ko map karta hai, 
# aur "Profile" string ka matlab hai Profile class jo profiles table ko map karta hai.
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(200), nullable=False)
    role: Mapped[str] = mapped_column(String(30), nullable=False, default="student")

    profile = relationship("Profile", back_populates="user", uselist=False)
    documents = relationship(
        "Document",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    notifications = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    help_queries = relationship(
        "HelpQuery",
        back_populates="student",
        cascade="all, delete-orphan"
    )