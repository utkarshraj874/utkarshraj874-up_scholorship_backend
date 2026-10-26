from passlib.context import CryptContext
# importing a class from passlib libray
# cryptcontext knows  how to hash password , how to verify passwords
from jose import jwt
from datetime import datetime
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from jose import ExpiredSignatureError
from fastapi import HTTPException
from backend.app.core.config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login"# Creates an OAuth2 authentication scheme , it tells fastapi, that client can obtain a token byb calling "/login"
)
oauth2_scheme_optional = OAuth2PasswordBearer(
    tokenUrl="login",
    auto_error=False
)

pwd_context = CryptContext(
    schemes = ["argon2"],
    deprecated = "auto"# if we later changes scheme = ["bcrypt"] old argon can still be verified ,AND passlib can indicat they should be rhashed
)


def hash_password(password:str)->str:
    return pwd_context.hash(password)#hashes the password

def verify_password(
        plain_password: str,
        hashed_password:str
):
    return pwd_context.verify(
        plain_password,
        hashed_password
    )

def create_acess_token(data:dict):
     to_encode = data.copy()

     expire = datetime.utcnow()+timedelta(
         minutes = ACCESS_TOKEN_EXPIRE_MINUTES
     )

     to_encode.update(
         {"exp":expire}
         )

     encoded_jwt = jwt.encode(
         to_encode,
         SECRET_KEY,
         algorithm = ALGORITHM
     )

     return encoded_jwt

def verify_acess_token(token:str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms = [ALGORITHM]

        )

        return payload
    except ExpiredSignatureError:

        raise HTTPException(
            status_code = 401,
            detail="token has expired"
        )

    except JWTError:

        raise HTTPException(
            status_code=401,
            detail="invalid token"
        )


# Compatibility wrapper for existing imports expecting `get_password_hash`
def get_password_hash(password: str) -> str:
    """Return a hashed password using the configured CryptContext.
    This function mirrors the older name used in other modules.
    """
    return hash_password(password)
