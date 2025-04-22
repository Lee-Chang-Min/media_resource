from sqlalchemy import select, delete, text
from sqlalchemy.ext.asyncio import AsyncSession
from core.auth import verify_password, get_password_hash
from core.db.models import User as UserModel
from core.db.schemas import UserUpdate
from httpx import AsyncClient
from fastapi import HTTPException, status
from core.config import settings

async def auth_user(db: AsyncSession, company_name: str, email: str, password: str):
    """사용자 로그인 함수"""

    # 회사 조회
    async with AsyncClient() as client:
        response = await client.get(f"{settings.COMPANY_SERVICE_URL}/api/v1/?company={company_name}")
        if response.status_code != status.HTTP_200_OK:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"회사 서비스 호출 실패: {response.text}"
            )

        company_id = response.text.strip()
        if company_id == "null":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="회사를 찾을 수 없습니다."
            )
        
    result = await db.execute(select(UserModel).where(UserModel.email == email, UserModel.company_id == int(company_id)))
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


async def award_points_db(db: AsyncSession, user_id: int, points: int):
    """
    사용자에게 포인트를 부여하는 함수.
    """
    try:
        # 락 타임아웃 설정 (50ms)
        await db.execute(text("SET LOCAL lock_timeout = '50ms'"))
        
        # NOWAIT 옵션으로 즉시 락 시도
        result = await db.execute(
            select(UserModel)
            .where(UserModel.id == user_id)
            .with_for_update(nowait=True)
        )
        user = result.scalar_one_or_none()
        if not user:
            return None  # 유저가 없으면 None 반환
        
        # 실제 포인트 누적
        user.point += points
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        return user
    except Exception as e:
        await db.rollback()
        raise e
