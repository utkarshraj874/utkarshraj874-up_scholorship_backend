from backend.app.core.database import SessionLocal
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.security import oauth2_scheme, oauth2_scheme_optional, verify_acess_token
from backend.app.models.user import User


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    payload = verify_acess_token(token)
    email = payload.get("sub")

    if email is None:
        raise HTTPException(
            status_code=401,
            detail="user not found ",
        )

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="user not found",
        )
    return user


def get_current_user_optional(
    token: str | None = Depends(oauth2_scheme_optional),
    db: Session = Depends(get_db),
) -> User | None:
    if not token:
        return None
    try:
        payload = verify_acess_token(token)
        email = payload.get("sub")
        if not email:
            return None
        return db.query(User).filter(User.email == email).first()
    except Exception:
        return None


def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if getattr(current_user, "role", "student") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Access forbidden: Admin / Scholarship Coordinator privileges required",
        )
    return current_user