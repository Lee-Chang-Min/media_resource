from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Any, Union, Optional
from jose import jwt
from core.config import settings
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose.exceptions import JWTError


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 비밀번호 검증
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    일반 비밀번호와 해시된 비밀번호를 비교합니다.
    """
    return pwd_context.verify(plain_password, hashed_password)

# 비밀번호 해싱
def get_password_hash(password: str) -> str:
    """
    비밀번호를 해시화 합니다.
    """
    return pwd_context.hash(password) 

def create_access_token(
    data: dict, expires_delta: Optional[timedelta] = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_DAYS)
):
    """
    액세스 토큰 생성
    """
    to_encode = data.copy()
    expire = datetime.now(tz=timezone.utc) + expires_delta
 
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    user_id: int,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    리프레시 토큰 생성
    """
    to_encode = {"sub": str(user_id)}
    expire = datetime.now(tz=timezone.utc) + (
        expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


async def verify_access_token(token: str = Depends(OAuth2PasswordBearer)) -> dict:
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
        )