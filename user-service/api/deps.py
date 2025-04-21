
from fastapi import HTTPException, status, Depends
from core.db.models import User
from core.db.base import get_db
from jose import JWTError, jwt
from core.config import settings

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer
from core.auth import verify_access_token


# def get_admin_user(current_user: User = Depends(get_current_user)):
#     if current_user.role != "admin":
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not enough permissions"
#         )
#     return current_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login")

async def get_current_user(
    access_token: str = Depends(oauth2_scheme),
) -> User:
    """
    1) Authorization 헤더에서 토큰을 꺼내고,
    2) 토큰 유효성을 검증한 뒤,
    3) payload의 'sub' 값을 user_id로 사용해 DB에서 사용자 조회하여 반환합니다.
    """
    try:
        payload = await verify_access_token(access_token)

        user_id: str = payload.get("sub")
        company_id: int = payload.get("company_id")
        is_admin: bool = payload.get("is_admin")

        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user_id"
            )


        # 페이로드에서 직접 User 객체 생성
        user = User(
            id=user_id,
            company_id=company_id,
            is_admin=is_admin
        )
        
        return user
    
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token"
        )

