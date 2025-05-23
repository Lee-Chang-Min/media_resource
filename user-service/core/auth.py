from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Any, Union, Optional
from jose import jwt
from core.config import settings
from core.db.models import RefreshToken
# from core.db import crud_refresh
from core.db.base import AsyncSession

from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose.exceptions import JWTError

from crud.token import create_refresh_token_db, get_by_refresh_token


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

# JWT Access Token 생성
def create_access_token(
    data: dict, expires_delta: Optional[timedelta]
):
    """
    액세스 토큰 생성
    """
    to_encode = data.copy()
    expire = datetime.now(tz=timezone.utc) + expires_delta
 
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

# JWT Refresh Token 생성
async def create_refresh_token(
    db: AsyncSession,
    user_id: str,
    company_id: str,
    is_admin: bool,
    expires_delta: Optional[timedelta]
) -> str:
    """
    리프레시 토큰 생성
    """

    expire = datetime.now(tz=timezone.utc) + (
        expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    to_encode = {"sub": user_id, "company_id": company_id, "is_admin": is_admin, "exp": expire}

    refresh_token = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    #DB에 저장
    await create_refresh_token_db(
        db = db,
        token = refresh_token,
        user_id = int(user_id),
        expires_delta = expires_delta
    )

    return refresh_token

async def verify_access_token(token: str = Depends(OAuth2PasswordBearer)) -> dict:
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    
    except JWTError as e:
        print(f"JWT 에러 발생: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
        )
    
async def verify_refresh_token(
    db: AsyncSession,
    refresh_token: str
) -> dict:
    try:
        payload = jwt.decode(
            refresh_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
    except (JWTError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or malformed refresh token",
        )

    # DB에 저장된 토큰 객체 조회
    refresh_token_db = await get_by_refresh_token(db, int(payload["sub"]))

    if not refresh_token_db or not refresh_token_db.is_active() or (refresh_token_db.token != refresh_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is revoked or expired",
        )
    return payload

