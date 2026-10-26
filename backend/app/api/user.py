import hmac

from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session
from fastapi import HTTPException

from backend.app.schema.user import Usercreate, UserResponse
from backend.app.core.config import ADMIN_REGISTRATION_KEY

from backend.app.models.user import User

from backend.app.core.dependencies import get_db, get_current_user
from backend.app.core.security import hash_password, verify_password, create_acess_token

from email_validator import validate_email, EmailNotValidError
from fastapi import Request

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(
    user: Usercreate,
    db: Session = Depends(get_db)
    #  depends(get_db)
    # FastAPI bhai,
    # register function chalane se pehle
    # get_db() execute kar do,
    # aur jo return/yield kare
    # wo db me daal do
):
    if user.role == "admin":
        if not ADMIN_REGISTRATION_KEY:
            raise HTTPException(
                status_code=503,
                detail="Admin registration is not configured. Contact the system administrator.",
            )
        if not user.admin_passkey or not hmac.compare_digest(
            user.admin_passkey,
            ADMIN_REGISTRATION_KEY,
        ):
            raise HTTPException(status_code=403, detail="Invalid admin registration key")

    # ✅ Email validation
    try:
        validate_email(user.email)  # throws EmailNotValidError if invalid
    except EmailNotValidError as e:
        print("❌ Invalid email:", str(e))
        raise HTTPException(status_code=400, detail="Invalid email address")

    # check if user already exists
    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()  # .first() give first matching row or None if not found

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered "
        )

    # create new user object
    user_role = "admin" if user.role == "admin" else "student"
    db_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password),
        role=user_role,
    )

    db.add(db_user) 
    db.commit()  # id is generated here
    db.refresh(db_user)  # it is similar to SQL (SELECT * FROM users WHERE id=?)

    return db_user


@router.post("/login")
async def login(
    request: Request,
    db: Session = Depends(get_db)
):
    content_type = request.headers.get("content-type", "")
    username = None
    password = None

    if "application/json" in content_type:
        try:
            body = await request.json()
            username = body.get("email") or body.get("username")
            password = body.get("password")
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON body")
    else:
        try:
            form_data = await request.form()
            username = form_data.get("username") or form_data.get("email")
            password = form_data.get("password")
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid form data")

    if not username or not password:
        raise HTTPException(
            status_code=400,
            detail="Email/username and password are required"
        )

    db_user = db.query(User).filter(
        User.email == str(username).strip()
    ).first()

    if not db_user or not verify_password(str(password), db_user.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    access_token = create_acess_token(
        data={
            "sub": db_user.email,
            "role": db_user.role,
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": db_user.id,
            "name": db_user.name,
            "email": db_user.email,
            "role": db_user.role,
        }
    }

@router.get("/me")
async def read_me(
    current_user: User = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
    }



