from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional, Dict, Any

from core.db.models import Video as VideoModel
from core.db.schemas import VideoCreate, Video

async def create_video_db(db: AsyncSession, video: VideoCreate) -> Video:
    """
    비디오 정보를 데이터베이스에 생성합니다.
    
    Args:
        db: 데이터베이스 세션
        video: 비디오 데이터 (title, description, url 등)
        
    Returns:
        생성된 비디오 모델 객체
    """

    try:
        db_video = VideoModel(
            **video.model_dump(),
            company_id=video.company_id,
            user_id=video.user_id
        )
        
        db.add(db_video)
        await db.commit()
        await db.refresh(db_video)
        
        return db_video
    except Exception as e:
        await db.rollback()
        raise e



# async def get_video(db: AsyncSession, video_id: int) -> Optional[VideoModel]:
#     """
#     ID로 비디오를 조회합니다.
    
#     Args:
#         db: 데이터베이스 세션
#         video_id: 비디오 ID
        
#     Returns:
#         비디오 모델 객체 또는 None
#     """
#     result = await db.execute(select(VideoModel).where(VideoModel.id == video_id))
#     return result.scalars().first()

# async def get_videos(
#     db: AsyncSession, 
#     skip: int = 0, 
#     limit: int = 100,
#     company_id: Optional[int] = None
# ) -> List[VideoModel]:
#     """
#     비디오 목록을 조회합니다.
    
#     Args:
#         db: 데이터베이스 세션
#         skip: 건너뛸 레코드 수
#         limit: 최대 반환 레코드 수
#         company_id: 회사 ID로 필터링 (선택 사항)
        
#     Returns:
#         비디오 모델 객체 리스트
#     """
#     query = select(VideoModel).offset(skip).limit(limit)
    
#     if company_id is not None:
#         query = query.where(VideoModel.company_id == company_id)
    
#     result = await db.execute(query)
#     return result.scalars().all()

# async def update_video(
#     db: AsyncSession, 
#     video_id: int, 
#     video_update: VideoUpdate
# ) -> Optional[VideoModel]:
#     """
#     비디오 정보를 업데이트합니다.
    
#     Args:
#         db: 데이터베이스 세션
#         video_id: 비디오 ID
#         video_update: 업데이트할 비디오 데이터
        
#     Returns:
#         업데이트된 비디오 모델 객체 또는 None
#     """
#     video = await get_video(db, video_id)
#     if not video:
#         return None
    
#     update_data = video_update.dict(exclude_unset=True)
#     for field, value in update_data.items():
#         setattr(video, field, value)
    
#     await db.commit()
#     await db.refresh(video)
#     return video

# async def delete_video(db: AsyncSession, video_id: int) -> bool:
#     """
#     비디오를 삭제합니다.
    
#     Args:
#         db: 데이터베이스 세션
#         video_id: 비디오 ID
        
#     Returns:
#         삭제 성공 여부
#     """
#     video = await get_video(db, video_id)
#     if not video:
#         return False
    
#     await db.delete(video)
#     await db.commit()
#     return True
