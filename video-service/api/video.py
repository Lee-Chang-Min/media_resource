from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import os
from typing import Optional

from core.db.base import get_db
from core.db.models import Video
from core.db.schemas import VideoCreate, Video
from core.dep import get_current_user
from core.utils.file_utils import save_upload_file
from crud.video import create_video_db

router = APIRouter()

@router.post("/upload", response_model=Video)
async def upload_video(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    video_file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # admin 권한만 접근 가능
):
    try:
        # [1]파일 확장자 검증
        allowed_extensions = [".mp4", ".avi", ".mov", ".mkv", ".wmv"]
        file_ext = os.path.splitext(video_file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"지원하지 않는 파일 형식입니다. 지원 형식: {', '.join(allowed_extensions)}"
            )
        
        # [2] 파일 저장 # return file_path
        file_path = await save_upload_file(video_file)  

        # [3] 비디오 정보 저장
        video = await create_video_db(db, VideoCreate(
            name=name,
            description=description,
            file_path=file_path,
            company_id=current_user["company_id"],
            user_id=current_user["user_id"]
        ))

        return video
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"비디오 업로드 중 오류 발생: {e}"
        )



# @router.delete("/{video_id}", response_model=Video)
# async def delete_video(
#     video_id: int,
#     db: AsyncSession = Depends(get_db),
#     current_user: dict = Depends(get_current_admin_user)  # admin 권한만 접근 가능
# ):
#     async with db as session:
#         result = await session.execute(
#             select(VideoModel).where(
#                 VideoModel.id == video_id,
#                 VideoModel.company_id == current_user["company_id"]
#             )
#         )
#         video = result.scalar_one_or_none()
        
#         if not video:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="비디오를 찾을 수 없습니다"
#             )
        
#         video.is_deleted = True
#         video.deleted_at = datetime.utcnow()
        
#         session.add(video)
#         await session.commit()
#         await session.refresh(video)
        
#         return video

# @router.post("/{video_id}/restore", response_model=Video)
# async def restore_video(
#     video_id: int,
#     db: AsyncSession = Depends(get_db),
#     current_user: dict = Depends(get_current_admin_user),  # admin 권한만 접근 가능
#     is_premium: bool = Depends(is_company_premium)  # 프리미엄 회사 체크
# ):
#     if not is_premium:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="프리미엄 플랜 기업만 비디오 복구 기능을 사용할 수 있습니다"
#         )
    
#     async with db as session:
#         result = await session.execute(
#             select(VideoModel).where(
#                 VideoModel.id == video_id,
#                 VideoModel.company_id == current_user["company_id"],
#                 VideoModel.is_deleted == True
#             )
#         )
#         video = result.scalar_one_or_none()
        
#         if not video:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="삭제된 비디오를 찾을 수 없습니다"
#             )
        
#         video.is_deleted = False
#         video.deleted_at = None
        
#         session.add(video)
#         await session.commit()
#         await session.refresh(video)
        
#         return video
