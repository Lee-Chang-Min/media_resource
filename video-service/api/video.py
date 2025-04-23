import os
import httpx
from fastapi.responses import StreamingResponse
import mimetypes
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from core.db.base import get_db
from core.config import settings
from core.db.models import Video
from core.db.schemas import VideoCreate, Video
from core.dep import get_current_user
from core.utils.file_utils import save_upload_file
from crud.video import create_video_db, get_video, delete_video_db

from sqlalchemy import update
from sqlalchemy.ext.asyncio import async_session

router = APIRouter()

#health check
@router.get("/health")
async def health_check():
    return {"status": "ok"}


@router.post("/upload", response_model=Video)
async def upload_video(
    title: str = Form(...),
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
        print(current_user) #{'id': '10', 'company_id': 17, 'is_admin': True}
        print(file_path) #file\video_files\2025\04\20250422082237_01bd0731e64741b6bdd49d8026e62d98.mp4
        video = await create_video_db(db, VideoCreate(
            title=title,
            description=description,
            file_path=file_path,
            company_id=current_user["company_id"],
            user_id=current_user["id"]
        ))

        return video
    
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"비디오 업로드 중 오류 발생: {e}"
        )



@router.delete("/{video_id}")
async def delete_video(
    video_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # admin 권한만 접근 가능
):
    try:
        # [1] 비디오 조회
        video = await get_video(db, video_id)
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="비디오를 찾을 수 없습니다"
            )
        
        # [2] 기업 플랜 확인
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.COMPANY_SERVICE_URL}/v1/premium/{current_user['company_id']}")
            print(response.json())
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="프리미엄 플랜 기업만 비디오 삭제 기능을 사용할 수 있습니다"
                )
        plan = response.json()

        # [3] 비디오 삭제
        result = await delete_video_db(db, plan=plan, video=video)

        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"비디오 삭제 중 오류 발생: {e}"
        )

   

@router.get("/{video_id}/stream", response_class=StreamingResponse)
async def stream_video(
    video_id: int,
    db: AsyncSession = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: dict = Depends(get_current_user)
):
    # [1] 비디오 메타 조회
    video = await get_video(db, video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="비디오를 찾을 수 없습니다"
        )

    # [2] 파일 경로 확인
    file_path = video.file_path
    if not os.path.isfile(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="비디오 파일을 찾을 수 없습니다"
        )

    # [3] MIME 타입 추론 (기본: application/octet-stream)
    media_type, _ = mimetypes.guess_type(file_path)
    media_type = media_type or "application/octet-stream"

    # [4] 로그인된 유저에게 10점 부과 (백그라운드로 처리)
    background_tasks.add_task(award_points, current_user["id"], 10)

    # [5] 청크 단위 파일 스트리밍 제너레이터
    def iterfile():
        with open(file_path, "rb") as file:
            while chunk := file.read(1024 * 1024):  # 1MiB씩
                yield chunk

    return StreamingResponse(iterfile(), media_type=media_type)


async def award_points(user_id: int, points: int):
    """
    Video Service에서 호출할 때 BackgroundTasks로 등록할 포인트 적립 함수.
    User Service의 /points/award 엔드포인트를 호출합니다.
    """
    url = f"{settings.USER_SERVICE_URL}/v1/points"
    params = {"user_id": user_id, "points": points} 

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, params=params)
            if resp.status_code != status.HTTP_200_OK:
                # 실패 시 로깅 또는 재시도 로직 트리거
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"User Service 포인트 적립 실패: {resp.status_code} {resp.text}"
                )
            print(resp.json())
    except httpx.RequestError as e:
        # 네트워크 오류, 타임아웃 등
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"User Service 연결 오류: {e}"
        )