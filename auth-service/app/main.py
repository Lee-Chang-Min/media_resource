from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from datetime import datetime, timedelta

from app.core.config import settings
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token
from app.schemas import UserCreate, UserUpdate, User, Token
from app.models import Base, User as UserModel, RefreshToken
from app.deps import get_db, get_current_user, get_current_active_user

app = FastAPI(title="Auth Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = create_async_engine(settings.DATABASE_URL)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.post("/login", response_model=Token)
async def login(
    email: str, 
    password: str, 
    db: AsyncSession = Depends(get_db)
):
    async with db as session:
        result = await session.execute(select(UserModel).where(UserModel.email == email))
        user = result.scalar_one_or_none()
        
        if not user or not verify_password(password, user.hashed_password):
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
        
        new_refresh_token = RefreshToken(
            token=refresh_token,
            user_id=user.id,
            expires_at=datetime.utcnow() + refresh_token_expires
        )
        
        session.add(new_refresh_token)
        await session.commit()
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

@app.post("/users", response_model=User)
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
        result = await session.execute(
            select(UserModel).where(
                UserModel.email == user_in.email,
                UserModel.company_id == user_in.company_id
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail="이메일이 이미 사용 중입니다"
            )
        
        hashed_password = get_password_hash(user_in.password)
        db_user = UserModel(
            email=user_in.email,
            hashed_password=hashed_password,
            company_id=user_in.company_id,
            is_admin=user_in.is_admin
        )
        
        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)
        
        return db_user

# 추가적인 엔드포인트 (유저 수정, 삭제 등) 구현... 