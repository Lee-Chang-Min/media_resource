from datetime import datetime, timedelta, timezone
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from core.auth import verify_password, get_password_hash
from core.db.models import User as UserModel, RefreshToken
from core.db.schemas import UserUpdate

async def auth_user(db: AsyncSession, email: str, password: str):
    """사용자 로그인 함수"""
    result = await db.execute(select(UserModel).where(UserModel.email == email))
    user: UserModel | None = result.scalar_one_or_none()
    
    if not user or not verify_password(password, user.password):
        return None
    
    return user

async def get_user_by_id(db: AsyncSession, user_id: int):
    """사용자 조회"""
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    return result.scalar_one_or_none()

async def get_users_db(db: AsyncSession, company_id: int):
    """사용자 목록 조회"""
    result = await db.execute(select(UserModel).where(UserModel.company_id == company_id))
    return result.scalars().all()

async def update_user_db(
    db: AsyncSession,
    db_user: UserModel,           # id 대신 이미 조회된 User 인스턴스를 받음
    user_in: UserUpdate
) -> UserModel:
    """
    이미 조회된 db_user에 대해서만 name, phone_number, is_admin를 덮어쓰고
    커밋 후 갱신된 User 객체를 반환합니다.
    """
    if user_in.name is not None:
        db_user.name = user_in.name
    if user_in.phoneNumber is not None:
        db_user.phoneNumber = user_in.phoneNumber
    if user_in.is_admin is not None:
        db_user.is_admin = user_in.is_admin


    await db.commit()
    await db.refresh(db_user)
    return db_user

async def delete_user_db(db: AsyncSession, user_id: int):
    """사용자 삭제"""
    result = await db.execute(delete(UserModel).where(UserModel.id == user_id))
    return result.scalar_one_or_none()

async def check_email_exists(db: AsyncSession, email: str, company_id: int):
    """이메일 중복 체크"""
    result = await db.execute(
        select(UserModel).where(
            UserModel.email == email,
            UserModel.company_id == company_id
        )
    )

    return result.scalar_one_or_none() is not None

async def create_user_db(db: AsyncSession, email: str, password: str, company_id: int, is_admin: bool, name: str, phoneNumber: str):
    """사용자 생성"""
    hashed_password = get_password_hash(password)
    db_user = UserModel(
        email=email,
        password=hashed_password,
        company_id=company_id,
        is_admin=is_admin,
        name=name,
        phoneNumber=phoneNumber
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return db_user
