from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timedelta
import random
import string

from backend.app.core.database import get_db
from sqlalchemy.orm import Session
from backend.app.models.password_reset import PasswordReset
from backend.app.models.user import User
from backend.app.core.security import get_password_hash
from backend.app.core.email import send_email

router = APIRouter(prefix="/password-reset", tags=["Password Reset"])

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=4, max_length=10)
    new_password: str = Field(..., min_length=6)

def generate_otp(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))

@router.post("/forgot")
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User with this email not found")
    otp = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=15)
    pr = PasswordReset(email=req.email, otp=otp, expires_at=expires_at, used=False)
    db.add(pr)
    db.commit()
    # Send email (stub prints to console if SMTP not configured)
    subject = "Your password reset OTP"
    body = f"Your OTP for resetting password is: {otp}. It expires in 15 minutes."
    send_email(to=req.email, subject=subject, body=body)
    return {"detail": "OTP sent to email if it exists"}

@router.post("/reset")
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    pr = db.query(PasswordReset).filter(PasswordReset.email == req.email, PasswordReset.otp == req.otp, PasswordReset.used == False).first()
    if not pr:
        raise HTTPException(status_code=400, detail="Invalid OTP or email")
    if pr.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP has expired")
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.hashed_password = get_password_hash(req.new_password)
    pr.used = True
    db.commit()
    return {"detail": "Password reset successful"}
