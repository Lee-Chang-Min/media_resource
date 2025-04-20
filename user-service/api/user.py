from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from core.config import settings
from core.security import create_access_token, create_refresh_token
from core.db.base import get_db
from core.db.models import User as UserModel
from crud.user import authenticate_user, create_refresh_token_db, check_email_exists, create_user_db
from schemas.token import Token
from schemas.user import User, UserCreate
from dependencies import get_current_active_user

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
    email: str, 
    password: str, 
    db: AsyncSession = Depends(get_db)
):
    async with db as session:
        user = await authenticate_user(session, email, password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="잘못된 이메일 또는 비밀번호입니다",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS)
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        access_token = create_access_token(
            subject=user.id,
            company_id=user.company_id,
            is_admin=user.is_admin,
            expires_delta=access_token_expires
        )
        
        refresh_token = create_refresh_token(
            subject=user.id,
            expires_delta=refresh_token_expires
        )
        
        await create_refresh_token_db(session, refresh_token, user.id, refresh_token_expires)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

@router.post("/users", response_model=User)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다"
        )
    
    async with db as session:
        # 같은 회사 내에서 이메일 중복 체크
        if await check_email_exists(session, user_in.email, user_in.company_id):
            raise HTTPException(
                status_code=400,
                detail="이메일이 이미 사용 중입니다"
            )
        
        db_user = await create_user_db(
            session, 
            user_in.email, 
            user_in.password, 
            user_in.company_id, 
            user_in.is_admin
        )
        
        return db_user

# 추가적인 엔드포인트 (유저 수정, 삭제 등) 구현... 