import hashlib
import hmac
import logging
import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.app.core.config import SECRET_KEY
from backend.app.core.database import get_db
from backend.app.core.email import send_email
from backend.app.core.security import get_password_hash
from backend.app.models.password_reset import PasswordReset
from backend.app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/password-reset", tags=["Password Reset"])
GENERIC_RESET_RESPONSE = {
    "detail": "If an account exists for that email, password reset instructions will be sent."
}


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., pattern=r"^[0-9]{6}$")
    new_password: str = Field(..., min_length=8, max_length=128)


def generate_otp() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def _hash_otp(email: str, otp: str) -> str:
    message = f"{email.casefold()}:{otp}".encode("utf-8")
    return hmac.new(SECRET_KEY.encode("utf-8"), message, hashlib.sha256).hexdigest()


@router.post("/forgot")
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    now = datetime.utcnow()
    email = str(req.email).casefold()
    user = db.query(User).filter(func.lower(User.email) == email).first()
    if user is None:
        return GENERIC_RESET_RESPONSE

    recent_requests = (
        db.query(PasswordReset)
        .filter(
            PasswordReset.email == email,
            PasswordReset.expires_at >= now + timedelta(minutes=14),
        )
        .count()
    )
    hourly_requests = (
        db.query(PasswordReset)
        .filter(
            PasswordReset.email == email,
            PasswordReset.expires_at >= now - timedelta(minutes=45),
        )
        .count()
    )
    if recent_requests or hourly_requests >= 5:
        return GENERIC_RESET_RESPONSE

    otp = generate_otp()
    reset = PasswordReset(
        email=email,
        otp=_hash_otp(email, otp),
        expires_at=now + timedelta(minutes=15),
        used=False,
    )

    db.query(PasswordReset).filter(
        PasswordReset.email == email,
        PasswordReset.used.is_(False),
    ).update({PasswordReset.used: True}, synchronize_session=False)
    db.add(reset)
    db.commit()

    try:
        send_email(
            to=email,
            subject="Your scholarship portal password reset code",
            body=f"Your password reset code is {otp}. It expires in 15 minutes. "
            "If you did not request this code, you can ignore this email.",
        )
    except RuntimeError:
        logger.exception("Password reset email delivery failed")
        reset.used = True
        db.commit()

    return GENERIC_RESET_RESPONSE


@router.post("/reset")
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    email = str(req.email).casefold()
    now = datetime.utcnow()
    candidate_hash = _hash_otp(email, req.otp)
    reset = (
        db.query(PasswordReset)
        .filter(
            PasswordReset.email == email,
            PasswordReset.used.is_(False),
        )
        .order_by(PasswordReset.expires_at.desc())
        .first()
    )

    if reset is None:
        raise HTTPException(status_code=400, detail="Invalid or expired reset code")

    if reset.expires_at <= now:
        reset.used = True
        db.commit()
        raise HTTPException(status_code=400, detail="Invalid or expired reset code")

    if not hmac.compare_digest(reset.otp, candidate_hash):
        reset.attempts += 1
        if reset.attempts >= 5:
            reset.used = True
        db.commit()
        raise HTTPException(status_code=400, detail="Invalid or expired reset code")

    user = db.query(User).filter(func.lower(User.email) == email).first()
    if user is None:
        reset.used = True
        db.commit()
        raise HTTPException(status_code=400, detail="Invalid or expired reset code")

    user.password = get_password_hash(req.new_password)
    reset.used = True
    db.query(PasswordReset).filter(
        PasswordReset.email == email,
        PasswordReset.id != reset.id,
        PasswordReset.used.is_(False),
    ).update({PasswordReset.used: True}, synchronize_session=False)
    db.commit()
    return {"detail": "Password reset successful"}
