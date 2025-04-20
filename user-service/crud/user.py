from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.auth import verify_password, get_password_hash
from core.db.models import User as UserModel, RefreshToken


async def auth_user(db: AsyncSession, email: str, password: str):
    """사용자 로그인 함수"""
    result = await db.execute(select(UserModel).where(UserModel.email == email))
    user: UserModel | None = result.scalar_one_or_none()
    
    if not user or not verify_password(password, user.password):
        return None
    
    return user

async def create_refresh_token_db(db: AsyncSession, token: str, user_id: int, expires_delta: timedelta):
    """리프레시 토큰을 DB에 저장"""
    new_refresh_token = RefreshToken(
        token=token,
        user_id=user_id,
        expires_at=datetime.utcnow() + expires_delta
    )
    
    db.add(new_refresh_token)
    await db.commit()
    return new_refresh_token

async def check_email_exists(db: AsyncSession, email: str, company_id: int):
    """이메일 중복 체크"""
    result = await db.execute(
        select(UserModel).where(
            UserModel.email == email,
            UserModel.company_id == company_id
        )
    )
    return result.scalar_one_or_none() is not None

async def create_user_db(db: AsyncSession, email: str, password: str, company_id: int, is_admin: bool):
    """새 사용자 생성"""
    hashed_password = get_password_hash(password)
    db_user = UserModel(
        email=email,
        hashed_password=hashed_password,
        company_id=company_id,
        is_admin=is_admin
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
