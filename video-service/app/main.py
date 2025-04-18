from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from datetime import datetime
import httpx

from app.core.config import settings
from app.schemas import VideoCreate, VideoUpdate, Video
from app.models import Base, Video as VideoModel
from app.deps import get_db, get_current_user, get_current_admin_user, is_company_premium

app = FastAPI(title="Video Service")

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

@app.post("/", response_model=Video)
async def create_video(
    video_in: VideoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)  # admin 권한만 접근 가능
):
    async with db as session:
        db_video = VideoModel(
            title=video_in.title,
            description=video_in.description,
            url=video_in.url,
            company_id=current_user["company_id"],
            created_by=current_user["id"]
        )
        
        session.add(db_video)
        await session.commit()
        await session.refresh(db_video)
        
        return db_video

@app.delete("/{video_id}", response_model=Video)
async def delete_video(
    video_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)  # admin 권한만 접근 가능
):
    async with db as session:
        result = await session.execute(
            select(VideoModel).where(
                VideoModel.id == video_id,
                VideoModel.company_id == current_user["company_id"]
            )
        )
        video = result.scalar_one_or_none()
        
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="비디오를 찾을 수 없습니다"
            )
        
        video.is_deleted = True
        video.deleted_at = datetime.utcnow()
        
        session.add(video)
        await session.commit()
        await session.refresh(video)
        
        return video

@app.post("/{video_id}/restore", response_model=Video)
async def restore_video(
    video_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user),  # admin 권한만 접근 가능
    is_premium: bool = Depends(is_company_premium)  # 프리미엄 회사 체크
):
    if not is_premium:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="프리미엄 플랜 기업만 비디오 복구 기능을 사용할 수 있습니다"
        )
    
    async with db as session:
        result = await session.execute(
            select(VideoModel).where(
                VideoModel.id == video_id,
                VideoModel.company_id == current_user["company_id"],
                VideoModel.is_deleted == True
            )
        )
        video = result.scalar_one_or_none()
        
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="삭제된 비디오를 찾을 수 없습니다"
            )
        
        video.is_deleted = False
        video.deleted_at = None
        
        session.add(video)
        await session.commit()
        await session.refresh(video)
        
        return video

# 추가적인 엔드포인트 (비디오 조회, 수정 등) 구현... 