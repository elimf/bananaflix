from __future__ import annotations

from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from config import ACCESS_TOKEN_EXPIRE_HOUR, SECRET_KEY, ALGORITHM
from common.models.user import User

# Hashing
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# OAuth2 token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (timedelta(hours=ACCESS_TOKEN_EXPIRE_HOUR))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
    except (JWTError, TypeError, ValueError) as e:
        print("Erreur JWT :", e)
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return user
