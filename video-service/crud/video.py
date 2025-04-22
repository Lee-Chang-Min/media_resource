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
        db_video = VideoModel(**video.model_dump())
        db.add(db_video)
        await db.commit()
        await db.refresh(db_video)
        
        return db_video
    except Exception as e:
        await db.rollback()
        raise e



async def get_video(db: AsyncSession, video_id: int) -> Optional[VideoModel]:
    """
    ID로 비디오를 조회합니다.
    
    Args:
        db: 데이터베이스 세션
        video_id: 비디오 ID
        
    Returns:
        비디오 모델 객체 또는 None
    """
    result = await db.execute(
        select(VideoModel).where(
            (VideoModel.id == video_id) & (VideoModel.is_deleted == False)
        )
    )

    # → 첫 번째 요소를 반환.
    # → 조회 결과가 없으면 None 리턴.
    return result.scalars().first()

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


async def delete_video_db(db: AsyncSession, plan: bool, video: VideoModel):
    """
    비디오를 삭제합니다.
    
    Args:
        db: 데이터베이스 세션
        video_id: 비디오 ID
        plan: 플랜 유형 (True: 소프트 삭제, False: 하드 삭제)
        
    Returns:
        삭제 성공 여부
    """
    try:
    
        if plan:
            # 소프트 삭제: is_delete 플래그 설정 및 7일 후 삭제 예정
            print("소프트 삭제")
            from datetime import datetime, timedelta
            video.is_deleted = True
            video.deleted_at = datetime.now() + timedelta(days=7)
            await db.commit()
        else:
            # 하드 삭제: 데이터베이스에서 즉시 삭제 
            # 실제로 Host에 있는 파일도 삭제 해 줘야 함. 
            # 단 무료 플랜에서 유로 플랜이 될때 어떤 비즈니스 로직과 고객의 요구 사항이 있는지에 따라 요구 사항이 변동 될 수 있음
            # 우선 DB 정보만 삭제 하는 것으로 구현현
            print("하드 삭제")
            await db.delete(video)
            await db.commit()
        
        return {"success": True}
        
    except Exception as e:
        await db.rollback()
        raise e

